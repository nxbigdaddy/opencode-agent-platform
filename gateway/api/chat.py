from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

from core.database import get_db
from core.security import get_current_user
from models.chat import ChatRequest, ChatResponse, SessionInfo
from models.user import User, Session as SessionModel, Message
from services.opencode_client import opencode_client
from services.quota import QuotaManager
from services.workspace import command_registry

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    发送聊天消息（非流式）
    
    等待完整响应后返回
    """
    try:
        # 检查配额
        quota_status = await QuotaManager.check_quota(current_user.id, db)
        if not quota_status["has_quota"]:
            raise HTTPException(
                status_code=403,
                detail=f"配额不足：{quota_status['message']}（剩余：{quota_status['remaining']} tokens）",
            )
        
        session_id = request.session_id
        
        # 如果没有会话ID，创建新会话
        if not session_id:
            # 创建数据库会话记录
            db_session = SessionModel(
                user_id=current_user.id,
                title="新会话",
                agent=request.agent or "general",
            )
            db.add(db_session)
            await db.commit()
            await db.refresh(db_session)
            session_id = db_session.id
            
            # 创建物理隔离的工作区
            await opencode_client.create_session(current_user.id)
        
        # 验证会话属于当前用户
        result = await db.execute(
            select(SessionModel).where(
                SessionModel.id == session_id,
                SessionModel.user_id == current_user.id,
            )
        )
        db_session = result.scalar_one_or_none()
        if not db_session:
            raise HTTPException(status_code=404, detail="会话不存在或无权访问")
        
        # 收集所有 SSE 事件
        full_response = ""
        async for event_data in opencode_client.send_message_sse(
            session_id=session_id,
            message=request.message,
            user_id=current_user.id,
        ):
            if event_data.startswith("data: "):
                data = json.loads(event_data[6:])
                if "text" in data:
                    full_response += data["text"]
        
        # 估算 Token 消耗
        token_count = await QuotaManager.estimate_tokens(request.message + full_response)
        
        # 扣减配额
        await QuotaManager.consume_quota(current_user.id, token_count, db)
        
        # 保存用户消息
        user_message = Message(
            session_id=session_id,
            user_id=current_user.id,
            role="user",
            content=request.message,
            token_count=await QuotaManager.estimate_tokens(request.message),
        )
        db.add(user_message)
        
        # 保存 AI 回复
        ai_message = Message(
            session_id=session_id,
            user_id=current_user.id,
            role="assistant",
            content=full_response,
            token_count=await QuotaManager.estimate_tokens(full_response),
        )
        db.add(ai_message)
        
        # 更新会话
        db_session.message_count += 2
        if db_session.title == "新会话" and request.message:
            db_session.title = request.message[:50]
        
        await db.commit()
        
        return ChatResponse(
            session_id=session_id,
            message_id=ai_message.id,
            content=full_response,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    发送聊天消息（流式 SSE）
    
    实时返回 AI 响应片段
    """
    try:
        # 检查配额
        quota_status = await QuotaManager.check_quota(current_user.id, db)
        if not quota_status["has_quota"]:
            raise HTTPException(
                status_code=403,
                detail=f"配额不足：{quota_status['message']}（剩余：{quota_status['remaining']} tokens）",
            )
        
        session_id = request.session_id
        
        # 如果没有会话ID，创建新会话
        if not session_id:
            db_session = SessionModel(
                user_id=current_user.id,
                title="新会话",
                agent=request.agent or "general",
            )
            db.add(db_session)
            await db.commit()
            await db.refresh(db_session)
            session_id = db_session.id
            
            # 创建物理隔离的工作区
            await opencode_client.create_session(current_user.id)
        
        # 验证会话属于当前用户
        result = await db.execute(
            select(SessionModel).where(
                SessionModel.id == session_id,
                SessionModel.user_id == current_user.id,
            )
        )
        db_session = result.scalar_one_or_none()
        if not db_session:
            raise HTTPException(status_code=404, detail="会话不存在或无权访问")
        
        # 保存用户消息
        user_message = Message(
            session_id=session_id,
            user_id=current_user.id,
            role="user",
            content=request.message,
            token_count=await QuotaManager.estimate_tokens(request.message),
        )
        db.add(user_message)
        await db.commit()
        
        # 返回 SSE 流
        async def event_generator():
            # 发送会话ID
            yield f"event: session\ndata: {json.dumps({'session_id': session_id})}\n\n"
            
            # 转发 OpenCode SSE 流
            full_response = ""
            async for event_data in opencode_client.send_message_sse(
                session_id=session_id,
                message=request.message,
                user_id=current_user.id,
            ):
                yield event_data
                if event_data.startswith("data: "):
                    try:
                        data = json.loads(event_data[6:])
                        if "text" in data:
                            full_response += data["text"]
                    except:
                        pass
            
            # 估算 Token 消耗并扣减配额
            token_count = await QuotaManager.estimate_tokens(request.message + full_response)
            await QuotaManager.consume_quota(current_user.id, token_count, db)
            
            # 保存 AI 回复
            ai_message = Message(
                session_id=session_id,
                user_id=current_user.id,
                role="assistant",
                content=full_response,
                token_count=await QuotaManager.estimate_tokens(full_response),
            )
            db.add(ai_message)
            
            # 更新会话
            db_session.message_count += 2
            if db_session.title == "新会话" and request.message:
                db_session.title = request.message[:50]
            await db.commit()
            
            # 发送完成事件
            yield f"event: done\ndata: {json.dumps({'session_id': session_id})}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions", response_model=list[SessionInfo])
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的会话列表"""
    try:
        result = await db.execute(
            select(SessionModel)
            .where(SessionModel.user_id == current_user.id)
            .order_by(SessionModel.updated_at.desc())
        )
        sessions = result.scalars().all()
        
        return [
            SessionInfo(
                id=s.id,
                title=s.title,
                agent=s.agent,
                message_count=s.message_count,
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in sessions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", response_model=SessionInfo)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取会话详情"""
    try:
        result = await db.execute(
            select(SessionModel).where(
                SessionModel.id == session_id,
                SessionModel.user_id == current_user.id,
            )
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        return SessionInfo(
            id=session.id,
            title=session.title,
            agent=session.agent,
            message_count=session.message_count,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/messages")
async def get_messages(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取会话消息历史"""
    try:
        # 验证会话权限
        result = await db.execute(
            select(SessionModel).where(
                SessionModel.id == session_id,
                SessionModel.user_id == current_user.id,
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 获取消息
        result = await db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
        )
        messages = result.scalars().all()
        
        return [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "token_count": m.token_count,
                "created_at": m.created_at,
            }
            for m in messages
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quota")
async def get_quota(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户配额信息"""
    quota_status = await QuotaManager.check_quota(current_user.id, db)
    return quota_status


@router.get("/commands")
async def list_commands():
    """获取可用预设指令列表"""
    return command_registry.list_commands()
