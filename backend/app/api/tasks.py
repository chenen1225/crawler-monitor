from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import schemas, models
from app.utils import get_current_user

router = APIRouter()

@router.get("/", response_model=List[schemas.CrawlTaskResponse])
def get_tasks(
    skip: int = 0, 
    limit: int = 100, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tasks = db.query(models.CrawlTask).filter(
        models.CrawlTask.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return tasks

@router.post("/", response_model=schemas.CrawlTaskResponse)
def create_task(
    task: schemas.CrawlTaskCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 创建任务
    task_data = task.dict(exclude={'site_ids', 'keyword_ids'})
    db_task = models.CrawlTask(**task_data, user_id=current_user.id)
    db.add(db_task)
    db.flush()  # 获取任务ID但不提交事务

    # 创建任务与网站的关联
    for site_id in task.site_ids:
        task_site = models.TaskSite(task_id=db_task.id, site_id=site_id)
        db.add(task_site)

    # 创建任务与关键词的关联
    for keyword_id in task.keyword_ids:
        task_keyword = models.TaskKeyword(task_id=db_task.id, keyword_id=keyword_id)
        db.add(task_keyword)

    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/{task_id}", response_model=schemas.CrawlTaskResponse)
def get_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(models.CrawlTask).filter(
        models.CrawlTask.id == task_id,
        models.CrawlTask.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=schemas.CrawlTaskResponse)
def update_task(
    task_id: int,
    task: schemas.CrawlTaskUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_task = db.query(models.CrawlTask).filter(
        models.CrawlTask.id == task_id,
        models.CrawlTask.user_id == current_user.id
    ).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # 更新任务基本信息
    update_data = task.dict(exclude={'site_ids', 'keyword_ids'}, exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    # 如果提供了新的site_ids，先删除旧关联，再创建新关联
    if task.site_ids is not None:
        # 删除旧关联
        db.query(models.TaskSite).filter(models.TaskSite.task_id == task_id).delete()
        # 创建新关联
        for site_id in task.site_ids:
            task_site = models.TaskSite(task_id=task_id, site_id=site_id)
            db.add(task_site)
    
    # 如果提供了新的keyword_ids，先删除旧关联，再创建新关联
    if task.keyword_ids is not None:
        # 删除旧关联
        db.query(models.TaskKeyword).filter(models.TaskKeyword.task_id == task_id).delete()
        # 创建新关联
        for keyword_id in task.keyword_ids:
            task_keyword = models.TaskKeyword(task_id=task_id, keyword_id=keyword_id)
            db.add(task_keyword)

    db.commit()
    db.refresh(db_task)
    return db_task

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(models.CrawlTask).filter(
        models.CrawlTask.id == task_id,
        models.CrawlTask.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # 删除关联表记录
    db.query(models.TaskSite).filter(models.TaskSite.task_id == task_id).delete()
    db.query(models.TaskKeyword).filter(models.TaskKeyword.task_id == task_id).delete()
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}