from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, Interval
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class MonitoredSite(Base):
    __tablename__ = "monitored_sites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    url = Column(String, nullable=False)
    site_type = Column(String, default="general")  # 如: news, forum, blog 等
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))

class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, index=True, nullable=False)
    category = Column(String, default="general")
    priority = Column(Integer, default=1)  # 1-5, 5为最高优先级
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))

class CrawlTask(Base):
    __tablename__ = "crawl_tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    frequency = Column(Interval, nullable=False)  # 爬取频率
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))

class CrawlResult(Base):
    __tablename__ = "crawl_results"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    content = Column(Text)
    summary = Column(String)
    published_at = Column(DateTime)
    crawled_at = Column(DateTime, default=func.now())
    keyword_matched = Column(String, index=True)
    site_id = Column(Integer, ForeignKey("monitored_sites.id"))
    task_id = Column(Integer, ForeignKey("crawl_tasks.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

class TaskSite(Base):
    __tablename__ = "task_sites"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("crawl_tasks.id"), nullable=False)
    site_id = Column(Integer, ForeignKey("monitored_sites.id"), nullable=False)

class TaskKeyword(Base):
    __tablename__ = "task_keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("crawl_tasks.id"), nullable=False)
    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=False)