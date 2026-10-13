from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class Role(str, Enum):
    """消息角色"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageStatus(str, Enum):
    """消息状态"""
    PENDING = "pending"
    STREAMING = "streaming"
    COMPLETED = "completed"
    ERROR = "error"


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., min_length=1, max_length=4000, description="用户消息")
    session_id: Optional[str] = Field(None, description="会话ID，为空则创建新会话")
    agent: Optional[str] = Field("general", description="Agent 名称")


class ChatResponse(BaseModel):
    """聊天响应（非流式）"""
    session_id: str
    message_id: str
    role: Role = Role.ASSISTANT
    content: str
    status: MessageStatus = MessageStatus.COMPLETED
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SessionInfo(BaseModel):
    """会话信息"""
    id: str
    title: str
    agent: str = "general"
    message_count: int = 0
    created_at: datetime
    updated_at: datetime


class SSEEvent(BaseModel):
    """SSE 事件"""
    type: str = Field(..., description="事件类型: text/tool_result/done/error")
    data: dict = Field(default_factory=dict, description="事件数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
