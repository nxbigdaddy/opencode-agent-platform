from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from datetime import datetime


class QuotaManager:
    """租户资源配额管理器"""
    
    @staticmethod
    async def check_quota(user_id: str, db: AsyncSession) -> dict:
        """检查用户配额状态"""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            return {
                "has_quota": False,
                "message": "用户不存在",
            }
        
        remaining = user.quota - user.used_quota
        
        return {
            "has_quota": remaining > 0,
            "quota": user.quota,
            "used_quota": user.used_quota,
            "remaining": remaining,
            "message": "配额充足" if remaining > 0 else "配额已用完",
        }
    
    @staticmethod
    async def consume_quota(user_id: str, token_count: int, db: AsyncSession) -> bool:
        """扣减用户配额"""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            return False
        
        remaining = user.quota - user.used_quota
        if remaining < token_count:
            return False
        
        # 扣减配额
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                used_quota=user.used_quota + token_count,
                updated_at=datetime.utcnow(),
            )
        )
        await db.commit()
        
        return True
    
    @staticmethod
    async def reset_quota(user_id: str, new_quota: int, db: AsyncSession):
        """重置用户配额（管理员操作）"""
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                quota=new_quota,
                used_quota=0,
                updated_at=datetime.utcnow(),
            )
        )
        await db.commit()
    
    @staticmethod
    async def estimate_tokens(text: str) -> int:
        """估算文本的 Token 数量（粗略估算）"""
        # 中文约 1.5-2 个字符 = 1 token
        # 英文约 4 个字符 = 1 token
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other_chars = len(text) - chinese_chars
        
        return int(chinese_chars * 0.6 + other_chars * 0.25)
