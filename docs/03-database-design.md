# 03 - 数据库设计文档

**项目名称**：AI Agent 对话平台  
**版本**：v1.0  
**日期**：2026-04-21  
**数据库**：PostgreSQL 15+  
**编写人**：AI Agent 团队  
**目标读者**：后端开发、DBA、运维团队

---

## 目录

1. [设计概述](#1-设计概述)
2. [命名规范](#2-命名规范)
3. [实体关系图](#3-实体关系图)
4. [表结构设计](#4-表结构设计)
5. [索引设计](#5-索引设计)
6. [分区策略](#6-分区策略)
7. [视图与函数](#7-视图与函数)
8. [数据字典](#8-数据字典)
9. [迁移脚本](#9-迁移脚本)
10. [备份策略](#10-备份策略)

---

## 1. 设计概述

### 1.1 设计目标

- 支持多租户用户隔离
- 支持高并发读写（SSE 流式消息）
- 支持灵活的工具配置（JSONB）
- 支持审计追踪
- 支持数据归档

### 1.2 设计原则

1. **第三范式为主**：减少冗余，保证一致性
2. **JSONB 辅助**：工具配置、元数据等动态字段使用 JSONB
3. **软删除为主**：核心业务表使用 deleted_at 软删除
4. **时间戳必备**：created_at, updated_at 所有表必备
5. **UUID 主键**：使用 gen_random_uuid() 生成主键

### 1.3 容量规划

| 表名 | 预估数据量 | 增长速率 | 存储需求 |
|------|-----------|----------|----------|
| users | 1,000 | 100/月 | 10MB |
| sessions | 100,000 | 10,000/月 | 100MB |
| messages | 10,000,000 | 1,000,000/月 | 10GB |
| agents | 500 | 50/月 | 5MB |
| audit_logs | 50,000,000 | 5,000,000/月 | 50GB |

---

## 2. 命名规范

### 2.1 表命名

- **小写 + 下划线**：`user_profiles`, `chat_sessions`
- **复数形式**：`users`, `sessions`, `messages`
- **避免保留字**：不使用 `user`, `order`, `group` 等

### 2.2 字段命名

- **小写 + 下划线**：`created_at`, `updated_at`
- **外键格式**：`{table}_id`，如 `user_id`, `session_id`
- **布尔值**：`is_{形容词}` 或 `has_{名词}`，如 `is_active`, `is_admin`
- **时间戳**：`{action}_at`，如 `created_at`, `deleted_at`

### 2.3 索引命名

- **主键**：`{table}_pkey`
- **唯一索引**：`{table}_{column}_uniq`
- **普通索引**：`idx_{table}_{column}`
- **复合索引**：`idx_{table}_{col1}_{col2}`

---

## 3. 实体关系图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              实体关系图                                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐         ┌─────────────┐         ┌─────────────────┐
│    users    │         │   agents    │         │   mcp_services  │
├─────────────┤         ├─────────────┤         ├─────────────────┤
│ id (PK)     │◄───────│ created_by  │         │ id (PK)         │
│ username    │         │ id (PK)     │         │ name            │
│ email       │         │ name        │         │ type            │
│ password_hash│        │ description │         │ endpoint        │
│ role        │         │ system_prompt│        │ config          │
│ status      │         │ model_config│         │ status          │
│ quota       │         │ tools_config│         │ created_at      │
│ created_at  │         │ is_builtin  │         └─────────────────┘
│ updated_at  │         │ created_at  │
└──────┬──────┘         └──────┬──────┘
       │                       │
       │    ┌──────────────────┘
       │    │
       ▼    ▼
┌─────────────────────────────────────────────────────────────────┐
│                          sessions                               │
├─────────────────────────────────────────────────────────────────┤
│ id (PK)                                                         │
│ user_id (FK → users.id)                                         │
│ agent_id (FK → agents.id)                                       │
│ title                                                           │
│ workspace_path                                                  │
│ opencode_session_id                                             │
│ status                                                          │
│ metadata                                                        │
│ created_at                                                      │
│ updated_at                                                      │
│ deleted_at                                                      │
└─────────────────────────────────────────────────────────────────┘
       │
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                          messages                               │
├─────────────────────────────────────────────────────────────────┤
│ id (PK)                                                         │
│ session_id (FK → sessions.id)                                   │
│ role                                                            │
│ content                                                         │
│ tool_calls                                                      │
│ tokens_used                                                     │
│ latency_ms                                                      │
│ created_at                                                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        audit_logs                               │
├─────────────────────────────────────────────────────────────────┤
│ id (PK)                                                         │
│ user_id (FK → users.id)                                         │
│ action                                                          │
│ resource_type                                                   │
│ resource_id                                                     │
│ details                                                         │
│ ip_address                                                      │
│ user_agent                                                      │
│ created_at                                                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        usage_stats                              │
├─────────────────────────────────────────────────────────────────┤
│ id (PK)                                                         │
│ user_id (FK → users.id)                                         │
│ date                                                            │
│ session_count                                                   │
│ message_count                                                   │
│ tokens_input                                                    │
│ tokens_output                                                   │
│ cost                                                            │
│ created_at                                                      │
│ updated_at                                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. 表结构设计

### 4.1 用户表 (users)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    avatar_url VARCHAR(500),
    
    -- 角色与权限
    role VARCHAR(20) NOT NULL DEFAULT 'user' 
        CHECK (role IN ('superadmin', 'admin', 'user', 'guest')),
    
    -- 账号状态
    status VARCHAR(20) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'inactive', 'suspended', 'deleted')),
    
    -- 配额限制
    daily_token_quota INTEGER DEFAULT 100000,  -- 每日 Token 上限
    monthly_token_quota INTEGER DEFAULT 2000000, -- 每月 Token 上限
    
    -- 认证相关
    last_login_at TIMESTAMPTZ,
    login_fail_count INTEGER DEFAULT 0,
    locked_until TIMESTAMPTZ,
    
    -- OAuth 绑定
    oauth_provider VARCHAR(50),
    oauth_id VARCHAR(255),
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    
    -- 约束
    CONSTRAINT chk_username_format CHECK (username ~ '^[a-zA-Z0-9_-]{3,50}$'),
    CONSTRAINT chk_email_format CHECK (email IS NULL OR email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

COMMENT ON TABLE users IS '用户表';
COMMENT ON COLUMN users.role IS '角色: superadmin-超级管理员, admin-管理员, user-普通用户, guest-访客';
COMMENT ON COLUMN users.status IS '状态: active-活跃, inactive-未激活, suspended-已禁用, deleted-已删除';
```

### 4.2 Agent 配置表 (agents)

```sql
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    description TEXT,
    
    -- Agent 配置
    system_prompt TEXT NOT NULL,
    model_config JSONB NOT NULL DEFAULT '{}',
    -- 示例: {"model": "anthropic/claude-sonnet-4-20250514", "temperature": 0.3, "max_steps": 50}
    
    tools_config JSONB NOT NULL DEFAULT '[]',
    -- 示例: [{"name": "filesystem", "permission": "allow"}, {"name": "bash", "permission": "ask"}]
    
    -- Agent 属性
    mode VARCHAR(20) NOT NULL DEFAULT 'all'
        CHECK (mode IN ('primary', 'subagent', 'all')),
    color VARCHAR(20),
    is_builtin BOOLEAN NOT NULL DEFAULT FALSE,
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- 归属
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    organization_id UUID,  -- 预留：多组织支持
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    
    -- 约束
    CONSTRAINT chk_agent_name_unique UNIQUE (name, created_by)
);

COMMENT ON TABLE agents IS 'Agent 配置表';
COMMENT ON COLUMN agents.model_config IS '模型配置 JSON: {model, temperature, max_steps, top_p}';
COMMENT ON COLUMN agents.tools_config IS '工具权限配置 JSON 数组';
COMMENT ON COLUMN agents.mode IS '模式: primary-主Agent, subagent-子Agent, all-两者皆可';
```

### 4.3 MCP 服务表 (mcp_services)

```sql
CREATE TABLE mcp_services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    
    -- 连接配置
    type VARCHAR(20) NOT NULL
        CHECK (type IN ('local', 'remote')),
    endpoint VARCHAR(500),  -- remote 时使用 URL
    command JSONB,          -- local 时使用命令和参数 ["npx", "-y", "@modelcontextprotocol/server-filesystem"]
    environment JSONB,      -- 环境变量 {"KEY": "value"}
    headers JSONB,          -- remote 时 HTTP 请求头 {"Authorization": "Bearer xxx"}
    
    -- 状态与健康
    status VARCHAR(20) NOT NULL DEFAULT 'inactive'
        CHECK (status IN ('active', 'inactive', 'error')),
    last_heartbeat_at TIMESTAMPTZ,
    error_message TEXT,
    
    -- 工具定义缓存
    tools_schema JSONB DEFAULT '[]',
    -- 示例: [{"name": "read_file", "description": "...", "inputSchema": {...}}]
    
    -- 权限配置
    permissions JSONB DEFAULT '{}',
    -- 示例: {"read_file": "allow", "write_file": "ask", "delete_file": "deny"}
    
    -- 超时配置
    timeout_ms INTEGER DEFAULT 5000,
    
    -- 创建者
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

COMMENT ON TABLE mcp_services IS 'MCP 服务注册表';
COMMENT ON COLUMN mcp_services.type IS '类型: local-本地命令, remote-远程 URL';
COMMENT ON COLUMN mcp_services.command IS '本地命令配置 JSON 数组';
COMMENT ON COLUMN mcp_services.tools_schema IS '工具定义缓存';
```

### 4.4 会话表 (sessions)

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 关联
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE RESTRICT,
    
    -- 基本信息
    title VARCHAR(200) NOT NULL DEFAULT '新会话',
    summary TEXT,  -- AI 生成的会话摘要
    
    -- 工作区
    workspace_path VARCHAR(500) NOT NULL,
    -- 示例: /opt/aigateway/workspaces/{user_id}/{session_id}/
    
    -- OpenCode 关联
    opencode_session_id VARCHAR(100),  -- OpenCode 内部会话 ID
    
    -- 状态
    status VARCHAR(20) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'archived', 'deleted')),
    
    -- 统计
    message_count INTEGER DEFAULT 0,
    total_tokens_used INTEGER DEFAULT 0,
    
    -- 元数据
    metadata JSONB DEFAULT '{}',
    -- 示例: {"source": "web", "client_info": "Chrome 120", "ip": "203.0.113.10"}
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    archived_at TIMESTAMPTZ,
    
    -- 约束
    CONSTRAINT chk_workspace_format CHECK (workspace_path ~ '^/[&#xfffd;-Za-z0-9_/-]+$')
);

COMMENT ON TABLE sessions IS '会话表';
COMMENT ON COLUMN sessions.workspace_path IS '工作区绝对路径';
COMMENT ON COLUMN sessions.opencode_session_id IS '关联的 OpenCode 会话 ID';
COMMENT ON COLUMN sessions.metadata IS '扩展元数据 JSON';
```

### 4.5 消息表 (messages)

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 关联
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    
    -- 消息内容
    role VARCHAR(20) NOT NULL
        CHECK (role IN ('user', 'assistant', 'system', 'tool')),
    content TEXT,
    
    -- 消息结构（OpenCode 兼容）
    parts JSONB DEFAULT '[]',
    -- 示例: [
    --   {"type": "text", "text": "Hello"},
    --   {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": "..."}}
    -- ]
    
    -- 工具调用
    tool_calls JSONB DEFAULT NULL,
    -- 示例: {
    --   "name": "read_file",
    --   "arguments": {"path": "/workspace/main.py"},
    --   "result": "file content...",
    --   "status": "success",
    --   "duration_ms": 150
    -- }
    
    -- Token 统计
    tokens_input INTEGER DEFAULT 0,
    tokens_output INTEGER DEFAULT 0,
    tokens_total INTEGER GENERATED ALWAYS AS (tokens_input + tokens_output) STORED,
    
    -- 性能指标
    latency_ms INTEGER,  -- 响应耗时
    
    -- 排序
    sequence_number INTEGER NOT NULL,  -- 会话内消息序号
    
    -- 元数据
    metadata JSONB DEFAULT '{}',
    -- 示例: {"model": "claude-3-5-sonnet", "provider": "anthropic"}
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE messages IS '消息表';
COMMENT ON COLUMN messages.role IS '角色: user-用户, assistant-助手, system-系统, tool-工具';
COMMENT ON COLUMN messages.parts IS '消息片段数组（OpenCode 格式）';
COMMENT ON COLUMN messages.tool_calls IS '工具调用详情';
COMMENT ON COLUMN messages.sequence_number IS '会话内消息顺序号';
```

### 4.6 审计日志表 (audit_logs)

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 操作者
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    username VARCHAR(50),  -- 冗余，防止用户删除后无法追溯
    
    -- 操作信息
    action VARCHAR(50) NOT NULL,
    -- 示例: login, logout, create_session, send_message, delete_session
    
    resource_type VARCHAR(50) NOT NULL,
    -- 示例: user, session, message, agent, mcp_service
    
    resource_id UUID,
    
    -- 操作详情
    details JSONB DEFAULT '{}',
    -- 示例: {"session_title": "新会话", "agent_name": "Build"}
    
    -- 客户端信息
    ip_address INET,
    user_agent TEXT,
    
    -- 结果
    status VARCHAR(20) NOT NULL DEFAULT 'success'
        CHECK (status IN ('success', 'failure', 'denied')),
    error_message TEXT,
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE audit_logs IS '审计日志表';
COMMENT ON COLUMN audit_logs.action IS '操作类型';
COMMENT ON COLUMN audit_logs.resource_type IS '资源类型';
COMMENT ON COLUMN audit_logs.details IS '操作详情 JSON';
```

### 4.7 用量统计表 (usage_stats)

```sql
CREATE TABLE usage_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 关联
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- 统计周期
    stats_date DATE NOT NULL,
    stats_type VARCHAR(20) NOT NULL DEFAULT 'daily'
        CHECK (stats_type IN ('daily', 'weekly', 'monthly')),
    
    -- 用量数据
    session_count INTEGER DEFAULT 0,
    message_count INTEGER DEFAULT 0,
    message_count_user INTEGER DEFAULT 0,
    message_count_assistant INTEGER DEFAULT 0,
    
    -- Token 统计
    tokens_input INTEGER DEFAULT 0,
    tokens_output INTEGER DEFAULT 0,
    tokens_total INTEGER GENERATED ALWAYS AS (tokens_input + tokens_output) STORED,
    
    -- 工具调用统计
    tool_call_count INTEGER DEFAULT 0,
    tool_calls_by_name JSONB DEFAULT '{}',
    -- 示例: {"read_file": 100, "write_file": 50}
    
    -- 成本估算
    estimated_cost DECIMAL(10, 4) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- 性能指标
    avg_latency_ms INTEGER,
    p95_latency_ms INTEGER,
    p99_latency_ms INTEGER,
    
    -- 元数据
    metadata JSONB DEFAULT '{}',
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 约束
    CONSTRAINT uniq_user_date_type UNIQUE (user_id, stats_date, stats_type)
);

COMMENT ON TABLE usage_stats IS '用量统计表';
COMMENT ON COLUMN usage_stats.stats_type IS '统计类型: daily-日, weekly-周, monthly-月';
COMMENT ON COLUMN usage_stats.estimated_cost IS '预估成本（基于 Token 消耗）';
```

### 4.8 系统配置表 (system_configs)

```sql
CREATE TABLE system_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value JSONB NOT NULL,
    -- 示例: {"default_model": "anthropic/claude-sonnet-4-20250514"}
    
    description TEXT,
    
    -- 修改追踪
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE system_configs IS '系统配置表';
```

---

## 5. 索引设计

### 5.1 用户表索引

```sql
-- 主键索引（自动创建）
-- users_pkey ON users(id)

-- 唯一索引（自动创建）
-- users_username_key ON users(username)
-- users_email_key ON users(email)

-- 查询索引
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at);

-- 复合索引（管理员查询）
CREATE INDEX idx_users_role_status ON users(role, status) 
    WHERE deleted_at IS NULL;
```

### 5.2 Agent 表索引

```sql
-- 查询索引
CREATE INDEX idx_agents_mode ON agents(mode);
CREATE INDEX idx_agents_is_builtin ON agents(is_builtin);
CREATE INDEX idx_agents_created_by ON agents(created_by);

-- 全文搜索（Agent 名称和描述）
CREATE INDEX idx_agents_search ON agents 
    USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));
```

### 5.3 MCP 服务表索引

```sql
-- 查询索引
CREATE INDEX idx_mcp_services_type ON mcp_services(type);
CREATE INDEX idx_mcp_services_status ON mcp_services(status);
```

### 5.4 会话表索引

```sql
-- 查询索引
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_agent_id ON sessions(agent_id);
CREATE INDEX idx_sessions_status ON sessions(status);

-- 时间范围查询
CREATE INDEX idx_sessions_created_at ON sessions(created_at);
CREATE INDEX idx_sessions_updated_at ON sessions(updated_at);

-- 复合索引（用户会话列表）
CREATE INDEX idx_sessions_user_status_updated ON sessions(user_id, status, updated_at DESC)
    WHERE deleted_at IS NULL;

-- OpenCode 会话 ID 查询
CREATE INDEX idx_sessions_opencode_id ON sessions(opencode_session_id) 
    WHERE opencode_session_id IS NOT NULL;
```

### 5.5 消息表索引

```sql
-- 查询索引
CREATE INDEX idx_messages_session_id ON messages(session_id);
CREATE INDEX idx_messages_role ON messages(role);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- 复合索引（会话消息列表，最常用查询）
CREATE INDEX idx_messages_session_sequence ON messages(session_id, sequence_number);

-- 时间范围查询（用于统计）
CREATE INDEX idx_messages_created_at_session ON messages(created_at, session_id);

-- 工具调用查询
CREATE INDEX idx_messages_tool_calls ON messages(tool_calls) 
    WHERE tool_calls IS NOT NULL;
```

### 5.6 审计日志索引

```sql
-- 查询索引
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- 复合索引（审计查询）
CREATE INDEX idx_audit_logs_user_time ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_audit_logs_action_time ON audit_logs(action, created_at DESC);
```

### 5.7 用量统计索引

```sql
-- 查询索引
CREATE INDEX idx_usage_stats_user_id ON usage_stats(user_id);
CREATE INDEX idx_usage_stats_date ON usage_stats(stats_date);
CREATE INDEX idx_usage_stats_type ON usage_stats(stats_type);

-- 复合索引（用量查询）
CREATE INDEX idx_usage_stats_user_date ON usage_stats(user_id, stats_date DESC);
```

---

## 6. 分区策略

### 6.1 消息表分区

消息表数据量最大，建议按月分区：

```sql
-- 创建分区表（PostgreSQL 15+ 支持声明式分区）
CREATE TABLE messages_partitioned (
    id UUID,
    session_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT,
    parts JSONB DEFAULT '[]',
    tool_calls JSONB,
    tokens_input INTEGER DEFAULT 0,
    tokens_output INTEGER DEFAULT 0,
    tokens_total INTEGER,
    latency_ms INTEGER,
    sequence_number INTEGER NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
) PARTITION BY RANGE (created_at);

-- 创建月分区
CREATE TABLE messages_y2026m04 PARTITION OF messages_partitioned
    FOR VALUES FROM ('2026-04-01') TO ('2026-05-01');

CREATE TABLE messages_y2026m05 PARTITION OF messages_partitioned
    FOR VALUES FROM ('2026-05-01') TO ('2026-06-01');

-- 自动创建新分区的函数
CREATE OR REPLACE FUNCTION create_message_partition()
RETURNS void AS $$
DECLARE
    partition_date DATE;
    partition_name TEXT;
    start_date DATE;
    end_date DATE;
BEGIN
    partition_date := DATE_TRUNC('month', NOW() + INTERVAL '1 month');
    partition_name := 'messages_y' || TO_CHAR(partition_date, 'YYYY') || 'm' || TO_CHAR(partition_date, 'MM');
    start_date := partition_date;
    end_date := partition_date + INTERVAL '1 month';
    
    EXECUTE format('CREATE TABLE IF NOT EXISTS %I PARTITION OF messages_partitioned
                    FOR VALUES FROM (%L) TO (%L)',
                   partition_name, start_date, end_date);
END;
$$ LANGUAGE plpgsql;
```

### 6.2 审计日志表分区

```sql
-- 按周分区
CREATE TABLE audit_logs_partitioned (
    id UUID,
    user_id UUID,
    username VARCHAR(50),
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    status VARCHAR(20),
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL
) PARTITION BY RANGE (created_at);

-- 创建周分区
CREATE TABLE audit_logs_y2026w17 PARTITION OF audit_logs_partitioned
    FOR VALUES FROM ('2026-04-21') TO ('2026-04-28');
```

---

## 7. 视图与函数

### 7.1 常用视图

#### 7.1.1 活跃会话视图

```sql
CREATE VIEW v_active_sessions AS
SELECT 
    s.id,
    s.title,
    s.user_id,
    u.username,
    u.display_name,
    s.agent_id,
    a.name AS agent_name,
    s.workspace_path,
    s.message_count,
    s.total_tokens_used,
    s.created_at,
    s.updated_at,
    (SELECT COUNT(*) FROM messages m WHERE m.session_id = s.id) AS actual_message_count
FROM sessions s
JOIN users u ON s.user_id = u.id
JOIN agents a ON s.agent_id = a.id
WHERE s.status = 'active' 
  AND s.deleted_at IS NULL;

COMMENT ON VIEW v_active_sessions IS '活跃会话视图';
```

#### 7.1.2 用户用量统计视图

```sql
CREATE VIEW v_user_usage_summary AS
SELECT 
    u.id AS user_id,
    u.username,
    u.display_name,
    u.role,
    COUNT(DISTINCT s.id) AS total_sessions,
    COUNT(DISTINCT CASE WHEN s.status = 'active' THEN s.id END) AS active_sessions,
    COALESCE(SUM(us.tokens_total), 0) AS total_tokens_used,
    COALESCE(SUM(us.message_count), 0) AS total_messages,
    COALESCE(SUM(us.estimated_cost), 0) AS total_estimated_cost,
    MAX(s.created_at) AS last_session_at
FROM users u
LEFT JOIN sessions s ON u.id = s.user_id AND s.deleted_at IS NULL
LEFT JOIN usage_stats us ON u.id = us.user_id AND us.stats_type = 'daily'
WHERE u.deleted_at IS NULL
GROUP BY u.id, u.username, u.display_name, u.role;

COMMENT ON VIEW v_user_usage_summary IS '用户用量汇总视图';
```

### 7.2 存储函数

#### 7.2.1 更新会话统计

```sql
CREATE OR REPLACE FUNCTION update_session_stats(p_session_id UUID)
RETURNS void AS $$
BEGIN
    UPDATE sessions
    SET 
        message_count = (SELECT COUNT(*) FROM messages WHERE session_id = p_session_id),
        total_tokens_used = (SELECT COALESCE(SUM(tokens_total), 0) FROM messages WHERE session_id = p_session_id),
        updated_at = NOW()
    WHERE id = p_session_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_session_stats IS '更新会话统计信息';
```

#### 7.2.2 获取用户当日用量

```sql
CREATE OR REPLACE FUNCTION get_user_daily_usage(p_user_id UUID, p_date DATE DEFAULT CURRENT_DATE)
RETURNS TABLE (
    tokens_input INTEGER,
    tokens_output INTEGER,
    tokens_total INTEGER,
    message_count INTEGER,
    session_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COALESCE(SUM(m.tokens_input), 0)::INTEGER,
        COALESCE(SUM(m.tokens_output), 0)::INTEGER,
        COALESCE(SUM(m.tokens_total), 0)::INTEGER,
        COUNT(DISTINCT m.id)::INTEGER,
        COUNT(DISTINCT m.session_id)::INTEGER
    FROM messages m
    JOIN sessions s ON m.session_id = s.id
    WHERE s.user_id = p_user_id
      AND DATE(m.created_at) = p_date;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_user_daily_usage IS '获取用户指定日期的用量统计';
```

#### 7.2.3 归档旧会话

```sql
CREATE OR REPLACE FUNCTION archive_old_sessions(p_days INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    UPDATE sessions
    SET 
        status = 'archived',
        archived_at = NOW(),
        updated_at = NOW()
    WHERE status = 'active'
      AND updated_at < NOW() - INTERVAL '1 day' * p_days
      AND deleted_at IS NULL;
    
    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION archive_old_sessions IS '归档指定天数未活跃的会话';
```

---

## 8. 数据字典

### 8.1 枚举值定义

| 枚举类型 | 值 | 说明 |
|----------|-----|------|
| **user_role** | superadmin | 超级管理员 |
| | admin | 管理员 |
| | user | 普通用户 |
| | guest | 访客 |
| **user_status** | active | 活跃 |
| | inactive | 未激活 |
| | suspended | 已禁用 |
| | deleted | 已删除 |
| **agent_mode** | primary | 主 Agent |
| | subagent | 子 Agent |
| | all | 两者皆可 |
| **session_status** | active | 活跃 |
| | archived | 已归档 |
| | deleted | 已删除 |
| **message_role** | user | 用户 |
| | assistant | 助手 |
| | system | 系统 |
| | tool | 工具 |
| **mcp_type** | local | 本地命令 |
| | remote | 远程 URL |
| **mcp_status** | active | 在线 |
| | inactive | 离线 |
| | error | 错误 |
| **audit_action** | login | 登录 |
| | logout | 登出 |
| | create_session | 创建会话 |
| | delete_session | 删除会话 |
| | send_message | 发送消息 |
| | create_agent | 创建 Agent |
| | update_config | 更新配置 |
| **audit_status** | success | 成功 |
| | failure | 失败 |
| | denied | 拒绝 |

---

## 9. 迁移脚本

### 9.1 初始迁移（V1.0.0）

```sql
-- V1.0.0__initial_schema.sql

-- 启用 UUID 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建表（见第 4 节）
-- ...

-- 创建索引（见第 5 节）
-- ...

-- 创建视图（见第 7 节）
-- ...

-- 创建函数（见第 7 节）
-- ...

-- 插入默认数据
INSERT INTO system_configs (config_key, config_value, description) VALUES
('default_model', '{"provider": "anthropic", "model": "claude-sonnet-4-20250514"}', '默认 LLM 模型'),
('rate_limit', '{"requests_per_minute": 60, "tokens_per_day": 100000}', '速率限制配置'),
('maintenance', '{"enabled": false, "message": "系统维护中"}', '维护模式配置');

-- 创建默认 Agent
INSERT INTO agents (name, description, system_prompt, model_config, is_builtin, is_public) VALUES
('build', '默认开发 Agent', 'You are a helpful coding assistant.', '{"temperature": 0.3}', true, true),
('plan', '规划 Agent', 'You are a planning assistant.', '{"temperature": 0.1}', true, true),
('general', '通用 Agent', 'You are a general assistant.', '{"temperature": 0.5}', true, true);
```

### 9.2 后续迁移示例

```sql
-- V1.1.0__add_session_summary.sql
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS summary TEXT;

-- V1.2.0__add_message_parts.sql
ALTER TABLE messages ADD COLUMN IF NOT EXISTS parts JSONB DEFAULT '[]';

-- V1.3.0__add_user_quota.sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS daily_token_quota INTEGER DEFAULT 100000;
ALTER TABLE users ADD COLUMN IF NOT EXISTS monthly_token_quota INTEGER DEFAULT 2000000;
```

---

## 10. 备份策略

### 10.1 备份方案

| 备份类型 | 频率 | 保留期 | 工具 |
|----------|------|--------|------|
| **全量备份** | 每日 02:00 | 30 天 | pg_dump |
| **增量备份** | 每小时 | 7 天 | WAL 归档 |
| **逻辑备份** | 每周 | 90 天 | pg_dump (schema + data) |

### 10.2 pg_dump 脚本

```bash
#!/bin/bash
# backup.sh

DB_NAME="aigateway"
DB_USER="postgres"
BACKUP_DIR="/opt/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)

# 全量备份
pg_dump -h localhost -U $DB_USER -d $DB_NAME -F c -f "$BACKUP_DIR/full_$DATE.dump"

# 清理 30 天前的备份
find $BACKUP_DIR -name "full_*.dump" -mtime +30 -delete

# 上传到 S3（可选）
aws s3 cp "$BACKUP_DIR/full_$DATE.dump" s3://aigateway-backups/postgresql/
```

### 10.3 恢复流程

```bash
# 恢复数据库
pg_restore -h localhost -U postgres -d aigateway -c full_20260421_020000.dump

# 验证恢复
psql -h localhost -U postgres -d aigateway -c "SELECT COUNT(*) FROM users;"
```

---

**文档结束**
