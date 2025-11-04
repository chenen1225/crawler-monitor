from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import schemas, models
from app.utils import get_current_user

router = APIRouter()

@router.get("/", response_model=List[schemas.CrawlResultResponse])
def get_results(
    skip: int = 0, 
    limit: int = 100, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    results = db.query(models.CrawlResult).filter(
        models.CrawlResult.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return results

@router.get("/task/{task_id}", response_model=List[schemas.CrawlResultResponse])
def get_results_by_task(
    task_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    results = db.query(models.CrawlResult).filter(
        models.CrawlResult.task_id == task_id,
        models.CrawlResult.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return results

@router.get("/keyword/{keyword}", response_model=List[schemas.CrawlResultResponse])
def get_results_by_keyword(
    keyword: str,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    results = db.query(models.CrawlResult).filter(
        models.CrawlResult.keyword_matched == keyword,
        models.CrawlResult.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return results

@router.get("/{result_id}", response_model=schemas.CrawlResultResponse)
def get_result(
    result_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = db.query(models.CrawlResult).filter(
        models.CrawlResult.id == result_id,
        models.CrawlResult.user_id == current_user.id
    ).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result