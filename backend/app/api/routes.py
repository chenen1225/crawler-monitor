from fastapi import APIRouter
from app.api import auth, sites, keywords, tasks, results

router = APIRouter()

# 包含各个模块的路由
router.include_router(auth.router, tags=["auth"], prefix="/auth")
router.include_router(sites.router, tags=["sites"], prefix="/sites")
router.include_router(keywords.router, tags=["keywords"], prefix="/keywords")
router.include_router(tasks.router, tags=["tasks"], prefix="/tasks")
router.include_router(results.router, tags=["results"], prefix="/results")