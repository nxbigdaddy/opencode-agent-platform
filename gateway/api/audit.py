from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from core.database import get_db
from core.security import get_current_admin_user
from models.user import User
from services.audit import AuditService

router = APIRouter(prefix="/api/v1/audit", tags=["审计日志"])


@router.get("/logs")
async def get_audit_logs(
    user_id: Optional[str] = Query(None, description="筛选特定用户"),
    action: Optional[str] = Query(None, description="筛选特定操作"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取审计日志列表 (仅管理员)
    """
    logs = await AuditService.get_logs(
        db=db,
        user_id=user_id,
        action=action,
        limit=limit,
        offset=offset,
    )
    
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "ip_address": log.ip_address,
            "details": log.details,
            "created_at": log.created_at,
        }
        for log in logs
    ]
