from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import schemas, models
from app.utils import get_current_user

router = APIRouter()

@router.get("/", response_model=List[schemas.KeywordResponse])
def get_keywords(
    skip: int = 0, 
    limit: int = 100, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    keywords = db.query(models.Keyword).filter(
        models.Keyword.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return keywords

@router.post("/", response_model=schemas.KeywordResponse)
def create_keyword(
    keyword: schemas.KeywordCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_keyword = models.Keyword(**keyword.dict(), user_id=current_user.id)
    db.add(db_keyword)
    db.commit()
    db.refresh(db_keyword)
    return db_keyword

@router.get("/{keyword_id}", response_model=schemas.KeywordResponse)
def get_keyword(
    keyword_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    keyword = db.query(models.Keyword).filter(
        models.Keyword.id == keyword_id,
        models.Keyword.user_id == current_user.id
    ).first()
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")
    return keyword

@router.put("/{keyword_id}", response_model=schemas.KeywordResponse)
def update_keyword(
    keyword_id: int,
    keyword: schemas.KeywordUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_keyword = db.query(models.Keyword).filter(
        models.Keyword.id == keyword_id,
        models.Keyword.user_id == current_user.id
    ).first()
    if not db_keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")
    
    update_data = keyword.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_keyword, field, value)
    
    db.commit()
    db.refresh(db_keyword)
    return db_keyword

@router.delete("/{keyword_id}")
def delete_keyword(
    keyword_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    keyword = db.query(models.Keyword).filter(
        models.Keyword.id == keyword_id,
        models.Keyword.user_id == current_user.id
    ).first()
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")
    
    db.delete(keyword)
    db.commit()
    return {"message": "Keyword deleted successfully"}