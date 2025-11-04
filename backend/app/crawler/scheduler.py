import asyncio
import threading
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CrawlTask
from app.crawler.core import Crawler

class TaskSchedulerService:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.is_running = False

    def start_scheduler(self):
        """启动调度器，定期检查需要运行的任务"""
        self.scheduler.add_job(
            func=self._check_and_run_tasks,
            trigger=IntervalTrigger(seconds=30),  # 每30秒检查一次
            id='task_checker',
            name='Check and run crawl tasks',
            replace_existing=True
        )
        self.is_running = True
        print("Task scheduler started")

    def stop_scheduler(self):
        """停止调度器"""
        self.scheduler.shutdown()
        self.is_running = False
        print("Task scheduler stopped")

    def _check_and_run_tasks(self):
        """检查并运行需要执行的任务"""
        print(f"Checking tasks at {datetime.now()}")
        
        # 获取数据库会话
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            # 获取所有激活的、需要运行的任务
            active_tasks = db.query(CrawlTask).filter(
                CrawlTask.is_active == True
            ).all()
            
            crawler = Crawler(db)
            
            for task in active_tasks:
                if self._should_run_task(task):
                    print(f"Running task: {task.name} (ID: {task.id})")
                    # 这里我们使用同步方式调用，因为APScheduler不直接支持async
                    asyncio.run(crawler.crawl_task(task.id))
                    
                    # 更新任务的下次运行时间
                    self._update_next_run_time(db, task)
        except Exception as e:
            print(f"Error in task scheduler: {str(e)}")
        finally:
            db.close()

    def _should_run_task(self, task: CrawlTask) -> bool:
        """判断任务是否应该运行"""
        if not task.next_run:
            return True
        return datetime.utcnow() >= task.next_run

    def _update_next_run_time(self, db: Session, task: CrawlTask):
        """更新任务的下次运行时间"""
        # 解析任务的频率设置并更新下次运行时间
        # 这里简化处理，假设频率是以秒为单位的字符串
        import isodate
        try:
            # 使用ISO 8601格式解析间隔
            interval = isodate.parse_duration(task.frequency)
            task.next_run = datetime.utcnow() + interval
        except:
            # 如果解析失败，使用默认值（1小时）
            task.next_run = datetime.utcnow() + timedelta(hours=1)
        
        db.commit()

    def add_task_to_schedule(self, task_id: int, interval_seconds: int):
        """将特定任务添加到调度中"""
        job_id = f'crawl_task_{task_id}'
        
        # 移除可能已存在的相同任务
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
        
        # 添加新任务
        self.scheduler.add_job(
            func=self._run_specific_task,
            trigger=IntervalTrigger(seconds=interval_seconds),
            id=job_id,
            name=f'Crawl task {task_id}',
            args=[task_id],
            replace_existing=True
        )
        print(f"Task {task_id} added to scheduler with {interval_seconds}s interval")

    def _run_specific_task(self, task_id: int):
        """运行特定任务"""
        print(f"Running specific task {task_id}")
        
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            crawler = Crawler(db)
            asyncio.run(crawler.crawl_task(task_id))
        except Exception as e:
            print(f"Error running task {task_id}: {str(e)}")
        finally:
            db.close()

# 全局调度器实例
scheduler_service = TaskSchedulerService()