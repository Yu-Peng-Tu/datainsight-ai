from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import upload, analyze, charts, report

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI 驱动的数据洞察平台 API"
)

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(upload.router, prefix="/api", tags=["文件上传"])
app.include_router(analyze.router, prefix="/api", tags=["AI 分析"])
app.include_router(charts.router, prefix="/api", tags=["可视化图表"])
app.include_router(report.router, prefix="/api", tags=["报告导出"])


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    init_db()


@app.get("/")
async def root():
    """健康检查"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """API 健康检查"""
    return {"status": "ok"}
