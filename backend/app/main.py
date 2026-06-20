from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

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
    allow_origins=["*"],
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


@app.get("/api/health")
async def health_check():
    """API 健康检查"""
    return {"status": "ok"}


# SPA 回退路由：API 路由优先，其余返回静态文件或 index.html
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """提供前端静态文件，支持 SPA 路由回退"""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    file_path = os.path.join(static_dir, full_path)

    # 如果文件存在则返回
    if os.path.isfile(file_path):
        return FileResponse(file_path)

    # 否则返回 index.html（SPA 回退）
    return FileResponse(os.path.join(static_dir, "index.html"))
