# 05 - OpenCode 集成设计文档

**项目名称**：AI Agent 对话平台  
**版本**：v1.0  
**日期**：2026-04-21  
**编写人**：AI Agent 团队  
**目标读者**：后端开发、DevOps、架构师  
**参考文档**：
- [OpenCode Server 文档](https://opencode.ai/docs/server/)
- [OpenCode SDK 文档](https://opencode.ai/docs/sdk/)
- [OpenCode Agents 文档](https://opencode.ai/docs/agents/)
- [OpenCode MCP Servers 文档](https://opencode.ai/docs/mcp-servers/)
- [OpenCode Tools 文档](https://opencode.ai/docs/tools/)
- [OpenCode Custom Tools 文档](https://opencode.ai/docs/custom-tools/)

---

## 目录

1. [概述](#1-概述)
2. [OpenCode Server 部署](#2-opencode-server-部署)
3. [认证与通信](#3-认证与通信)
4. [会话管理集成](#4-会话管理集成)
5. [消息处理集成](#5-消息处理集成)
6. [Agent 系统集成](#6-agent-系统集成)
7. [MCP 工具集成](#7-mcp-工具集成)
8. [SSE 流式处理](#8-sse-流式处理)
9. [错误处理与重试](#9-错误处理与重试)
10. [性能优化](#10-性能优化)
11. [监控与健康检查](#11-监控与健康检查)
12. [代码示例](#12-代码示例)

---

## 1. 概述

### 1.1 集成目标

将 OpenCode CLI 的 `serve` 模式作为后台 Agent 引擎，通过其 HTTP API 实现：
- 多用户会话隔离
- 流式对话响应
- Agent 动态切换
- MCP 工具扩展
- 工作区文件管理

### 1.2 集成架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        网关层 (FastAPI)                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   OpenCode Client                        │   │
│  │  ┌────────────┐ ┌────────────┐ ┌─────────────────────┐  │   │
│  │  │ HTTP Client│ │ SSE Handler│ │ Session Manager     │  │   │
│  │  │ (httpx)    │ │ (async)    │ │ (映射表)            │  │   │
│  │  └──────┬─────┘ └──────┬─────┘ └─────────────────────┘  │   │
│  └─────────┼──────────────┼────────────────────────────────┘   │
└────────────┼──────────────┼─────────────────────────────────────┘
             │              │
             │ HTTP         │ SSE
             │              │
┌────────────┼──────────────┼─────────────────────────────────────┐
│            ▼              ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   OpenCode Server                        │   │
│  │              (http://127.0.0.1:4096)                     │   │
│  │  ┌────────────┐ ┌────────────┐ ┌─────────────────────┐  │   │
│  │  │ Session API│ │ Message API│ │ Event Stream        │  │   │
│  │  │            │ │            │ │ (SSE)               │  │   │
│  │  └──────┬─────┘ └──────┬─────┘ └─────────────────────┘  │   │
│  └─────────┼──────────────┼────────────────────────────────┘   │
│            │              │                                     │
│            ▼              ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                     MCP Servers                          │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. OpenCode Server 部署

### 2.1 安装

**通过 npm 安装**（参考 [OpenCode 文档](https://opencode.ai/docs/)）：

```bash
npm install -g opencode-ai
```

**或通过 curl**：

```bash
curl -fsSL https://opencode.ai/install | bash
```

**或通过 Docker**：

```bash
docker run -it --rm ghcr.io/anomalyco/opencode
```

### 2.2 启动配置

**基础启动**（参考 [OpenCode Server 文档](https://opencode.ai/docs/server/)）：

```bash
opencode serve --port 4096 --hostname 127.0.0.1
```

**生产环境启动**（启用认证）：

```bash
export OPENCODE_SERVER_PASSWORD="YOUR_PASSWORD"
export OPENCODE_SERVER_USERNAME="gateway"
export OPENCODE_API_KEY="YOUR_SECRET"
export OPENCODE_MODEL="anthropic/claude-sonnet-4-20250514"

opencode serve \
  --port 4096 \
  --hostname 127.0.0.1 \
  --cors http://localhost:3000 \
  --cors https://app.aigateway.example.com
```

**systemd 服务配置**：

```ini
# /etc/systemd/system/opencode.service
[Unit]
Description=OpenCode Agent Server
After=network.target

[Service]
Type=simple
User=opencode
Group=opencode
WorkingDirectory=/opt/opencode

Environment="OPENCODE_SERVER_PASSWORD=YOUR_PASSWORD"
Environment="OPENCODE_SERVER_USERNAME=gateway"
Environment="OPENCODE_API_KEY=YOUR_SECRET"
Environment="OPENCODE_MODEL=anthropic/claude-sonnet-4-20250514"
Environment="PATH=/usr/local/bin:/usr/bin:/bin"

ExecStart=/usr/local/bin/opencode serve --port 4096 --hostname 127.0.0.1
ExecReload=/bin/kill -HUP $MAINPID

Restart=always
RestartSec=5
StartLimitInterval=60s
StartLimitBurst=3

# 资源限制
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
```

**启动服务**：

```bash
sudo systemctl daemon-reload
sudo systemctl enable opencode
sudo systemctl start opencode
sudo systemctl status opencode
```

### 2.3 配置工作区模板

**初始化用户工作区脚本**：

```bash
#!/bin/bash
# init-workspace.sh

USER_ID=$1
SESSION_ID=$2
WORKSPACE_BASE="/opt/aigateway/workspaces"
WORKSPACE_DIR="${WORKSPACE_BASE}/${USER_ID}/${SESSION_ID}"

# 创建工作区目录
mkdir -p "${WORKSPACE_DIR}/workspace"
mkdir -p "${WORKSPACE_DIR}/.opencode"

# 创建默认配置文件
cat > "${WORKSPACE_DIR}/.opencode/config.json" <<EOF
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-20250514",
  "permission": {
    "edit": "ask",
    "bash": "ask"
  }
}
EOF

# 设置权限
chown -R opencode:opencode "${WORKSPACE_DIR}"
chmod -R 750 "${WORKSPACE_DIR}"

echo "Workspace initialized: ${WORKSPACE_DIR}"
```

---

## 3. 认证与通信

### 3.1 HTTP Basic Auth

OpenCode Server 支持 HTTP Basic Auth（参考 [OpenCode Server 文档 - Authentication](https://opencode.ai/docs/server/)）。

**Python 客户端示例**：

```python
import httpx

class OpenCodeClient:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.auth = (username, password)
        self.client = httpx.AsyncClient(auth=self.auth, timeout=60.0)
    
    async def health_check(self) -> dict:
        """检查服务健康状态"""
        response = await self.client.get(f"{self.base_url}/global/health")
        response.raise_for_status()
        return response.json()
```

### 3.2 连接池配置

```python
import httpx

# 使用连接池提高性能
limits = httpx.Limits(
    max_keepalive_connections=20,
    max_connections=100
)

timeout = httpx.Timeout(
    connect=5.0,
    read=60.0,
    write=10.0,
    pool=5.0
)

client = httpx.AsyncClient(
    auth=("gateway", "your-password"),
    limits=limits,
    timeout=timeout,
    http2=True  # 启用 HTTP/2
)
```

---

## 4. 会话管理集成

### 4.1 会话生命周期映射

```
Gateway Session          OpenCode Session
     │                         │
     │── create ──────────────►│ POST /session
     │◄── session_id ──────────│
     │                         │
     │── send message ────────►│ POST /session/{id}/message
     │◄── SSE stream ──────────│
     │                         │
     │── delete ──────────────►│ DELETE /session/{id}
     │◄── success ─────────────│
```

### 4.2 创建会话

**OpenCode API**（参考 [OpenCode Server 文档 - Sessions](https://opencode.ai/docs/server/)）：

```python
async def create_opencode_session(
    self, 
    title: str | None = None,
    parent_id: str | None = None
) -> dict:
    """
    创建 OpenCode 会话
    
    POST /session
    Body: { parentID?, title? }
    Returns: Session
    """
    payload = {}
    if title:
        payload["title"] = title
    if parent_id:
        payload["parentID"] = parent_id
    
    response = await self.client.post(
        f"{self.base_url}/session",
        json=payload
    )
    response.raise_for_status()
    return response.json()
```

**Session 对象结构**（参考 [OpenCode SDK 文档](https://opencode.ai/docs/sdk/)）：

```typescript
interface Session {
  id: string;
  title: string;
  status: string;
  createdAt: string;
  updatedAt: string;
  parentID?: string;
  children?: Session[];
}
```

### 4.3 获取会话列表

```python
async def list_opencode_sessions(self) -> list[dict]:
    """
    获取所有 OpenCode 会话
    
    GET /session
    Returns: Session[]
    """
    response = await self.client.get(f"{self.base_url}/session")
    response.raise_for_status()
    return response.json()
```

### 4.4 删除会话

```python
async def delete_opencode_session(self, session_id: str) -> bool:
    """
    删除 OpenCode 会话
    
    DELETE /session/{id}
    Returns: boolean
    """
    response = await self.client.delete(
        f"{self.base_url}/session/{session_id}"
    )
    response.raise_for_status()
    return response.json()
```

### 4.5 会话状态映射表

网关层维护 `gateway_session` ↔ `opencode_session` 的映射关系：

```python
class SessionMapping(BaseModel):
    gateway_session_id: UUID      # 网关层会话 ID
    opencode_session_id: str      # OpenCode 会话 ID
    user_id: UUID                 # 用户 ID
    workspace_path: str           # 工作区路径
    agent_id: UUID                # 当前 Agent ID
    created_at: datetime
    updated_at: datetime
```

---

## 5. 消息处理集成

### 5.1 发送消息（同步）

**OpenCode API**（参考 [OpenCode Server 文档 - Messages](https://opencode.ai/docs/server/)）：

```python
async def send_message(
    self,
    session_id: str,
    content: str,
    agent: str | None = None,
    model: str | None = None,
    no_reply: bool = False
) -> dict:
    """
    发送消息并等待响应
    
    POST /session/{id}/message
    Body: { messageID?, model?, agent?, noReply?, system?, tools?, parts }
    Returns: { info: Message, parts: Part[] }
    """
    payload = {
        "parts": [{"type": "text", "text": content}]
    }
    
    if agent:
        payload["agent"] = agent
    if model:
        payload["model"] = model
    if no_reply:
        payload["noReply"] = True
    
    response = await self.client.post(
        f"{self.base_url}/session/{session_id}/message",
        json=payload
    )
    response.raise_for_status()
    return response.json()
```

### 5.2 异步发送消息

```python
async def send_message_async(
    self,
    session_id: str,
    content: str,
    agent: str | None = None
) -> None:
    """
    异步发送消息（不等待响应）
    
    POST /session/{id}/prompt_async
    Body: same as /message
    Returns: 204 No Content
    """
    payload = {
        "parts": [{"type": "text", "text": content}]
    }
    
    if agent:
        payload["agent"] = agent
    
    response = await self.client.post(
        f"{self.base_url}/session/{session_id}/prompt_async",
        json=payload
    )
    response.raise_for_status()
```

### 5.3 消息结构

**Part 类型**（参考 [OpenCode SDK 文档](https://opencode.ai/docs/sdk/)）：

```typescript
interface Part {
  type: 'text' | 'code' | 'image' | 'tool_use' | 'tool_result';
  text?: string;
  code?: string;
  language?: string;
  source?: {
    type: 'base64';
    media_type: string;
    data: string;
  };
}
```

### 5.4 获取消息列表

```python
async def get_messages(
    self,
    session_id: str,
    limit: int | None = None
) -> list[dict]:
    """
    获取会话消息列表
    
    GET /session/{id}/message?limit={limit}
    Returns: { info: Message, parts: Part[] }[]
    """
    params = {}
    if limit:
        params["limit"] = limit
    
    response = await self.client.get(
        f"{self.base_url}/session/{session_id}/message",
        params=params
    )
    response.raise_for_status()
    return response.json()
```

---

## 6. Agent 系统集成

### 6.1 获取 Agent 列表

**OpenCode API**（参考 [OpenCode Server 文档 - Agents](https://opencode.ai/docs/server/)）：

```python
async def list_agents(self) -> list[dict]:
    """
    获取所有可用 Agent
    
    GET /agent
    Returns: Agent[]
    """
    response = await self.client.get(f"{self.base_url}/agent")
    response.raise_for_status()
    return response.json()
```

**Agent 对象结构**（参考 [OpenCode Agents 文档](https://opencode.ai/docs/agents/)）：

```typescript
interface Agent {
  id: string;
  name: string;
  description: string;
  mode: 'primary' | 'subagent' | 'all';
  model?: string;
  temperature?: number;
  prompt?: string;
  color?: string;
  hidden?: boolean;
}
```

### 6.2 Agent 配置

OpenCode 的 Agent 配置存储在 `~/.config/opencode/config.json` 或项目目录的 `.opencode/config.json` 中（参考 [OpenCode Agents 文档 - Configure](https://opencode.ai/docs/agents/)）。

**配置示例**：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "build": {
      "mode": "primary",
      "model": "anthropic/claude-sonnet-4-20250514",
      "temperature": 0.3,
      "prompt": "{file:./prompts/build.txt}"
    },
    "code-reviewer": {
      "description": "Reviews code for best practices",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-4-20250514",
      "temperature": 0.1,
      "permission": {
        "edit": "deny",
        "bash": false
      }
    }
  }
}
```

**动态 Agent 配置**：

每个工作区可以有自己的 Agent 配置：

```python
async def configure_workspace_agent(
    self,
    workspace_path: str,
    agent_config: dict
) -> None:
    """为指定工作区配置 Agent"""
    import json
    import os
    
    config_path = os.path.join(workspace_path, ".opencode", "config.json")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    # 写入配置
    with open(config_path, 'w') as f:
        json.dump(agent_config, f, indent=2)
    
    # 设置权限
    os.chmod(config_path, 0o640)
```

### 6.3 Agent 权限系统

OpenCode 使用 `permission` 字段控制工具访问（参考 [OpenCode Agents 文档 - Permissions](https://opencode.ai/docs/agents/)）：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "edit": "ask",
    "bash": {
      "*": "ask",
      "git status *": "allow"
    }
  }
}
```

**权限级别**：
- `"allow"` - 允许执行
- `"ask"` - 执行前询问确认
- `"deny"` - 禁止执行

**网关层权限增强**：

在 OpenCode 权限基础上，网关层增加额外的权限检查：

```python
class PermissionChecker:
    def __init__(self, user_role: str, agent_config: dict):
        self.user_role = user_role
        self.agent_config = agent_config
    
    def can_use_tool(self, tool_name: str) -> bool:
        """检查用户是否可以使用指定工具"""
        # 管理员可以使用所有工具
        if self.user_role == 'superadmin':
            return True
        
        # 检查 Agent 配置中的工具白名单
        allowed_tools = self.agent_config.get('allowed_tools', [])
        if tool_name not in allowed_tools:
            return False
        
        return True
    
    def can_execute_command(self, command: str) -> tuple[bool, str]:
        """检查是否可以执行 Shell 命令"""
        # 命令白名单
        whitelist = ['git', 'python', 'ls', 'cat', 'grep']
        
        cmd = command.split()[0]
        if cmd not in whitelist:
            return False, f"Command '{cmd}' is not in whitelist"
        
        return True, ""
```

---

## 7. MCP 工具集成

### 7.1 MCP 服务注册

OpenCode 支持动态添加 MCP Server（参考 [OpenCode Server 文档 - LSP, Formatters & MCP](https://opencode.ai/docs/server/)）：

```python
async def add_mcp_server(self, name: str, config: dict) -> dict:
    """
    添加 MCP Server
    
    POST /mcp
    Body: { name, config }
    Returns: MCP status object
    """
    response = await self.client.post(
        f"{self.base_url}/mcp",
        json={"name": name, "config": config}
    )
    response.raise_for_status()
    return response.json()
```

### 7.2 MCP 配置格式

**Local MCP**（参考 [OpenCode MCP Servers 文档 - Local](https://opencode.ai/docs/mcp-servers/)）：

```python
local_mcp_config = {
    "type": "local",
    "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem"],
    "environment": {
        "ALLOWED_PATHS": "/opt/aigateway/workspaces"
    },
    "enabled": True
}
```

**Remote MCP**（参考 [OpenCode MCP Servers 文档 - Remote](https://opencode.ai/docs/mcp-servers/)）：

```python
remote_mcp_config = {
    "type": "remote",
    "url": "https://mcp.example.com",
    "headers": {
        "Authorization": "Bearer token"
    },
    "enabled": True
}
```

### 7.3 自定义 MCP 服务

**文件系统 MCP**（Python 实现）：

```python
# mcp_filesystem.py
from mcp.server.fastmcp import FastMCP
import os

mcp = FastMCP("filesystem")

@mcp.tool()
def read_file(path: str) -> str:
    """读取文件内容"""
    # 安全检查：防止目录遍历
    allowed_base = os.environ.get('ALLOWED_PATHS', '/tmp')
    full_path = os.path.join(allowed_base, path)
    
    # 确保路径在允许范围内
    if not full_path.startswith(allowed_base):
        raise ValueError("Path not allowed")
    
    with open(full_path, 'r') as f:
        return f.read()

@mcp.tool()
def write_file(path: str, content: str) -> str:
    """写入文件"""
    allowed_base = os.environ.get('ALLOWED_PATHS', '/tmp')
    full_path = os.path.join(allowed_base, path)
    
    if not full_path.startswith(allowed_base):
        raise ValueError("Path not allowed")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    with open(full_path, 'w') as f:
        f.write(content)
    
    return "File written successfully"

if __name__ == "__main__":
    mcp.run()
```

**注册自定义 MCP**：

```python
# 在 OpenCode 配置中注册
mcp_config = {
    "type": "local",
    "command": ["python", "/opt/aigateway/mcp-servers/filesystem.py"],
    "environment": {
        "ALLOWED_PATHS": "/opt/aigateway/workspaces"
    }
}

await opencode_client.add_mcp_server("filesystem", mcp_config)
```

### 7.4 MCP 状态监控

```python
async def get_mcp_status(self) -> dict:
    """
    获取所有 MCP 服务状态
    
    GET /mcp
    Returns: { [name]: MCPStatus }
    """
    response = await self.client.get(f"{self.base_url}/mcp")
    response.raise_for_status()
    return response.json()
```

---

## 8. SSE 流式处理

### 8.1 SSE 事件类型

OpenCode Server 提供以下 SSE 事件（参考 [OpenCode Server 文档 - Events](https://opencode.ai/docs/server/)）：

| 事件类型 | 说明 | 数据来源 |
|----------|------|----------|
| `server.connected` | 连接成功 | 首次连接 |
| `message` | 消息事件 | AI 响应 |
| `tool_call` | 工具调用 | AI 调用工具 |
| `tool_result` | 工具结果 | 工具执行完成 |
| `error` | 错误事件 | 系统错误 |

### 8.2 SSE 客户端实现

```python
import asyncio
from httpx import AsyncClient

class SSEClient:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.auth = (username, password)
        self.client = AsyncClient(auth=self.auth, timeout=None)
    
    async def connect(self, path: str = "/event"):
        """建立 SSE 连接"""
        async with self.client.stream(
            "GET", 
            f"{self.base_url}{path}",
            headers={"Accept": "text/event-stream"}
        ) as response:
            response.raise_for_status()
            
            async for line in response.aiter_lines():
                if line.startswith("event: "):
                    event_type = line[7:]
                elif line.startswith("data: "):
                    data = line[6:]
                    yield event_type, data
    
    async def subscribe_events(self):
        """订阅所有事件"""
        async for event_type, data in self.connect():
            print(f"Event: {event_type}, Data: {data}")
```

### 8.3 网关层 SSE 代理

```python
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio
import json

app = FastAPI()

@app.post("/api/v1/chat/stream")
async def chat_stream(request: Request):
    """
    SSE 流式对话接口
    
    1. 接收前端请求
    2. 建立与 OpenCode Server 的 SSE 连接
    3. 双向转发事件
    """
    body = await request.json()
    session_id = body.get("session_id")
    message = body.get("message")
    
    # 获取或创建 OpenCode 会话
    opencode_session = await get_or_create_opencode_session(session_id)
    
    async def event_generator():
        try:
            # 建立 SSE 连接
            async with opencode_client.connect("/event") as events:
                # 发送用户消息
                await opencode_client.send_message_async(
                    opencode_session["id"],
                    message
                )
                
                # 转发事件
                async for event_type, data in events:
                    # 转换事件格式
                    formatted_event = format_event(event_type, data)
                    
                    # 发送 SSE 事件
                    yield f"event: {formatted_event['type']}\n"
                    yield f"data: {json.dumps(formatted_event['data'])}\n\n"
                    
                    # 结束标记
                    if formatted_event['type'] == 'done':
                        break
                        
        except Exception as e:
            yield f"event: error\n"
            yield f"data: {json.dumps({'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

def format_event(event_type: str, data: str) -> dict:
    """转换 OpenCode 事件为网关层格式"""
    event_map = {
        "server.connected": {"type": "connected", "data": {}},
        "message": {"type": "message", "data": json.loads(data)},
        "tool_call": {"type": "tool_call", "data": json.loads(data)},
        "tool_result": {"type": "tool_result", "data": json.loads(data)},
    }
    
    return event_map.get(event_type, {"type": "unknown", "data": {}})
```

### 8.4 SSE 连接管理

```python
import asyncio
from collections import defaultdict

class SSEConnectionManager:
    def __init__(self):
        self.connections = defaultdict(list)  # session_id -> [queues]
        self.heartbeat_interval = 30  # 心跳间隔（秒）
    
    async def connect(self, session_id: str) -> asyncio.Queue:
        """建立 SSE 连接"""
        queue = asyncio.Queue()
        self.connections[session_id].append(queue)
        
        # 启动心跳
        asyncio.create_task(self._heartbeat(session_id, queue))
        
        return queue
    
    async def disconnect(self, session_id: str, queue: asyncio.Queue):
        """断开 SSE 连接"""
        if session_id in self.connections:
            self.connections[session_id].remove(queue)
            if not self.connections[session_id]:
                del self.connections[session_id]
    
    async def broadcast(self, session_id: str, event: dict):
        """广播事件到所有连接"""
        if session_id in self.connections:
            for queue in self.connections[session_id]:
                await queue.put(event)
    
    async def _heartbeat(self, session_id: str, queue: asyncio.Queue):
        """心跳保活"""
        while session_id in self.connections and queue in self.connections[session_id]:
            await queue.put({"type": "heartbeat", "data": {"timestamp": datetime.now().isoformat()}})
            await asyncio.sleep(self.heartbeat_interval)
```

---

## 9. 错误处理与重试

### 9.1 错误分类

| 错误类型 | 说明 | 处理策略 |
|----------|------|----------|
| **连接错误** | 无法连接到 OpenCode Server | 指数退避重试，最大 3 次 |
| **超时错误** | 请求超时 | 返回友好提示，前端重试 |
| **认证错误** | Basic Auth 失败 | 记录日志，告警通知 |
| **业务错误** | 会话不存在等 | 返回具体错误信息 |
| **SSE 断开** | 连接意外断开 | 自动重连，恢复上下文 |

### 9.2 重试策略

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

class OpenCodeClient:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.auth = (username, password)
        self.client = httpx.AsyncClient(auth=self.auth)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=lambda e: isinstance(e, (httpx.ConnectError, httpx.TimeoutException))
    )
    async def request_with_retry(self, method: str, path: str, **kwargs) -> dict:
        """带重试的 HTTP 请求"""
        response = await self.client.request(
            method,
            f"{self.base_url}{path}",
            **kwargs
        )
        response.raise_for_status()
        return response.json()
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            response = await self.client.get(
                f"{self.base_url}/global/health",
                timeout=5.0
            )
            return response.status_code == 200
        except Exception:
            return False
```

### 9.3 降级策略

```python
class OpenCodeFallback:
    def __init__(self, client: OpenCodeClient):
        self.client = client
        self.fallback_messages = {
            "server_unavailable": "AI 服务暂时不可用，请稍后重试。",
            "rate_limited": "请求过于频繁，请稍后再试。",
            "quota_exceeded": "您的 Token 配额已用完，请联系管理员。"
        }
    
    async def send_message_with_fallback(
        self,
        session_id: str,
        message: str
    ) -> AsyncGenerator[dict, None]:
        """发送消息，带降级处理"""
        try:
            # 检查 OpenCode Server 健康状态
            if not await self.client.health_check():
                yield {
                    "type": "error",
                    "data": {
                        "message": self.fallback_messages["server_unavailable"]
                    }
                }
                return
            
            # 正常发送消息
            async for event in self.client.stream_message(session_id, message):
                yield event
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                yield {
                    "type": "error",
                    "data": {
                        "message": self.fallback_messages["rate_limited"]
                    }
                }
            else:
                yield {
                    "type": "error",
                    "data": {
                        "message": f"服务异常: {e.response.status_code}"
                    }
                }
        except Exception as e:
            yield {
                "type": "error",
                "data": {
                    "message": f"未知错误: {str(e)}"
                }
            }
```

---

## 10. 性能优化

### 10.1 连接池优化

```python
import httpx

# 配置连接池
limits = httpx.Limits(
    max_keepalive_connections=50,
    max_connections=200
)

# 配置超时
timeout = httpx.Timeout(
    connect=5.0,
    read=300.0,  # SSE 连接需要长超时
    write=10.0,
    pool=5.0
)

client = httpx.AsyncClient(
    auth=("gateway", "password"),
    limits=limits,
    timeout=timeout,
    http2=True,
    http1=True
)
```

### 10.2 缓存策略

```python
import aioredis
from functools import wraps

class OpenCodeCache:
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.ttl = 300  # 5 分钟缓存
    
    async def get_agent_list(self) -> list[dict]:
        """获取 Agent 列表（带缓存）"""
        cache_key = "opencode:agents"
        
        # 尝试从缓存获取
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # 从 OpenCode Server 获取
        agents = await opencode_client.list_agents()
        
        # 写入缓存
        await self.redis.setex(
            cache_key,
            self.ttl,
            json.dumps(agents)
        )
        
        return agents
    
    async def invalidate_agent_cache(self):
        """使 Agent 缓存失效"""
        await self.redis.delete("opencode:agents")
```

### 10.3 批量操作

```python
async def batch_delete_sessions(self, session_ids: list[str]) -> list[bool]:
    """批量删除会话"""
    tasks = [
        self.delete_opencode_session(session_id)
        for session_id in session_ids
    ]
    
    # 并发执行，限制并发数
    semaphore = asyncio.Semaphore(10)
    
    async def delete_with_limit(session_id: str):
        async with semaphore:
            return await self.delete_opencode_session(session_id)
    
    results = await asyncio.gather(*[
        delete_with_limit(sid)
        for sid in session_ids
    ], return_exceptions=True)
    
    return [
        result if not isinstance(result, Exception) else False
        for result in results
    ]
```

---

## 11. 监控与健康检查

### 11.1 健康检查端点

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class HealthStatus(BaseModel):
    status: str
    version: str
    components: dict[str, str]

@app.get("/health")
async def health_check() -> HealthStatus:
    """系统健康检查"""
    components = {}
    
    # 检查 OpenCode Server
    try:
        opencode_healthy = await opencode_client.health_check()
        components["opencode"] = "healthy" if opencode_healthy else "unhealthy"
    except Exception as e:
        components["opencode"] = f"error: {str(e)}"
    
    # 检查 Redis
    try:
        await redis_client.ping()
        components["redis"] = "healthy"
    except Exception as e:
        components["redis"] = f"error: {str(e)}"
    
    # 检查 PostgreSQL
    try:
        await db.execute("SELECT 1")
        components["database"] = "healthy"
    except Exception as e:
        components["database"] = f"error: {str(e)}"
    
    overall = "healthy" if all(
        v == "healthy" for v in components.values()
    ) else "degraded"
    
    return HealthStatus(
        status=overall,
        version="1.0.0",
        components=components
    )
```

### 11.2 指标采集

```python
from prometheus_client import Counter, Histogram, Gauge

# 定义指标
opencode_requests_total = Counter(
    'opencode_requests_total',
    'Total requests to OpenCode Server',
    ['method', 'endpoint', 'status']
)

opencode_request_duration = Histogram(
    'opencode_request_duration_seconds',
    'Request duration to OpenCode Server',
    ['method', 'endpoint']
)

opencode_active_connections = Gauge(
    'opencode_active_connections',
    'Active SSE connections to OpenCode Server'
)

class MetricsMiddleware:
    async def __call__(self, request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        
        opencode_requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        opencode_request_duration.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        return response
```

---

## 12. 代码示例

### 12.1 完整 OpenCode 客户端

```python
import httpx
import asyncio
from typing import AsyncGenerator, Optional
from pydantic import BaseModel

class OpenCodeConfig(BaseModel):
    base_url: str = "http://127.0.0.1:4096"
    username: str = "gateway"
    password: str
    timeout: float = 60.0

class OpenCodeClient:
    def __init__(self, config: OpenCodeConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            auth=(config.username, config.password),
            timeout=httpx.Timeout(config.timeout),
            http2=True
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    # === 全局 API ===
    
    async def health_check(self) -> dict:
        """GET /global/health"""
        response = await self.client.get(f"{self.config.base_url}/global/health")
        response.raise_for_status()
        return response.json()
    
    # === 会话 API ===
    
    async def create_session(self, title: Optional[str] = None) -> dict:
        """POST /session"""
        payload = {}
        if title:
            payload["title"] = title
        
        response = await self.client.post(
            f"{self.config.base_url}/session",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def list_sessions(self) -> list[dict]:
        """GET /session"""
        response = await self.client.get(f"{self.config.base_url}/session")
        response.raise_for_status()
        return response.json()
    
    async def get_session(self, session_id: str) -> dict:
        """GET /session/{id}"""
        response = await self.client.get(
            f"{self.config.base_url}/session/{session_id}"
        )
        response.raise_for_status()
        return response.json()
    
    async def delete_session(self, session_id: str) -> bool:
        """DELETE /session/{id}"""
        response = await self.client.delete(
            f"{self.config.base_url}/session/{session_id}"
        )
        response.raise_for_status()
        return response.json()
    
    # === 消息 API ===
    
    async def send_message(
        self,
        session_id: str,
        content: str,
        agent: Optional[str] = None
    ) -> dict:
        """POST /session/{id}/message"""
        payload = {
            "parts": [{"type": "text", "text": content}]
        }
        if agent:
            payload["agent"] = agent
        
        response = await self.client.post(
            f"{self.config.base_url}/session/{session_id}/message",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def send_message_async(
        self,
        session_id: str,
        content: str,
        agent: Optional[str] = None
    ) -> None:
        """POST /session/{id}/prompt_async"""
        payload = {
            "parts": [{"type": "text", "text": content}]
        }
        if agent:
            payload["agent"] = agent
        
        response = await self.client.post(
            f"{self.config.base_url}/session/{session_id}/prompt_async",
            json=payload
        )
        response.raise_for_status()
    
    async def get_messages(self, session_id: str) -> list[dict]:
        """GET /session/{id}/message"""
        response = await self.client.get(
            f"{self.config.base_url}/session/{session_id}/message"
        )
        response.raise_for_status()
        return response.json()
    
    # === SSE API ===
    
    async def stream_events(self) -> AsyncGenerator[tuple[str, str], None]:
        """GET /event"""
        async with self.client.stream(
            "GET",
            f"{self.config.base_url}/event",
            headers={"Accept": "text/event-stream"}
        ) as response:
            response.raise_for_status()
            
            event_type = ""
            async for line in response.aiter_lines():
                if line.startswith("event: "):
                    event_type = line[7:]
                elif line.startswith("data: "):
                    data = line[6:]
                    yield event_type, data
    
    # === Agent API ===
    
    async def list_agents(self) -> list[dict]:
        """GET /agent"""
        response = await self.client.get(f"{self.config.base_url}/agent")
        response.raise_for_status()
        return response.json()
    
    # === MCP API ===
    
    async def add_mcp(self, name: str, config: dict) -> dict:
        """POST /mcp"""
        response = await self.client.post(
            f"{self.config.base_url}/mcp",
            json={"name": name, "config": config}
        )
        response.raise_for_status()
        return response.json()
    
    async def list_mcp(self) -> dict:
        """GET /mcp"""
        response = await self.client.get(f"{self.config.base_url}/mcp")
        response.raise_for_status()
        return response.json()


# 使用示例
async def main():
    config = OpenCodeConfig(password="YOUR_PASSWORD")
    
    async with OpenCodeClient(config) as client:
        # 健康检查
        health = await client.health_check()
        print(f"Health: {health}")
        
        # 创建会话
        session = await client.create_session("Test Session")
        print(f"Session: {session['id']}")
        
        # 发送消息
        response = await client.send_message(
            session["id"],
            "Hello, OpenCode!",
            agent="build"
        )
        print(f"Response: {response}")
        
        # 订阅事件
        async for event_type, data in client.stream_events():
            print(f"Event: {event_type}, Data: {data}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 12.2 网关层集成示例

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio

app = FastAPI()

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    agent_id: str = "default"
    attachments: list[dict] = []

@app.post("/api/v1/chat/stream")
async def chat_stream(request: ChatRequest, user: User = Depends(get_current_user)):
    """SSE 流式对话"""
    
    # 1. 获取或创建会话
    if request.session_id:
        session = await session_manager.get_session(request.session_id)
        if not session or session.user_id != user.id:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = await session_manager.create_session(
            user_id=user.id,
            agent_id=request.agent_id
        )
    
    # 2. 获取 OpenCode 会话映射
    opencode_session_id = session.opencode_session_id
    if not opencode_session_id:
        # 创建 OpenCode 会话
        opencode_session = await opencode_client.create_session(session.title)
        opencode_session_id = opencode_session["id"]
        await session_manager.update_opencode_session_id(
            session.id,
            opencode_session_id
        )
    
    # 3. 发送消息并流式返回
    async def event_generator():
        try:
            # 发送异步消息
            await opencode_client.send_message_async(
                opencode_session_id,
                request.message,
                agent=request.agent_id
            )
            
            # 订阅事件流
            async for event_type, data in opencode_client.stream_events():
                event_data = json.loads(data)
                
                # 转换并转发事件
                yield f"event: {event_type}\n"
                yield f"data: {json.dumps(event_data)}\n\n"
                
                # 保存消息到数据库
                if event_type == "message":
                    await message_manager.save_message(
                        session_id=session.id,
                        role="assistant",
                        content=event_data.get("content", ""),
                        metadata=event_data
                    )
                
                # 结束标记
                if event_type == "done":
                    break
                    
        except Exception as e:
            yield f"event: error\n"
            yield f"data: {json.dumps({'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

---

**文档结束**
