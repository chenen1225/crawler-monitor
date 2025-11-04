import uvicorn
from app.database_init import init_db

if __name__ == "__main__":
    # 初始化数据库
    init_db()
    
    # 启动FastAPI应用
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"]
    )