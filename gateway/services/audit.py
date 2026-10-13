from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.audit import AuditLog
from typing import Optional
import json


class AuditService:
    """审计日志服务"""

    @staticmethod
    async def log_action(
        db: AsyncSession,
        action: str,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[dict] = None,
    ):
        """记录操作日志"""
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=json.dumps(details) if details else None,
        )
        db.add(log_entry)
        await db.commit()

    @staticmethod
    async def get_logs(
        db: AsyncSession,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ):
        """获取日志列表"""
        query = select(AuditLog)
        
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if action:
            query = query.where(AuditLog.action == action)
            
        query = query.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.scalars().all()
