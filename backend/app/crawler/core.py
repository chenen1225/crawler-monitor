import asyncio
import aiohttp
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse
import re
from bs4 import BeautifulSoup
import requests
from sqlalchemy.orm import Session
import os

from app.models import CrawlResult, MonitoredSite, Keyword, CrawlTask, TaskSite, TaskKeyword
from app.database import get_db
from app.utils.text_summarizer import summarizer
from app.utils.excel_exporter import ExcelExporter

class Crawler:
    def __init__(self, db: Session):
        self.db = db
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    async def crawl_task(self, task_id: int):
        """
        执行一个爬虫任务
        """
        task = self.db.query(CrawlTask).filter(CrawlTask.id == task_id).first()
        if not task:
            print(f"Task {task_id} not found")
            return

        # 获取任务关联的网站和关键词
        site_ids = [ts.site_id for ts in self.db.query(TaskSite).filter(TaskSite.task_id == task_id).all()]
        keyword_ids = [tk.keyword_id for tk in self.db.query(TaskKeyword).filter(TaskKeyword.task_id == task_id).all()]
        
        sites = self.db.query(MonitoredSite).filter(MonitoredSite.id.in_(site_ids)).all()
        keywords = self.db.query(Keyword).filter(Keyword.id.in_(keyword_ids)).all()
        
        all_results = []
        for site in sites:
            for keyword in keywords:
                results = self.crawl_site_for_keyword(site, keyword)
                
                # 为每个结果生成摘要
                for result in results:
                    if result['content']:
                        result['summary'] = summarizer.summarize_text(result['content'])
                    else:
                        result['summary'] = summarizer.summarize_text(result['title'])
                
                all_results.extend(results)
        
        # 保存结果到数据库
        for result in all_results:
            crawl_result = CrawlResult(
                title=result['title'],
                url=result['url'],
                content=result['content'],
                summary=result.get('summary', ''),
                published_at=result.get('published_at'),
                keyword_matched=result['keyword_matched'],
                site_id=result['site_id'],
                task_id=task_id,  # 修复：使用传入的task_id
                user_id=result['user_id']
            )
            self.db.add(crawl_result)
        
        self.db.commit()
        
        # 更新任务的最后运行时间
        task.last_run = datetime.utcnow()
        self.db.commit()
        
        # 将结果保存到Excel文件
        if all_results:
            keyword_str = "_".join([kw.keyword for kw in keywords[:3]])  # 使用前3个关键词作为文件名标识
            self.save_results_to_excel(all_results, keyword=keyword_str)
        
        return all_results

    def crawl_site_for_keyword(self, site: MonitoredSite, keyword: Keyword) -> List[Dict[str, Any]]:
        """
        在指定网站搜索关键词并返回结果
        """
        results = []
        try:
            response = self.session.get(site.url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找包含关键词的内容（简化版，实际可能需要更复杂的逻辑）
            elements = soup.find_all(string=re.compile(keyword.keyword, re.IGNORECASE))
            
            for element in elements:
                # 找到包含关键词的元素的父级链接
                parent_link = element.parent.find_parent('a', href=True)
                
                if parent_link:
                    link_url = urljoin(site.url, parent_link['href'])
                    
                    # 获取页面详情
                    try:
                        detail_response = self.session.get(link_url, timeout=10)
                        detail_response.raise_for_status()
                        
                        detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
                        
                        # 尝试提取标题
                        title_elem = detail_soup.find(['h1', 'h2', 'h3', 'title'])
                        title = title_elem.get_text().strip() if title_elem else 'Untitled'
                        
                        # 尝试提取发布日期（简化处理）
                        date_elem = detail_soup.find(['time', 'span'], class_=re.compile(r'date|time|published', re.IGNORECASE))
                        published_at = None
                        if date_elem:
                            date_text = date_elem.get_text().strip()
                            # 这里可以添加日期解析逻辑
                            try:
                                published_at = datetime.fromisoformat(date_text.replace('Z', '+00:00'))
                            except:
                                published_at = datetime.utcnow()
                        
                        # 提取全文内容
                        content_elem = detail_soup.find('body')
                        content = content_elem.get_text().strip() if content_elem else ''
                        
                        # 创建结果对象
                        result = {
                            'title': title,
                            'url': link_url,
                            'content': content[:5000],  # 限制内容长度
                            'published_at': published_at,
                            'keyword_matched': keyword.keyword,
                            'site_id': site.id,
                            'task_id': 0,  # 将在保存时设置
                            'user_id': site.user_id
                        }
                        
                        results.append(result)
                        
                        # 为了简单起见，我们只获取第一个匹配项
                        # 在实际应用中，你可能需要遍历更多元素
                        break
                        
                    except Exception as e:
                        print(f"Error crawling link {link_url}: {str(e)}")
                        continue
                        
        except Exception as e:
            print(f"Error crawling site {site.url}: {str(e)}")
        
        return results

    def save_results_to_excel(self, results: List[Dict[str, Any]], filename: str = None, keyword: str = None):
        """
        将爬取结果保存到Excel文件
        """
        if not results:
            print("No results to save")
            return
        
        exporter = ExcelExporter(output_dir="exports")
        try:
            filepath = exporter.export_crawl_results(results, filename, keyword)
            print(f"Saved {len(results)} results to {filepath}")
            return filepath
        except Exception as e:
            print(f"Error saving results to Excel: {str(e)}")
            return None

# 任务调度器
class TaskScheduler:
    def __init__(self):
        self.running_tasks = set()
    
    async def run_scheduled_tasks(self):
        """
        运行所有计划任务
        """
        # 这里可以定期查询数据库中需要运行的任务
        # 并执行它们
        db_gen = get_db()
        db = next(db_gen)
        
        # 获取所有激活的、需要运行的任务
        active_tasks = db.query(CrawlTask).filter(
            CrawlTask.is_active == True
        ).all()
        
        for task in active_tasks:
            # 检查是否需要运行
            if self.should_run_task(task):
                await self.execute_task(task.id)
        
        db.close()
    
    def should_run_task(self, task: CrawlTask) -> bool:
        """
        判断任务是否应该运行
        """
        if not task.next_run:
            return True
            
        return datetime.utcnow() >= task.next_run
    
    async def execute_task(self, task_id: int):
        """
        执行指定的任务
        """
        if task_id in self.running_tasks:
            print(f"Task {task_id} is already running")
            return
            
        self.running_tasks.add(task_id)
        
        try:
            db_gen = get_db()
            db = next(db_gen)
            
            crawler = Crawler(db)
            await crawler.crawl_task(task_id)
            
            db.close()
        except Exception as e:
            print(f"Error executing task {task_id}: {str(e)}")
        finally:
            self.running_tasks.discard(task_id)