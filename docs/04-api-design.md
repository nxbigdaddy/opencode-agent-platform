# 04 - API 接口设计文档

**项目名称**：AI Agent 对话平台  
**版本**：v1.0  
**日期**：2026-04-21  
**协议**：HTTP/1.1, HTTP/2  
**格式**：JSON  
**认证**：JWT (Bearer Token)  
**编写人**：AI Agent 团队  
**目标读者**：前端开发、后端开发、测试团队、API 消费者

---

## 目录

1. [接口规范](#1-接口规范)
2. [认证模块](#2-认证模块)
3. [用户模块](#3-用户模块)
4. [会话模块](#4-会话模块)
5. [对话模块](#5-对话模块)
6. [Agent 模块](#6-agent-模块)
7. [MCP 模块](#7-mcp-模块)
8. [管理后台模块](#8-管理后台模块)
9. [Webhook 模块](#9-webhook-模块)
10. [错误码定义](#10-错误码定义)
11. [OpenCode Server API 映射](#11-opencode-server-api-映射)

---

## 1. 接口规范

### 1.1 基础信息

| 属性 | 值 |
|------|-----|
| **Base URL** | `https://api.aigateway.example.com/api/v1` |
| **Content-Type** | `application/json` |
| **字符编码** | UTF-8 |
| **时间格式** | ISO 8601 (RFC 3339) |
| **日期格式** | `YYYY-MM-DD` |

### 1.2 请求规范

#### 1.2.1 认证头

```http
Authorization: Bearer <eyJhbGciOiJIUzI1NiIs...XVCJ9...
```

#### 1.2.2 分页参数

```http
GET /api/v1/sessions?page=1&page_size=20
```

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `page` | integer | 否 | 1 | 页码，从 1 开始 |
| `page_size` | integer | 否 | 20 | 每页数量，最大 100 |

#### 1.2.3 排序参数

```http
GET /api/v1/sessions?sort=-created_at&sort=title
```

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `sort` | string | 否 | -created_at | 排序字段，`-` 前缀表示降序 |

### 1.3 响应规范

#### 1.3.1 成功响应

```json
{
  "code": 0,
  "message": "success",
  "data": { ... },
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

#### 1.3.2 错误响应

```json
{
  "code": 1001,
  "message": "Invalid credentials",
  "details": {
    "field": "password",
    "error": "Password must be at least 8 characters"
  }
}
```

#### 1.3.3 SSE 响应格式

```
event: message
data: {"type": "thinking", "content": "..."}

event: tool_call
data: {"type": "tool_call", "tool": "read_file", "args": {"path": "/workspace/main.py"}}

event: tool_result
data: {"type": "tool_result", "tool": "read_file", "result": "..."}

event: message
data: {"type": "text", "content": "最终回复内容"}

event: done
data: {"type": "done", "usage": {"prompt_tokens": 100, "completion_tokens": 200}}
```

---

## 2. 认证模块

### 2.1 用户注册

**Endpoint**：`POST /auth/register`

**请求**：

```json
{
  "username": "john_doe",
  "password": "SecureP@ss123",
  "email": "john@example.com",
  "invite_code": "INV-2026-XXXX"
}
```

**字段说明**：

| 字段 | 类型 | 必填 | 规则 |
|------|------|------|------|
| `username` | string | 是 | 3-50 字符，字母数字下划线 |
| `password` | string | 是 | 8-100 字符，至少包含大小写字母和数字 |
| `email` | string | 否 | 有效邮箱格式 |
| `invite_code` | string | 是 | 有效的邀请码 |

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "created_at": "2026-04-21T10:30:00Z"
  }
}
```

### 2.2 用户登录

**Endpoint**：`POST /auth/login`

**请求**：

```json
{
  "username": "john_doe",
  "password": "SecureP@ss123",
  "remember_me": true
}
```

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 900,
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "john_doe",
      "display_name": "John Doe",
      "role": "user",
      "avatar_url": "https://..."
    }
  }
}
```

### 2.3 Token 刷新

**Endpoint**：`POST /auth/refresh`

**请求**：

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 900
  }
}
```

### 2.4 用户登出

**Endpoint**：`POST /auth/logout`

**请求头**：`Authorization: Bearer <access_token>`

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": null
}
```

### 2.5 OAuth 登录（企业微信）

**Endpoint**：`GET /auth/oauth/wechat`

**查询参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `code` | string | 是 | 企业微信授权码 |
| `state` | string | 是 | CSRF 防护状态码 |

**响应**：重定向至前端回调页面，携带 Token

```
https://app.aigateway.example.com/auth/callback?access_token=YOUR_SECRET
```

---

## 3. 用户模块

### 3.1 获取当前用户信息

**Endpoint**：`GET /users/me`

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john@example.com",
    "display_name": "John Doe",
    "avatar_url": "https://...",
    "role": "user",
    "quota": {
      "daily_token_limit": 100000,
      "daily_token_used": 15000,
      "monthly_token_limit": 2000000,
      "monthly_token_used": 150000
    },
    "created_at": "2026-04-21T10:30:00Z"
  }
}
```

### 3.2 更新用户信息

**Endpoint**：`PATCH /users/me`

**请求**：

```json
{
  "display_name": "John Updated",
  "email": "john.new@example.com",
  "avatar_url": "https://new-avatar.jpg"
}
```

### 3.3 修改密码

**Endpoint**：`POST /users/me/password`

**请求**：

```json
{
  "old_password": "OldP@ss123",
  "new_password": "NewP@ss456"
}
```

### 3.4 获取用户用量统计

**Endpoint**：`GET /users/me/usage`

**查询参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `start_date` | string | 否 | 7 天前 | 开始日期 |
| `end_date` | string | 否 | 今天 | 结束日期 |

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "daily_stats": [
      {
        "date": "2026-04-20",
        "session_count": 5,
        "message_count": 50,
        "tokens_input": 5000,
        "tokens_output": 8000,
        "estimated_cost": 0.5
      }
    ],
    "summary": {
      "total_sessions": 20,
      "total_messages": 200,
      "total_tokens": 50000,
      "total_cost": 3.5
    }
  }
}
```

---

## 4. 会话模块

### 4.1 创建会话

**Endpoint**：`POST /sessions`

**请求**：

```json
{
  "title": "Python 项目开发",
  "agent_id": "550e8400-e29b-41d4-a716-446655440001",
  "metadata": {
    "source": "web",
    "project": "my-project"
  }
}
```

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "title": "Python 项目开发",
    "agent": {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "build",
      "description": "默认开发 Agent"
    },
    "workspace_path": "/opt/aigateway/workspaces/550e8400/550e8400-e29b-41d4-a716-446655440002",
    "status": "active",
    "message_count": 0,
    "created_at": "2026-04-21T10:30:00Z",
    "updated_at": "2026-04-21T10:30:00Z"
  }
}
```

### 4.2 获取会话列表

**Endpoint**：`GET /sessions`

**查询参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `status` | string | 否 | active | 状态筛选：active, archived, all |
| `search` | string | 否 | - | 标题搜索关键词 |
| `agent_id` | string | 否 | - | Agent ID 筛选 |
| `page` | integer | 否 | 1 | 页码 |
| `page_size` | integer | 否 | 20 | 每页数量 |
| `sort` | string | 否 | -updated_at | 排序字段 |

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "title": "Python 项目开发",
        "agent": {
          "id": "...",
          "name": "build"
        },
        "message_count": 15,
        "last_message_at": "2026-04-21T12:00:00Z",
        "status": "active",
        "created_at": "2026-04-21T10:30:00Z"
      }
    ],
    "meta": {
      "page": 1,
      "page_size": 20,
      "total": 50,
      "total_pages": 3
    }
  }
}
```

### 4.3 获取会话详情

**Endpoint**：`GET /sessions/{session_id}`

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "title": "Python 项目开发",
    "agent": {
      "id": "...",
      "name": "build",
      "description": "默认开发 Agent"
    },
    "workspace_path": "/opt/aigateway/workspaces/...",
    "status": "active",
    "message_count": 15,
    "total_tokens_used": 15000,
    "summary": "这是一个关于 Python 项目开发的会话...",
    "metadata": {},
    "created_at": "2026-04-21T10:30:00Z",
    "updated_at": "2026-04-21T12:00:00Z"
  }
}
```

### 4.4 更新会话

**Endpoint**：`PATCH /sessions/{session_id}`

**请求**：

```json
{
  "title": "更新后的标题",
  "agent_id": "new-agent-id"
}
```

### 4.5 删除会话

**Endpoint**：`DELETE /sessions/{session_id}`

**查询参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `force` | boolean | 否 | false | 是否强制删除（跳过确认） |

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "deleted_at": "2026-04-21T12:30:00Z"
  }
}
```

### 4.6 归档会话

**Endpoint**：`POST /sessions/{session_id}/archive`

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "status": "archived",
    "archived_at": "2026-04-21T12:30:00Z"
  }
}
```

### 4.7 恢复会话

**Endpoint**：`POST /sessions/{session_id}/restore`

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "status": "active",
    "archived_at": null
  }
}
```

---

## 5. 对话模块

### 5.1 发送消息（SSE 流式）

**Endpoint**：`POST /chat/stream`

**Content-Type**：`application/json`

**Accept**：`text/event-stream`

**请求**：

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440002",
  "message": "帮我写一个 Python 函数，计算斐波那契数列",
  "agent_id": "build",
  "attachments": [
    {
      "name": "requirements.txt",
      "content": "flask==2.3.0\nnumpy==1.24.0",
      "type": "text/plain"
    }
  ],
  "context_window": 10
}
```

**字段说明**：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `session_id` | string | 否 | null | 会话 ID，为空则新建会话 |
| `message` | string | 是 | - | 用户消息内容 |
| `agent_id` | string | 否 | "default" | 指定 Agent |
| `attachments` | array | 否 | [] | 文件附件 |
| `context_window` | integer | 否 | 10 | 携带历史轮数 |

**SSE 响应**：

```
event: message
data: {"type": "thinking", "content": "用户要求写一个计算斐波那契数列的 Python 函数..."}

event: tool_call
data: {"type": "tool_call", "tool": "write", "args": {"path": "/workspace/fibonacci.py", "content": "..."}}

event: tool_result
data: {"type": "tool_result", "tool": "write", "result": "File created successfully"}

event: message
data: {"type": "text", "content": "我已经为你创建了一个计算斐波那契数列的 Python 函数..."}

event: done
data: {"type": "done", "usage": {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300}}
```

### 5.2 获取消息列表

**Endpoint**：`GET /sessions/{session_id}/messages`

**查询参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `before_id` | string | 否 | - | 获取此 ID 之前的消息（向上翻页） |
| `after_id` | string | 否 | - | 获取此 ID 之后的消息（向下翻页） |
| `limit` | integer | 否 | 20 | 返回数量，最大 100 |
| `role` | string | 否 | - | 角色筛选：user, assistant, tool |

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "msg-001",
        "role": "user",
        "content": "帮我写一个 Python 函数",
        "parts": [{"type": "text", "text": "帮我写一个 Python 函数"}],
        "created_at": "2026-04-21T10:30:00Z"
      },
      {
        "id": "msg-002",
        "role": "assistant",
        "content": "我已经为你创建了一个计算斐波那契数列的 Python 函数...",
        "parts": [
          {"type": "text", "text": "我已经为你创建了一个计算斐波那契数列的 Python 函数..."},
          {"type": "code", "language": "python", "code": "def fibonacci(n):\n    ..."}
        ],
        "tool_calls": [
          {
            "name": "write",
            "arguments": {"path": "/workspace/fibonacci.py"},
            "result": "File created successfully",
            "status": "success",
            "duration_ms": 100
          }
        ],
        "tokens_input": 100,
        "tokens_output": 200,
        "latency_ms": 5000,
        "created_at": "2026-04-21T10:30:05Z"
      }
    ],
    "has_more": true
  }
}
```

### 5.3 重新生成回复

**Endpoint**：`POST /messages/{message_id}/regenerate`

**请求**：

```json
{
  "model": "anthropic/claude-opus-4-20250514"
}
```

**响应**：SSE 流（同发送消息）

### 5.4 删除消息

**Endpoint**：`DELETE /messages/{message_id}`

**说明**：仅支持删除用户自己发送的消息，且不能删除已产生后续回复的消息。

---

## 6. Agent 模块

### 6.1 获取 Agent 列表

**Endpoint**：`GET /agents`

**查询参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `mode` | string | 否 | - | 筛选：primary, subagent |
| `search` | string | 否 | - | 名称/描述搜索 |
| `include_builtin` | boolean | 否 | true | 是否包含内置 Agent |

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "...",
        "name": "build",
        "description": "默认开发 Agent，拥有所有工具权限",
        "mode": "primary",
        "color": "#3b82f6",
        "is_builtin": true,
        "model": "anthropic/claude-sonnet-4-20250514",
        "tools": [
          {"name": "read", "permission": "allow"},
          {"name": "write", "permission": "allow"},
          {"name": "bash", "permission": "ask"}
        ]
      }
    ]
  }
}
```

### 6.2 获取 Agent 详情

**Endpoint**：`GET /agents/{agent_id}`

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "...",
    "name": "code-reviewer",
    "description": "代码审查 Agent",
    "mode": "subagent",
    "system_prompt": "You are a code reviewer. Focus on security, performance...",
    "model_config": {
      "model": "anthropic/claude-sonnet-4-20250514",
      "temperature": 0.1,
      "max_steps": 20
    },
    "tools_config": [
      {"name": "read", "permission": "allow"},
      {"name": "write", "permission": "deny"}
    ],
    "created_by": {
      "id": "...",
      "username": "john_doe"
    },
    "created_at": "2026-04-21T10:30:00Z"
  }
}
```

### 6.3 创建自定义 Agent

**Endpoint**：`POST /agents`

**请求**：

```json
{
  "name": "security-auditor",
  "description": "安全审计 Agent",
  "mode": "subagent",
  "system_prompt": "You are a security expert...",
  "model_config": {
    "model": "anthropic/claude-sonnet-4-20250514",
    "temperature": 0.1,
    "max_steps": 30
  },
  "tools_config": [
    {"name": "read", "permission": "allow"},
    {"name": "grep", "permission": "allow"},
    {"name": "write", "permission": "deny"},
    {"name": "bash", "permission": "deny"}
  ],
  "color": "#ef4444"
}
```

### 6.4 更新 Agent

**Endpoint**：`PATCH /agents/{agent_id}`

**请求**：

```json
{
  "description": "更新后的描述",
  "system_prompt": "更新后的提示词...",
  "tools_config": [
    {"name": "read", "permission": "allow"}
  ]
}
```

### 6.5 删除 Agent

**Endpoint**：`DELETE /agents/{agent_id}`

**说明**：
- 内置 Agent 不可删除
- 删除前需确认没有活跃会话正在使用该 Agent

---

## 7. MCP 模块

### 7.1 获取 MCP 服务列表

**Endpoint**：`GET /mcp`

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "...",
        "name": "filesystem",
        "description": "文件系统操作",
        "type": "local",
        "status": "active",
        "tools": [
          {
            "name": "read_file",
            "description": "读取文件内容",
            "parameters": {
              "type": "object",
              "properties": {
                "path": {"type": "string", "description": "文件路径"}
              }
            }
          }
        ]
      }
    ]
  }
}
```

### 7.2 注册 MCP 服务

**Endpoint**：`POST /mcp`

**Local MCP 请求**：

```json
{
  "name": "sqlite",
  "description": "SQLite 数据库查询",
  "type": "local",
  "command": ["python", "-m", "mcp_sqlite", "/workspace/data.db"],
  "environment": {
    "DB_PATH": "/workspace/data.db"
  },
  "permissions": {
    "query": "allow",
    "execute": "ask"
  },
  "timeout": 10000
}
```

**Remote MCP 请求**：

```json
{
  "name": "company-api",
  "description": "公司内部 API",
  "type": "remote",
  "endpoint": "https://internal-api.example.com/mcp",
  "headers": {
    "Authorization": "Bearer {env:API_KEY}"
  },
  "permissions": {
    "*": "ask"
  }
}
```

### 7.3 获取 MCP 详情

**Endpoint**：`GET /mcp/{mcp_id}`

### 7.4 更新 MCP 配置

**Endpoint**：`PATCH /mcp/{mcp_id}`

### 7.5 删除 MCP 服务

**Endpoint**：`DELETE /mcp/{mcp_id}`

### 7.6 MCP 健康检查

**Endpoint**：`POST /mcp/{mcp_id}/health-check`

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "status": "healthy",
    "latency_ms": 50,
    "last_check": "2026-04-21T12:00:00Z"
  }
}
```

---

## 8. 管理后台模块

### 8.1 用户管理

#### 8.1.1 获取用户列表

**Endpoint**：`GET /admin/users`

**查询参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `role` | string | 否 | - | 角色筛选 |
| `status` | string | 否 | - | 状态筛选 |
| `search` | string | 否 | - | 用户名/邮箱搜索 |
| `page` | integer | 否 | 1 | 页码 |
| `page_size` | integer | 否 | 20 | 每页数量 |

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "...",
        "username": "john_doe",
        "email": "john@example.com",
        "display_name": "John Doe",
        "role": "user",
        "status": "active",
        "last_login_at": "2026-04-21T10:00:00Z",
        "session_count": 10,
        "total_tokens_used": 50000,
        "created_at": "2026-04-01T00:00:00Z"
      }
    ],
    "meta": {
      "page": 1,
      "page_size": 20,
      "total": 100
    }
  }
}
```

#### 8.1.2 创建用户

**Endpoint**：`POST /admin/users`

#### 8.1.3 更新用户

**Endpoint**：`PATCH /admin/users/{user_id}`

#### 8.1.4 禁用用户

**Endpoint**：`POST /admin/users/{user_id}/suspend`

#### 8.1.5 重置密码

**Endpoint**：`POST /admin/users/{user_id}/reset-password`

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "temporary_password": "TempP@ss123"
  }
}
```

### 8.2 用量统计

#### 8.2.1 系统用量概览

**Endpoint**：`GET /admin/usage/overview`

**查询参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `period` | string | 否 | 7d | 统计周期：1d, 7d, 30d, 90d |

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "period": "7d",
    "active_users": 150,
    "total_sessions": 500,
    "total_messages": 5000,
    "total_tokens": 500000,
    "total_cost": 50.0,
    "daily_trend": [
      {
        "date": "2026-04-20",
        "users": 80,
        "sessions": 100,
        "messages": 1000,
        "tokens": 100000
      }
    ],
    "top_users": [
      {
        "user_id": "...",
        "username": "john_doe",
        "tokens_used": 50000
      }
    ]
  }
}
```

#### 8.2.2 模型调用分布

**Endpoint**：`GET /admin/usage/models`

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "models": [
      {
        "model": "anthropic/claude-sonnet-4-20250514",
        "call_count": 1000,
        "tokens_input": 100000,
        "tokens_output": 200000,
        "percentage": 60.0
      }
    ]
  }
}
```

### 8.3 审计日志

#### 8.3.1 查询审计日志

**Endpoint**：`GET /admin/audit-logs`

**查询参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `user_id` | string | 否 | - | 用户 ID |
| `action` | string | 否 | - | 操作类型 |
| `resource_type` | string | 否 | - | 资源类型 |
| `start_date` | string | 否 | - | 开始日期 |
| `end_date` | string | 否 | - | 结束日期 |
| `page` | integer | 否 | 1 | 页码 |
| `page_size` | integer | 否 | 50 | 每页数量 |

#### 8.3.2 导出审计日志

**Endpoint**：`POST /admin/audit-logs/export`

**请求**：

```json
{
  "format": "csv",
  "start_date": "2026-04-01",
  "end_date": "2026-04-21",
  "filters": {
    "action": "login"
  }
}
```

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "download_url": "https://api.aigateway.example.com/exports/audit-20260421.csv",
    "expires_at": "2026-04-21T13:00:00Z"
  }
}
```

### 8.4 系统配置

#### 8.4.1 获取配置

**Endpoint**：`GET /admin/configs`

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "configs": [
      {
        "key": "default_model",
        "value": "anthropic/claude-sonnet-4-20250514",
        "description": "默认 LLM 模型"
      }
    ]
  }
}
```

#### 8.4.2 更新配置

**Endpoint**：`PUT /admin/configs/{key}`

**请求**：

```json
{
  "value": "anthropic/claude-opus-4-20250514",
  "description": "默认 LLM 模型"
}
```

---

## 9. Webhook 模块

### 9.1 企业微信消息推送

**Endpoint**：`POST /webhooks/wechat`

**请求头**：

```http
Content-Type: application/json
X-Wechat-Signature: sha1=...
```

**请求体**（企业微信格式）：

```json
{
  "msgtype": "text",
  "text": {
    "content": "@机器人 帮我写个 Python 函数"
  },
  "user_id": "wechat-user-id"
}
```

**响应**：

```json
{
  "msgtype": "markdown",
  "markdown": {
    "content": "**AI 回复**\n\n我已经为你写好了..."
  }
}
```

### 9.2 钉钉消息推送

**Endpoint**：`POST /webhooks/dingtalk`

**请求头**：

```http
Content-Type: application/json
X-Dingtalk-Signature: ...
```

**请求体**（钉钉格式）：

```json
{
  "msgtype": "text",
  "text": {
    "content": "@机器人 帮我写个 Python 函数"
  },
  "senderStaffId": "ding-user-id"
}
```

---

## 10. 错误码定义

### 10.1 通用错误码

| 错误码 | 错误信息 | HTTP 状态码 | 说明 |
|--------|----------|-------------|------|
| 0 | success | 200 | 成功 |
| 1 | unknown error | 500 | 未知错误 |
| 2 | service unavailable | 503 | 服务不可用 |

### 10.2 认证错误码

| 错误码 | 错误信息 | HTTP 状态码 | 说明 |
|--------|----------|-------------|------|
| 1001 | invalid credentials | 401 | 用户名或密码错误 |
| 1002 | token expired | 401 | Token 已过期 |
| 1003 | token invalid | 401 | Token 无效 |
| 1004 | permission denied | 403 | 权限不足 |
| 1005 | account locked | 403 | 账号已锁定 |
| 1006 | account inactive | 403 | 账号未激活 |
| 1007 | invite code invalid | 400 | 邀请码无效或已使用 |

### 10.3 请求错误码

| 错误码 | 错误信息 | HTTP 状态码 | 说明 |
|--------|----------|-------------|------|
| 2001 | bad request | 400 | 请求参数错误 |
| 2002 | validation failed | 422 | 参数校验失败 |
| 2003 | resource not found | 404 | 资源不存在 |
| 2004 | resource conflict | 409 | 资源冲突 |
| 2005 | rate limit exceeded | 429 | 请求频率超限 |

### 10.4 业务错误码

| 错误码 | 错误信息 | HTTP 状态码 | 说明 |
|--------|----------|-------------|------|
| 3001 | session not found | 404 | 会话不存在 |
| 3002 | session archived | 400 | 会话已归档 |
| 3003 | agent not found | 404 | Agent 不存在 |
| 3004 | mcp service error | 502 | MCP 服务异常 |
| 3005 | opencode server error | 502 | OpenCode Server 异常 |
| 3006 | quota exceeded | 429 | Token 配额已用完 |
| 3007 | file too large | 413 | 文件过大 |
| 3008 | unsupported file type | 415 | 不支持的文件类型 |

### 10.5 错误响应示例

```json
{
  "code": 2002,
  "message": "Validation failed",
  "details": {
    "errors": [
      {
        "field": "password",
        "message": "Password must be at least 8 characters"
      },
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

---

## 11. OpenCode Server API 映射

### 11.1 映射关系说明

网关层将前端请求映射到 OpenCode Server API（参考 [OpenCode Server 文档](https://opencode.ai/docs/server/)）。

### 11.2 会话管理映射

| 网关 API | OpenCode API | 说明 |
|----------|--------------|------|
| `POST /sessions` | `POST /session` | 创建会话 |
| `GET /sessions` | `GET /session` | 列表（需网关层分页） |
| `GET /sessions/{id}` | `GET /session/{id}` | 详情 |
| `DELETE /sessions/{id}` | `DELETE /session/{id}` | 删除 |
| `PATCH /sessions/{id}` | `PATCH /session/{id}` | 更新 |
| `POST /sessions/{id}/fork` | `POST /session/{id}/fork` | 分叉 |
| `POST /sessions/{id}/share` | `POST /session/{id}/share` | 分享 |
| `DELETE /sessions/{id}/share` | `DELETE /session/{id}/share` | 取消分享 |

### 11.3 消息管理映射

| 网关 API | OpenCode API | 说明 |
|----------|--------------|------|
| `GET /sessions/{id}/messages` | `GET /session/{id}/message` | 消息列表 |
| `POST /chat/stream` | `POST /session/{id}/message` | 发送消息（同步） |
| `POST /chat/async` | `POST /session/{id}/prompt_async` | 异步发送 |
| `POST /messages/{id}/regenerate` | `POST /session/{id}/message` | 重新生成 |

### 11.4 Agent 管理映射

| 网关 API | OpenCode API | 说明 |
|----------|--------------|------|
| `GET /agents` | `GET /agent` | Agent 列表 |
| `GET /agents/{id}` | - | 网关层从数据库查询 |
| `POST /agents` | - | 仅网关层数据库操作 |
| `DELETE /agents/{id}` | - | 仅网关层数据库操作 |

### 11.5 MCP 管理映射

| 网关 API | OpenCode API | 说明 |
|----------|--------------|------|
| `GET /mcp` | `GET /mcp` | MCP 状态 |
| `POST /mcp` | `POST /mcp` | 添加 MCP |
| `GET /mcp/{id}` | - | 网关层查询数据库 |
| `DELETE /mcp/{id}` | - | 网关层操作 |

### 11.6 事件流映射

| 网关 API | OpenCode API | 说明 |
|----------|--------------|------|
| `POST /chat/stream` (SSE) | `GET /event` | 全局事件流 |
| - | `GET /global/event` | 全局事件流 |

> **注意**：OpenCode Server 的 SSE 事件流通过网关层代理转发给前端，网关层负责：
> 1. 建立与 OpenCode Server 的 SSE 连接
> 2. 解析事件类型
> 3. 转换格式（如需）
> 4. 转发给前端 SSE 连接
> 5. 连接断开时自动重连

---

**文档结束**
