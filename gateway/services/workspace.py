import os
import json
import re
import uuid
import asyncio
from typing import AsyncGenerator, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class CommandTemplate:
    """命令模板"""
    name: str
    description: str
    agent: str = "general"
    model: str = ""
    prompt_template: str = ""
    parameters: list[str] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = []


class WorkspaceManager:
    """工作区管理器 - 实现租户物理隔离"""
    
    def __init__(self, base_path: str = "/workspaces"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def get_user_workspace(self, user_id: str) -> Path:
        """获取用户工作区根目录"""
        user_path = self.base_path / user_id
        user_path.mkdir(parents=True, exist_ok=True)
        return user_path
    
    def get_session_workspace(self, user_id: str, session_id: str) -> Path:
        """获取会话工作区（物理隔离）"""
        session_path = self.get_user_workspace(user_id) / session_id
        session_path.mkdir(parents=True, exist_ok=True)
        return session_path
    
    def cleanup_session_workspace(self, user_id: str, session_id: str):
        """清理会话工作区"""
        session_path = self.get_session_workspace(user_id, session_id)
        if session_path.exists():
            import shutil
            shutil.rmtree(session_path)


class CommandRegistry:
    """命令注册表 - 管理 OpenCode 预设指令"""
    
    def __init__(self, global_commands_path: str = None, project_commands_path: str = None):
        self.global_commands_path = Path(global_commands_path or "/opt/aigateway/commands/global")
        self.project_commands_path = Path(project_commands_path or "/opt/aigateway/commands/project")
        self.commands: dict[str, CommandTemplate] = {}
        
        # 确保目录存在
        self.global_commands_path.mkdir(parents=True, exist_ok=True)
        self.project_commands_path.mkdir(parents=True, exist_ok=True)
        
        # 加载命令
        self._load_commands()
    
    def _load_commands(self):
        """从文件系统加载命令模板"""
        # 加载全局命令
        self._load_from_directory(self.global_commands_path, is_global=True)
        # 加载项目命令
        self._load_from_directory(self.project_commands_path, is_global=False)
    
    def _load_from_directory(self, directory: Path, is_global: bool):
        """从目录加载 Markdown 命令文件"""
        if not directory.exists():
            return
        
        for md_file in directory.glob("*.md"):
            try:
                command = self._parse_command_file(md_file, is_global)
                if command:
                    self.commands[command.name] = command
            except Exception as e:
                print(f"加载命令文件失败 {md_file}: {e}")
    
    def _parse_command_file(self, file_path: Path, is_global: bool) -> Optional[CommandTemplate]:
        """解析 Markdown 命令文件"""
        content = file_path.read_text(encoding='utf-8')
        
        # 提取 Frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
        if not frontmatter_match:
            return None
        
        frontmatter_text = frontmatter_match.group(1)
        prompt_template = frontmatter_match.group(2).strip()
        
        # 解析 Frontmatter
        frontmatter = {}
        for line in frontmatter_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip().strip('"').strip("'")
        
        # 提取参数（从 prompt_template 中的 $1, $2 等）
        parameters = re.findall(r'\$(\d+)', prompt_template)
        parameters = [f"${i}" for i in sorted(set(int(p) for p in parameters))]
        
        return CommandTemplate(
            name=file_path.stem,
            description=frontmatter.get('description', ''),
            agent=frontmatter.get('agent', 'general'),
            model=frontmatter.get('model', ''),
            prompt_template=prompt_template,
            parameters=parameters,
        )
    
    def get_command(self, name: str) -> Optional[CommandTemplate]:
        """获取命令模板"""
        return self.commands.get(name)
    
    def list_commands(self) -> list[dict]:
        """列出所有可用命令"""
        return [
            {
                "name": cmd.name,
                "description": cmd.description,
                "agent": cmd.agent,
                "parameters": cmd.parameters,
            }
            for cmd in self.commands.values()
        ]
    
    def add_command(self, command: CommandTemplate, is_global: bool = False):
        """添加命令模板"""
        target_dir = self.global_commands_path if is_global else self.project_commands_path
        file_path = target_dir / f"{command.name}.md"
        
        # 生成 Markdown 文件
        frontmatter = f"""---
description: "{command.description}"
agent: "{command.agent}"
model: "{command.model}"
---

{command.prompt_template}
"""
        file_path.write_text(frontmatter, encoding='utf-8')
        self.commands[command.name] = command
    
    def render_command(self, name: str, args: list[str]) -> Optional[str]:
        """渲染命令模板，替换参数"""
        command = self.get_command(name)
        if not command:
            return None
        
        prompt = command.prompt_template
        for i, arg in enumerate(args):
            prompt = prompt.replace(f"${i+1}", arg)
        
        return prompt


# 全局实例
workspace_manager = WorkspaceManager()
command_registry = CommandRegistry()
