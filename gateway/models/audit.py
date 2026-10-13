from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func
from core.database import Base
import uuid


class AuditLog(Base):
    """审计日志模型"""
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True, index=True)
    action = Column(String(100), nullable=False)  # login, create_session, send_message, etc.
    resource_type = Column(String(50), nullable=True)  # session, message, user
    resource_id = Column(String(36), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    details = Column(String, nullable=True)  # JSON 格式的详细数据
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, action={self.action})>"
