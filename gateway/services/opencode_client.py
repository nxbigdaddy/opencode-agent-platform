import asyncio
import json
import uuid
import os
import re
from typing import AsyncGenerator
from core.config import get_settings
from services.workspace import workspace_manager, command_registry

settings = get_settings()


class OpenCodeClient:
    """OpenCode CLI 客户端（支持工作区隔离）"""
    
    def __init__(self):
        self.sessions = {}  # 本地会话管理
    
    async def create_session(self, user_id: str, directory: str = None) -> str:
        """创建本地会话（带工作区隔离）"""
        session_id = str(uuid.uuid4())[:12]
        
        # 创建物理隔离的工作区
        workspace_path = workspace_manager.get_session_workspace(user_id, session_id)
        
        self.sessions[session_id] = {
            "id": session_id,
            "user_id": user_id,
            "directory": str(workspace_path),
            "created_at": asyncio.get_event_loop().time(),
            "message_count": 0,
        }
        return session_id
    
    async def send_message_sse(
        self,
        session_id: str,
        message: str,
        user_id: str = None,
        directory: str = None,
    ) -> AsyncGenerator[str, None]:
        """发送消息并通过 CLI 获取响应（支持工作区隔离和预设指令）"""
        # 确保会话存在
        if session_id not in self.sessions:
            if user_id:
                workspace_path = workspace_manager.get_session_workspace(user_id, session_id)
            else:
                workspace_path = directory or "/tmp"
            
            self.sessions[session_id] = {
                "id": session_id,
                "user_id": user_id,
                "directory": str(workspace_path),
                "created_at": asyncio.get_event_loop().time(),
                "message_count": 0,
            }
        
        session = self.sessions[session_id]
        session["message_count"] += 1
        
        # 检查是否是预设指令调用（格式：/command-name arg1 arg2）
        command_match = re.match(r'^/(\S+)\s*(.*)', message)
        if command_match:
            command_name = command_match.group(1)
            args = command_match.group(2).split() if command_match.group(2) else []
            
            # 渲染命令模板
            rendered_prompt = command_registry.render_command(command_name, args)
            if rendered_prompt:
                message = rendered_prompt
        
        # 发送会话 ID 事件
        yield f"event: session\ndata: {json.dumps({'session_id': session_id})}\n\n"
        
        # 使用 opencode run 命令，在工作区目录下执行
        try:
            process = await asyncio.create_subprocess_exec(
                "opencode", "run", message,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=session["directory"],  # 使用隔离的工作区
            )
            
            stdout, stderr = await process.communicate()
            
            if stdout:
                response_text = stdout.decode('utf-8', errors='ignore').strip()
                # 过滤 ANSI 转义序列
                response_text = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', response_text)
                # 移除开头的提示符
                lines = response_text.split('\n')
                clean_lines = []
                for line in lines:
                    if not line.startswith('> ') and line.strip():
                        clean_lines.append(line)
                response_text = '\n'.join(clean_lines).strip()
                
                if response_text:
                    # 逐字返回，模拟流式打字机效果
                    for char in response_text:
                        yield f"data: {json.dumps({'text': char})}\n\n"
                        await asyncio.sleep(0.02)
                else:
                    yield f"data: {json.dumps({'text': '[AI 返回空响应]'})}\n\n"
            
            if stderr and process.returncode != 0:
                error_text = stderr.decode('utf-8', errors='ignore').strip()
                if error_text:
                    yield f"data: {json.dumps({'text': f'[错误] {error_text}'})}\n\n"
        
        except Exception as e:
            yield f"data: {json.dumps({'text': f'[执行失败] {str(e)}'})}\n\n"
        
        # 发送完成事件
        yield f"event: done\ndata: {json.dumps({'session_id': session_id})}\n\n"
    
    async def get_sessions(self, user_id: str = None) -> list[dict]:
        """获取会话列表（支持用户过滤）"""
        if user_id:
            return [s for s in self.sessions.values() if s.get("user_id") == user_id]
        return list(self.sessions.values())
    
    async def get_session(self, session_id: str) -> dict:
        """获取会话详情"""
        return self.sessions.get(session_id, {})


# 全局客户端实例
opencode_client = OpenCodeClient()
