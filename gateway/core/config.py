from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    APP_NAME: str = "AI Agent Gateway"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # 服务器配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # OpenCode Server 配置
    OPENCODE_SERVER_URL: str = "http://203.0.113.10:1776"
    OPENCODE_SERVER_USERNAME: str = "opencode"
    OPENCODE_SERVER_PASSWORD: str = "YOUR_PASSWORD"
    
    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://aigateway:aigateway123@localhost:5432/aigateway"
    REDIS_URL: str = "redis://localhost:6380/0"
    
    # JWT 配置
    JWT_SECRET_KEY: str = "your-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS 配置
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
