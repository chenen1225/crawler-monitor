# 爬虫监控系统

这是一个前后端分离的爬虫监控系统，可以按照设定的关键词和频率在指定网站上搜索相关内容，并将结果保存到Excel文件。

## 项目结构

```
crawler-monitor/
├── backend/                 # 后端代码 (FastAPI)
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── models/         # 数据库模型
│   │   ├── schemas/        # Pydantic模型
│   │   ├── database/       # 数据库相关
│   │   ├── utils/          # 工具函数
│   │   └── crawler/        # 爬虫相关代码
│   ├── requirements.txt    # Python依赖
│   ├── run.py             # 启动脚本
│   └── app/
├── frontend/               # 前端代码 (React)
│   ├── public/
│   ├── src/
│   │   ├── App.js         # 主组件
│   │   └── index.js       # 入口文件
│   └── package.json       # Node.js依赖
└── README.md              # 项目说明
```

## 功能特性

### 后端功能
- 用户注册/登录认证
- 监控网站管理（增删改查）
- 关键词管理（增删改查）
- 爬虫任务配置（频率、网站、关键词）
- 自动爬取和内容提取
- AI生成一句话摘要
- 数据存储到Excel文件
- 任务调度系统

### 前端功能
- 用户友好的管理界面
- 仪表板概览
- 网站管理页面
- 关键词管理页面
- 任务管理页面
- 爬取结果展示

## 技术栈

### 后端
- FastAPI: Web框架
- SQLAlchemy: ORM
- Requests/BeautifulSoup: 爬虫工具
- Pandas/openpyxl: Excel文件处理
- APScheduler: 任务调度
- JWT: 认证

### 前端
- React: 前端框架
- Ant Design: UI组件库
- Axios: HTTP客户端

## 快速开始

### 后端设置

1. 安装Python依赖:
```bash
cd backend
pip install -r requirements.txt
```

2. 启动后端服务:
```bash
python run.py
```
服务将在 http://localhost:8000 启动

### 前端设置

1. 安装Node.js依赖:
```bash
cd frontend
npm install
```

2. 启动前端开发服务器:
```bash
npm start
```
前端将在 http://localhost:3000 启动

## API接口

- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/sites/` - 获取监控网站列表
- `POST /api/v1/sites/` - 添加监控网站
- `GET /api/v1/keywords/` - 获取关键词列表
- `POST /api/v1/keywords/` - 添加关键词
- `GET /api/v1/tasks/` - 获取爬虫任务列表
- `POST /api/v1/tasks/` - 添加爬虫任务
- `GET /api/v1/results/` - 获取爬取结果

## 配置说明

### 环境变量

在后端根目录创建 `.env` 文件以配置数据库连接：
```
DATABASE_URL=sqlite:///./crawler_monitor.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 爬虫配置

系统支持多种网站类型的爬取，可根据实际需要扩展爬取规则。

## 数据存储

- 配置数据存储在数据库中
- 爬取结果以Excel格式保存在指定目录
- 文件按日期和关键词分类存储

## 安全考虑

- 使用JWT进行身份验证
- 遵循robots.txt协议
- 控制爬取频率以避免对目标网站造成压力
- 数据加密存储

## 扩展性

- 支持添加新的网站类型解析规则
- 可配置不同的AI摘要服务
- 支持分布式部署
- 可扩展多种数据导出格式