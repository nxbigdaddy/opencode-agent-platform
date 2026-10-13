from sqlalchemy import Column, String, Boolean, DateTime, Integer
from sqlalchemy.sql import func
from core.database import Base
import uuid


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)  # user, admin, super_admin
    is_active = Column(Boolean, default=True, nullable=False)
    quota = Column(Integer, default=100000)  # Token 配额
    used_quota = Column(Integer, default=0)  # 已使用配额
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class Session(Base):
    """会话模型"""
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)  # 外键关联 user.id
    title = Column(String(200), default="新会话", nullable=False)
    agent = Column(String(50), default="general", nullable=False)
    status = Column(String(20), default="active", nullable=False)  # active, archived, deleted
    message_count = Column(Integer, default=0, nullable=False)
    workspace = Column(String(500), nullable=True)  # 工作区路径
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, title={self.title})>"


class Message(Base):
    """消息模型"""
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), nullable=False, index=True)  # 外键关联 session.id
    user_id = Column(String(36), nullable=False, index=True)  # 冗余字段，便于查询
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(String, nullable=False)
    token_count = Column(Integer, default=0)  # Token 消耗
    status = Column(String(20), default="completed", nullable=False)  # pending, streaming, completed, error
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Message(id={self.id}, session_id={self.session_id}, role={self.role})>"
