from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes
import uvicorn

app = FastAPI(
    title="Crawler Monitor API",
    description="A web service for monitoring keywords on specified websites",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应限制为具体的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含API路由
app.include_router(routes.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Crawler Monitor API is running"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)