from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# User schemas
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# MonitoredSite schemas
class MonitoredSiteBase(BaseModel):
    name: str
    url: str
    site_type: Optional[str] = "general"
    is_active: Optional[bool] = True

class MonitoredSiteCreate(MonitoredSiteBase):
    pass

class MonitoredSiteUpdate(MonitoredSiteBase):
    name: Optional[str] = None
    url: Optional[str] = None
    site_type: Optional[str] = None
    is_active: Optional[bool] = None

class MonitoredSiteResponse(MonitoredSiteBase):
    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int

    class Config:
        from_attributes = True

# Keyword schemas
class KeywordBase(BaseModel):
    keyword: str
    category: Optional[str] = "general"
    priority: Optional[int] = 1
    is_active: Optional[bool] = True

class KeywordCreate(KeywordBase):
    pass

class KeywordUpdate(KeywordBase):
    keyword: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None

class KeywordResponse(KeywordBase):
    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int

    class Config:
        from_attributes = True

# CrawlTask schemas
class CrawlTaskBase(BaseModel):
    name: str
    description: Optional[str] = None
    frequency: str  # 使用ISO 8601时间间隔格式，如 "PT1H" 表示1小时
    is_active: Optional[bool] = True

class CrawlTaskCreate(CrawlTaskBase):
    site_ids: List[int]
    keyword_ids: List[int]

class CrawlTaskUpdate(CrawlTaskBase):
    name: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[str] = None
    is_active: Optional[bool] = None
    site_ids: Optional[List[int]] = None
    keyword_ids: Optional[List[int]] = None

class CrawlTaskResponse(CrawlTaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    user_id: int

    class Config:
        from_attributes = True

# CrawlResult schemas
class CrawlResultBase(BaseModel):
    title: str
    url: str
    content: Optional[str] = None
    summary: Optional[str] = None
    published_at: Optional[datetime] = None
    keyword_matched: str
    site_id: int
    task_id: int

class CrawlResultCreate(CrawlResultBase):
    pass

class CrawlResultUpdate(BaseModel):
    summary: Optional[str] = None

class CrawlResultResponse(CrawlResultBase):
    id: int
    crawled_at: datetime
    user_id: int

    class Config:
        from_attributes = True