import asyncio
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from core.config import get_settings

settings = get_settings()

# 创建同步引擎（用于初始化表）
sync_engine = create_engine(
    settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"),
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# 创建会话工厂
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 基础模型类
class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """获取数据库会话"""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库表"""
    # 导入所有模型以确保它们被注册到 Base.metadata
    from models.user import User, Session, Message
    from models.audit import AuditLog
    
    # 使用同步引擎创建表
    Base.metadata.create_all(sync_engine)
    print("✅ 数据库表初始化完成")
    
    # 创建默认管理员账户（如果不存在）
    from sqlalchemy.orm import Session
    from core.security import get_password_hash
    
    with Session(sync_engine) as session:
        from sqlalchemy import select
        result = session.execute(select(User).where(User.username == "admin"))
        if not result.scalar_one_or_none():
            admin_user = User(
                username="admin",
                password_hash=get_password_hash("admin123"),
                role="super_admin",
                is_active=True,
            )
            session.add(admin_user)
            session.commit()
            print("✅ 默认管理员账户已创建 (用户名: admin, 密码: admin123)")


async def close_db():
    """关闭数据库连接"""
    await engine.dispose()
