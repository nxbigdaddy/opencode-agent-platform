from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import get_settings
from core.database import init_db, close_db
from api.chat import router as chat_router
from api.auth import router as auth_router
from api.audit import router as audit_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    await init_db()
    print(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} 启动成功")
    print(f"📡 OpenCode Server: {settings.OPENCODE_SERVER_URL}")
    print(f"🔐 多租户认证已启用")
    
    yield
    
    # 关闭时清理
    await close_db()


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Agent 对话平台 - Gateway API（支持多租户）",
    lifespan=lifespan,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router)   # 认证路由（无需认证）
app.include_router(chat_router)   # 聊天路由（需要认证）
app.include_router(audit_router)  # 审计日志路由（管理员）


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "multi_tenant": True,
    }


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to AI Agent Gateway (Multi-Tenant)",
        "docs": "/docs",
        "health": "/health",
        "auth": "/api/v1/auth/login",
        "register": "/api/v1/auth/register",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
