# 09 - 开发规范与约定

**项目名称**：AI Agent 对话平台  
**版本**：v1.0  
**日期**：2026-04-21  
**编写人**：AI Agent 团队  
**目标读者**：开发团队

---

## 目录

1. [代码规范](#1-代码规范)
2. [Git 工作流](#2-git-工作流)
3. [项目结构规范](#3-项目结构规范)
4. [API 设计规范](#4-api-设计规范)
5. [数据库规范](#5-数据库规范)
6. [前端规范](#6-前端规范)
7. [文档规范](#7-文档规范)
8. [代码审查规范](#8-代码审查规范)

---

## 1. 代码规范

### 1.1 Python 规范

#### 1.1.1 代码风格

- **PEP 8**：遵循 PEP 8 规范
- **Black**：使用 Black 格式化代码
- **isort**：排序 imports
- **flake8**：静态代码检查
- **mypy**：类型检查

```bash
# 安装工具
pip install black isort flake8 mypy

# 配置 .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
        language_version: python3.12
  
  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort
  
  - repo: https://github.com/PyCQA/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
```

#### 1.1.2 命名规范

| 类型 | 命名方式 | 示例 |
|------|---------|------|
| 模块/包 | snake_case | `session_manager.py` |
| 类 | PascalCase | `SessionManager` |
| 函数/方法 | snake_case | `create_session()` |
| 常量 | SCREAMING_SNAKE_CASE | `MAX_SESSIONS` |
| 变量 | snake_case | `session_id` |
| 私有变量 | _snake_case | `_internal_state` |

#### 1.1.3 类型注解

```python
from typing import Optional, List, Dict, Any
from datetime import datetime

async def create_session(
    user_id: str,
    title: Optional[str] = None,
    agent_id: str = "default",
    metadata: Optional[Dict[str, Any]] = None
) -> Session:
    """创建新会话
    
    Args:
        user_id: 用户 ID
        title: 会话标题（可选）
        agent_id: Agent ID（默认 "default"）
        metadata: 扩展元数据（可选）
    
    Returns:
        创建的会话对象
    
    Raises:
        ValueError: 当 user_id 为空时
        NotFoundError: 当 agent_id 不存在时
    """
    if not user_id:
        raise ValueError("user_id is required")
    
    # ... 实现代码
```

#### 1.1.4 异步编程规范

```python
# 正确：使用 async/await
async def fetch_data() -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        return response.json()

# 错误：混合同步和异步代码
def bad_example():  # 不要这样做
    response = requests.get("https://api.example.com/data")  # 同步请求
    return response.json()

# 正确：在同步代码中调用异步函数
import asyncio

def sync_wrapper():
    return asyncio.run(fetch_data())
```

### 1.2 TypeScript 规范

#### 1.2.1 代码风格

- **ESLint**：使用 ESLint 检查代码
- **Prettier**：格式化代码
- **TypeScript**：strict 模式

```json
// .eslintrc.json
{
  "extends": [
    "eslint:recommended",
    "@typescript-eslint/recommended",
    "plugin:react-hooks/recommended"
  ],
  "parser": "@typescript-eslint/parser",
  "plugins": ["@typescript-eslint", "react-hooks"],
  "rules": {
    "@typescript-eslint/explicit-function-return-type": "warn",
    "@typescript-eslint/no-explicit-any": "error",
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn"
  }
}
```

#### 1.2.2 命名规范

| 类型 | 命名方式 | 示例 |
|------|---------|------|
| 组件 | PascalCase | `ChatWindow.tsx` |
| Hooks | camelCase, use 前缀 | `useChat.ts` |
| 工具函数 | camelCase | `formatDate.ts` |
| 类型/接口 | PascalCase | `Message.ts` |
| 常量 | SCREAMING_SNAKE_CASE | `MAX_FILE_SIZE` |
| 枚举 | PascalCase | `UserRole` |

#### 1.2.3 React 组件规范

```typescript
// 正确：使用函数组件 + Hooks
import React, { useState, useCallback } from 'react';
import { useChatStore } from '@/features/chat/stores/chatStore';

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export const MessageInput: React.FC<MessageInputProps> = ({
  onSend,
  disabled = false,
}) => {
  const [content, setContent] = useState('');
  const { isLoading } = useChatStore();
  
  const handleSubmit = useCallback(() => {
    if (!content.trim() || isLoading) return;
    onSend(content.trim());
    setContent('');
  }, [content, isLoading, onSend]);
  
  return (
    <div className="flex gap-2">
      <input
        type="text"
        value={content}
        onChange={(e) => setContent(e.target.value)}
        disabled={disabled || isLoading}
        className="flex-1 px-3 py-2 border rounded"
      />
      <button
        onClick={handleSubmit}
        disabled={disabled || isLoading}
        className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
      >
        发送
      </button>
    </div>
  );
};
```

---

## 2. Git 工作流

### 2.1 分支策略

采用 **Git Flow** 工作流：

```
main        ●────────●────────●────────●
             ↑        ↑        ↑        ↑
release/v1.0 ──●────●          │        │
                ↑    ↑          │        │
develop    ─────●────●─────────●────────●
                 ↑    ↑         ↑        ↑
feature/xxx  ────●────●         │        │
feature/yyy  ────────●────●────│────────│
                     ↑    ↑    │        │
hotfix/xxx   ──────────────●────●────────│
                           ↑    ↑        ↑
```

| 分支 | 用途 | 保护规则 |
|------|------|----------|
| `main` | 生产环境代码 | 禁止直接推送，需 PR |
| `develop` | 开发环境代码 | 禁止直接推送，需 PR |
| `feature/*` | 新功能开发 | 从 develop 创建 |
| `release/*` | 发布准备 | 从 develop 创建 |
| `hotfix/*` | 紧急修复 | 从 main 创建 |

### 2.2 提交规范

使用 **Conventional Commits** 规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**类型**：

| 类型 | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | 修复 Bug |
| `docs` | 文档更新 |
| `style` | 代码格式（不影响功能） |
| `refactor` | 重构 |
| `perf` | 性能优化 |
| `test` | 测试相关 |
| `chore` | 构建/工具链 |

**示例**：

```bash
feat(session): 添加会话归档功能

- 实现会话归档 API
- 添加归档会话列表查询
- 更新前端会话管理组件

Closes #123
```

### 2.3 Pull Request 规范

**PR 模板**：

```markdown
## 描述
简要描述本次变更的内容

## 变更类型
- [ ] 新功能
- [ ] Bug 修复
- [ ] 文档更新
- [ ] 性能优化
- [ ] 重构

## 测试
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 手动测试通过

## 检查清单
- [ ] 代码遵循项目规范
- [ ] 添加了必要的测试
- [ ] 更新了相关文档
- [ ] 通过了代码审查
```

---

## 3. 项目结构规范

### 3.1 后端项目结构

```
gateway/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── dependencies/        # 依赖注入
│   │   ├── __init__.py
│   │   ├── auth.py          # 认证依赖
│   │   └── db.py            # 数据库依赖
│   ├── routers/             # 路由模块
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── sessions.py
│   │   ├── chat.py
│   │   ├── agents.py
│   │   └── admin.py
│   ├── services/            # 业务逻辑
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── session_service.py
│   │   └── chat_service.py
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   ├── schemas.py       # Pydantic 模型
│   │   └── database.py      # SQLAlchemy 模型
│   ├── repositories/        # 数据访问层
│   │   ├── __init__.py
│   │   ├── user_repo.py
│   │   └── session_repo.py
│   └── utils/               # 工具函数
│       ├── __init__.py
│       ├── security.py
│       └── validators.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest 配置
│   ├── unit/                # 单元测试
│   └── integration/         # 集成测试
├── alembic/                 # 数据库迁移
├── scripts/                 # 脚本文件
├── docs/                    # 项目文档
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
└── pytest.ini
```

### 3.2 前端项目结构

```
frontend/
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── features/            # 功能模块
│   │   ├── auth/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── stores/
│   │   │   ├── types.ts
│   │   │   └── api.ts
│   │   ├── chat/
│   │   └── sessions/
│   ├── components/          # 公共组件
│   ├── hooks/               # 全局 Hooks
│   ├── stores/              # 全局状态
│   ├── lib/                 # 工具库
│   ├── types/               # 类型定义
│   └── styles/              # 样式文件
├── tests/
│   ├── unit/
│   └── e2e/
├── public/
├── index.html
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
└── package.json
```

---

## 4. API 设计规范

### 4.1 RESTful API 规范

#### 4.1.1 URL 设计

```
GET    /api/v1/users          # 列表
GET    /api/v1/users/{id}     # 详情
POST   /api/v1/users          # 创建
PUT    /api/v1/users/{id}     # 全量更新
PATCH  /api/v1/users/{id}     # 部分更新
DELETE /api/v1/users/{id}     # 删除
```

#### 4.1.2 状态码使用

| 状态码 | 使用场景 |
|--------|---------|
| 200 | 成功 |
| 201 | 创建成功 |
| 204 | 删除成功（无返回内容） |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 422 | 参数校验失败 |
| 429 | 请求频率超限 |
| 500 | 服务器内部错误 |
| 502 | 网关错误（下游服务异常） |

#### 4.1.3 响应格式

```json
{
  "code": 0,
  "message": "success",
  "data": { ... },
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 100
  }
}
```

### 4.2 错误处理规范

```python
# 自定义异常
class AppException(Exception):
    def __init__(
        self,
        code: int,
        message: str,
        status_code: int = 500,
        details: Optional[dict] = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

class NotFoundError(AppException):
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            code=3001,
            message=f"{resource} not found: {resource_id}",
            status_code=404
        )

class ValidationError(AppException):
    def __init__(self, field: str, error: str):
        super().__init__(
            code=2002,
            message="Validation failed",
            status_code=422,
            details={"field": field, "error": error}
        )

# 全局异常处理
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "details": exc.details
        }
    )
```

---

## 5. 数据库规范

### 5.1 表设计规范

#### 5.1.1 命名规范

- **表名**：复数形式，snake_case
- **字段名**：snake_case
- **索引名**：`idx_{table}_{column}`
- **外键名**：`fk_{table}_{referenced_table}`

#### 5.1.2 必备字段

```sql
CREATE TABLE example (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 业务字段
    ...
    
    -- 审计字段
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,  -- 软删除
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);
```

### 5.2 查询规范

```python
# 正确：使用参数化查询
result = await db.execute(
    text("SELECT * FROM users WHERE username = :username"),
    {"username": username}
)

# 错误：字符串拼接（SQL 注入风险）
# result = await db.execute(f"SELECT * FROM users WHERE username = '{username}'")

# 正确：使用 ORM
user = await db.get(User, user_id)

# 正确：分页查询
result = await db.execute(
    select(User)
    .where(User.status == "active")
    .offset((page - 1) * page_size)
    .limit(page_size)
)
```

---

## 6. 前端规范

### 6.1 组件设计原则

- **单一职责**：一个组件只做一件事
- ** props 向下传递**：数据通过 props 向下传递
- **事件向上触发**：事件通过回调向上传递
- **避免深层嵌套**：组件嵌套不超过 3 层

### 6.2 Hooks 使用规范

```typescript
// 正确：Hooks 在组件顶层调用
function MyComponent() {
  const [count, setCount] = useState(0);
  const { data } = useQuery({...});
  
  useEffect(() => {
    // 副作用逻辑
  }, [count]);
  
  return <div>{count}</div>;
}

// 错误：Hooks 在条件语句中调用
function BadComponent() {
  if (condition) {
    const [state, setState] = useState(0);  // ❌ 错误！
  }
}

// 错误：Hooks 在循环中调用
function BadComponent() {
  items.map((item, index) => {
    const [state, setState] = useState(0);  // ❌ 错误！
  });
}
```

### 6.3 样式规范

```typescript
// 正确：使用 Tailwind CSS
function Button({ children, variant = 'primary' }: ButtonProps) {
  return (
    <button
      className={cn(
        "px-4 py-2 rounded-lg font-medium transition-colors",
        variant === 'primary' && "bg-blue-600 text-white hover:bg-blue-700",
        variant === 'secondary' && "bg-gray-200 text-gray-800 hover:bg-gray-300",
        variant === 'danger' && "bg-red-600 text-white hover:bg-red-700"
      )}
    >
      {children}
    </button>
  );
}

// 错误：使用内联样式
function BadButton() {
  return (
    <button style={{ padding: '8px 16px', backgroundColor: 'blue' }}>
      Click me
    </button>
  );
}
```

---

## 7. 文档规范

### 7.1 代码注释规范

```python
# 模块级文档字符串
"""
会话管理模块

提供会话的 CRUD 操作和状态管理
"""

class SessionManager:
    """会话管理器
    
    负责创建、查询、更新和删除会话
    
    Attributes:
        db: 数据库会话
        redis: Redis 客户端
    
    Example:
        >>> manager = SessionManager(db, redis)
        >>> session = await manager.create(user_id="123", title="Test")
        >>> print(session.id)
        "550e8400-e29b-41d4-a716-446655440000"
    """
    
    async def create_session(
        self,
        user_id: str,
        title: Optional[str] = None
    ) -> Session:
        """创建新会话
        
        Args:
            user_id: 用户 ID
            title: 会话标题，默认为 "新会话"
        
        Returns:
            创建的会话对象
        
        Raises:
            ValueError: 当 user_id 为空时
            NotFoundError: 当用户不存在时
        """
        # 实现代码
```

### 7.2 API 文档规范

使用 FastAPI 自动文档功能：

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="AI Gateway API",
    description="AI Agent 对话平台 API",
    version="1.0.0"
)

class CreateSessionRequest(BaseModel):
    """创建会话请求"""
    title: Optional[str] = Field(
        None,
        description="会话标题",
        example="Python 项目开发"
    )
    agent_id: str = Field(
        "default",
        description="Agent ID",
        example="build"
    )

class SessionResponse(BaseModel):
    """会话响应"""
    id: str = Field(..., description="会话 ID")
    title: str = Field(..., description="会话标题")
    status: str = Field(..., description="会话状态")
    created_at: datetime = Field(..., description="创建时间")

@app.post(
    "/api/v1/sessions",
    response_model=SessionResponse,
    summary="创建会话",
    description="创建新的 AI 对话会话",
    tags=["会话管理"]
)
async def create_session(
    request: CreateSessionRequest,
    current_user: User = Depends(get_current_user)
):
    """创建新会话
    
    - **title**: 会话标题（可选）
    - **agent_id**: 指定 Agent（默认使用默认 Agent）
    """
    session = await session_service.create(
        user_id=current_user.id,
        title=request.title,
        agent_id=request.agent_id
    )
    return session
```

---

## 8. 代码审查规范

### 8.1 审查清单

#### 8.1.1 功能性检查

- [ ] 代码是否实现了需求
- [ ] 边界条件是否处理
- [ ] 错误处理是否完善
- [ ] 日志记录是否充分

#### 8.1.2 安全性检查

- [ ] 输入是否验证
- [ ] SQL 注入风险
- [ ] XSS 风险
- [ ] 敏感信息泄露
- [ ] 权限检查

#### 8.1.3 性能检查

- [ ] N+1 查询问题
- [ ] 不必要的循环
- [ ] 内存泄漏风险
- [ ] 大文件处理

#### 8.1.4 代码质量

- [ ] 代码是否可读
- [ ] 命名是否清晰
- [ ] 注释是否充分
- [ ] 是否符合规范

### 8.2 审查流程

1. **提交 PR**：开发者提交 Pull Request
2. **自动化检查**：CI 运行测试和代码检查
3. **代码审查**：至少 1 名审查者审查代码
4. **修改反馈**：开发者根据反馈修改
5. **合并代码**：审查通过后合并到目标分支

---

**文档结束**
