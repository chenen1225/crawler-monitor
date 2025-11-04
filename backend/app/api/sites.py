from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import schemas, models
from app.utils import get_current_user

router = APIRouter()

@router.get("/", response_model=List[schemas.MonitoredSiteResponse])
def get_sites(
    skip: int = 0, 
    limit: int = 100, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sites = db.query(models.MonitoredSite).filter(
        models.MonitoredSite.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return sites

@router.post("/", response_model=schemas.MonitoredSiteResponse)
def create_site(
    site: schemas.MonitoredSiteCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_site = models.MonitoredSite(**site.dict(), user_id=current_user.id)
    db.add(db_site)
    db.commit()
    db.refresh(db_site)
    return db_site

@router.get("/{site_id}", response_model=schemas.MonitoredSiteResponse)
def get_site(
    site_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    site = db.query(models.MonitoredSite).filter(
        models.MonitoredSite.id == site_id,
        models.MonitoredSite.user_id == current_user.id
    ).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site

@router.put("/{site_id}", response_model=schemas.MonitoredSiteResponse)
def update_site(
    site_id: int,
    site: schemas.MonitoredSiteUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_site = db.query(models.MonitoredSite).filter(
        models.MonitoredSite.id == site_id,
        models.MonitoredSite.user_id == current_user.id
    ).first()
    if not db_site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    update_data = site.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_site, field, value)
    
    db.commit()
    db.refresh(db_site)
    return db_site

@router.delete("/{site_id}")
def delete_site(
    site_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    site = db.query(models.MonitoredSite).filter(
        models.MonitoredSite.id == site_id,
        models.MonitoredSite.user_id == current_user.id
    ).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    db.delete(site)
    db.commit()
    return {"message": "Site deleted successfully"}