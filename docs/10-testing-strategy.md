# 10 - 测试策略文档

**项目名称**：AI Agent 对话平台  
**版本**：v1.0  
**日期**：2026-04-21  
**编写人**：AI Agent 团队  
**目标读者**：测试团队、开发团队、QA 工程师

---

## 目录

1. [测试概述](#1-测试概述)
2. [测试环境](#2-测试环境)
3. [单元测试](#3-单元测试)
4. [集成测试](#4-集成测试)
5. [端到端测试](#5-端到端测试)
6. [性能测试](#6-性能测试)
7. [安全测试](#7-安全测试)
8. [测试自动化](#8-测试自动化)
9. [测试报告](#9-测试报告)

---

## 1. 测试概述

### 1.1 测试目标

- 确保系统功能符合需求规格
- 保证系统在高并发下稳定运行
- 验证系统安全性
- 确保用户体验流畅

### 1.2 测试类型

| 测试类型 | 目标 | 工具 |
|----------|------|------|
| **单元测试** | 验证最小代码单元 | Pytest, Jest |
| **集成测试** | 验证模块间交互 | Pytest, Supertest |
| **端到端测试** | 验证完整用户流程 | Playwright |
| **性能测试** | 验证系统性能 | k6, Locust |
| **安全测试** | 发现安全漏洞 | OWASP ZAP |
| **API 测试** | 验证接口契约 | Postman, REST Assured |

### 1.3 测试金字塔

```
        /\
       /  \      E2E 测试 (5%)
      /----\
     /      \    集成测试 (20%)
    /--------\
   /          \  单元测试 (75%)
  /------------\
```

---

## 2. 测试环境

### 2.1 环境矩阵

| 环境 | 用途 | 数据 |
|------|------|------|
| **本地开发** | 开发调试 | 模拟数据 |
| **测试环境** | 自动化测试 | 测试数据集 |
| **预发布** | 验收测试 | 生产数据脱敏 |
| **生产环境** | 线上监控 | 真实数据 |

### 2.2 Docker Compose 测试配置

```yaml
# docker-compose.test.yml
version: "3.8"

services:
  gateway-test:
    build:
      context: ./gateway
      dockerfile: Dockerfile.test
    environment:
      - DATABASE_URL=postgresql+asyncpg://test:test@postgres-test:5432/test
      - REDIS_URL=redis://redis-test:6379/1
      - ENVIRONMENT=test
    depends_on:
      - postgres-test
      - redis-test
    volumes:
      - ./gateway:/app
    command: pytest -v --cov=app --cov-report=xml

  postgres-test:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: test
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
    volumes:
      - ./gateway/tests/fixtures:/docker-entrypoint-initdb.d

  redis-test:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb

  e2e-test:
    build:
      context: ./frontend
      dockerfile: Dockerfile.test
    environment:
      - CI=true
    depends_on:
      - gateway-test
    command: npx playwright test
```

---

## 3. 单元测试

### 3.1 Python 单元测试

#### 3.1.1 测试配置

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
```

#### 3.1.2 测试示例

```python
# tests/unit/test_auth_service.py
import pytest
from unittest.mock import Mock, AsyncMock
from app.services.auth_service import AuthService
from app.models.schemas import UserCreate

class TestAuthService:
    @pytest.fixture
    def auth_service(self):
        return AuthService(
            user_repo=Mock(),
            token_service=Mock(),
            password_hasher=Mock()
        )
    
    @pytest.mark.unit
    async def test_register_user_success(self, auth_service):
        """测试用户注册成功"""
        # Arrange
        user_data = UserCreate(
            username="testuser",
            password="YOUR_PASSWORD",
            email="test@example.com"
        )
        auth_service.user_repo.get_by_username = AsyncMock(return_value=None)
        auth_service.password_hasher.hash = Mock(return_value="hashed_password")
        auth_service.user_repo.create = AsyncMock(return_value={
            "id": "123",
            "username": "testuser",
            "email": "test@example.com"
        })
        
        # Act
        result = await auth_service.register(user_data)
        
        # Assert
        assert result["username"] == "testuser"
        assert result["email"] == "test@example.com"
        auth_service.user_repo.create.assert_called_once()
    
    @pytest.mark.unit
    async def test_register_duplicate_username(self, auth_service):
        """测试重复用户名注册失败"""
        # Arrange
        user_data = UserCreate(
            username="existinguser",
            password="YOUR_PASSWORD"
        )
        auth_service.user_repo.get_by_username = AsyncMock(return_value={
            "id": "456",
            "username": "existinguser"
        })
        
        # Act & Assert
        with pytest.raises(ValueError, match="Username already exists"):
            await auth_service.register(user_data)
    
    @pytest.mark.unit
    async def test_login_success(self, auth_service):
        """测试登录成功"""
        # Arrange
        auth_service.user_repo.get_by_username = AsyncMock(return_value={
            "id": "123",
            "username": "testuser",
            "password_hash": "hashed_password"
        })
        auth_service.password_hasher.verify = Mock(return_value=True)
        auth_service.token_service.create_access_token = YOUR_SECRET
            return_value="access_token"
        )
        auth_service.token_service.create_refresh_token = YOUR_SECRET
            return_value="refresh_token"
        )
        
        # Act
        result = await auth_service.login("testuser", "password")
        
        # Assert
        assert result["access_token"] == "access_token"
        assert result["refresh_token"] == "refresh_token"
    
    @pytest.mark.unit
    async def test_login_invalid_password(self, auth_service):
        """测试密码错误登录失败"""
        # Arrange
        auth_service.user_repo.get_by_username = AsyncMock(return_value={
            "id": "123",
            "username": "testuser",
            "password_hash": "hashed_password"
        })
        auth_service.password_hasher.verify = Mock(return_value=False)
        
        # Act & Assert
        with pytest.raises(AuthenticationError):
            await auth_service.login("testuser", "wrong_password")

# tests/unit/test_session_service.py
class TestSessionService:
    @pytest.fixture
    def session_service(self):
        return SessionService(
            session_repo=Mock(),
            opencode_client=Mock(),
            workspace_manager=Mock()
        )
    
    @pytest.mark.unit
    async def test_create_session(self, session_service):
        """测试创建会话"""
        # Arrange
        user_id = "user-123"
        title = "Test Session"
        
        session_service.workspace_manager.create = AsyncMock(
            return_value="/workspace/user-123/session-456"
        )
        session_service.opencode_client.create_session = AsyncMock(
            return_value={"id": "opencode-789"}
        )
        session_service.session_repo.create = AsyncMock(return_value={
            "id": "session-456",
            "title": title,
            "user_id": user_id
        })
        
        # Act
        result = await session_service.create(user_id, title)
        
        # Assert
        assert result["title"] == title
        assert result["user_id"] == user_id
        session_service.workspace_manager.create.assert_called_once()
        session_service.opencode_client.create_session.assert_called_once()
```

### 3.2 TypeScript 单元测试

#### 3.2.1 Jest 配置

```typescript
// jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.test.ts', '**/?(*.)+(spec|test).ts'],
  transform: {
    '^.+\\.tsx?$': 'ts-jest',
  },
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  setupFilesAfterEnv: ['<rootDir>/src/test-setup.ts'],
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/**/index.ts',
  ],
};
```

#### 3.2.2 测试示例

```typescript
// src/features/auth/__tests__/useAuth.test.ts
import { renderHook, act } from '@testing-library/react';
import { useAuth } from '../hooks/useAuth';
import { useAuthStore } from '../stores/authStore';

describe('useAuth', () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: null,
      accessToken: null,
      isAuthenticated: false,
    });
  });

  it('should login successfully', async () => {
    // Arrange
    const { result } = renderHook(() => useAuth());
    
    // Act
    await act(async () => {
      await result.current.login({
        username: 'testuser',
        password: 'YOUR_PASSWORD',
      });
    });
    
    // Assert
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user?.username).toBe('testuser');
  });

  it('should logout successfully', () => {
    // Arrange
    useAuthStore.setState({
      user: { id: '1', username: 'test' },
      isAuthenticated: true,
    });
    
    const { result } = renderHook(() => useAuth());
    
    // Act
    act(() => {
      result.current.logout();
    });
    
    // Assert
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
  });
});

// src/features/chat/__tests__/chatStore.test.ts
import { useChatStore } from '../stores/chatStore';

describe('chatStore', () => {
  beforeEach(() => {
    useChatStore.setState({
      messages: [],
      isLoading: false,
      error: null,
    });
  });

  it('should add message', () => {
    // Act
    useChatStore.getState().addMessage({
      id: '1',
      role: 'user',
      content: 'Hello',
      parts: [{ type: 'text', text: 'Hello' }],
      createdAt: new Date().toISOString(),
      status: 'complete',
    });
    
    // Assert
    const messages = useChatStore.getState().messages;
    expect(messages).toHaveLength(1);
    expect(messages[0].content).toBe('Hello');
  });

  it('should update streaming message', () => {
    // Arrange
    useChatStore.getState().setStreamingMessage({
      id: '2',
      role: 'assistant',
      content: '',
      parts: [],
      createdAt: new Date().toISOString(),
      status: 'streaming',
    });
    
    // Act
    useChatStore.getState().appendStreamingContent('Hello');
    
    // Assert
    expect(useChatStore.getState().streamingMessage?.content).toBe('Hello');
  });
});
```

---

## 4. 集成测试

### 4.1 API 集成测试

```python
# tests/integration/test_chat_api.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def auth_token(client):
    """获取认证 Token"""
    response = await client.post("/api/v1/auth/login", json={
        "username": "testuser",
        "password": "testpassword"
    })
    return response.json()["data"]["access_token"]

class TestChatAPI:
    @pytest.mark.integration
    async def test_create_session(self, client, auth_token):
        """测试创建会话"""
        # Act
        response = await client.post(
            "/api/v1/sessions",
            json={"title": "Test Session"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["title"] == "Test Session"
        assert "id" in data
    
    @pytest.mark.integration
    async def test_send_message(self, client, auth_token):
        """测试发送消息"""
        # Arrange
        session_response = await client.post(
            "/api/v1/sessions",
            json={"title": "Test"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        session_id = session_response.json()["data"]["id"]
        
        # Act
        response = await client.post(
            "/api/v1/chat/stream",
            json={
                "session_id": session_id,
                "message": "Hello"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream"
    
    @pytest.mark.integration
    async def test_get_messages(self, client, auth_token):
        """测试获取消息列表"""
        # Arrange
        session_response = await client.post(
            "/api/v1/sessions",
            json={"title": "Test"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        session_id = session_response.json()["data"]["id"]
        
        # Act
        response = await client.get(
            f"/api/v1/sessions/{session_id}/messages",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()["data"]
        assert "items" in data
        assert "has_more" in data
```

### 4.2 数据库集成测试

```python
# tests/integration/test_database.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import User, Session

@pytest.mark.integration
class TestDatabase:
    async def test_user_crud(self, db_session: AsyncSession):
        """测试用户 CRUD"""
        # Create
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed"
        )
        db_session.add(user)
        await db_session.commit()
        
        # Read
        result = await db_session.get(User, user.id)
        assert result.username == "testuser"
        
        # Update
        result.display_name = "Test User"
        await db_session.commit()
        
        # Delete
        await db_session.delete(result)
        await db_session.commit()
        
        result = await db_session.get(User, user.id)
        assert result is None
    
    async def test_session_user_relationship(self, db_session: AsyncSession):
        """测试会话与用户关系"""
        # Arrange
        user = User(username="test", password_hash="hash")
        db_session.add(user)
        await db_session.commit()
        
        session = Session(
            user_id=user.id,
            title="Test Session",
            workspace_path="/workspace/test"
        )
        db_session.add(session)
        await db_session.commit()
        
        # Act
        result = await db_session.get(Session, session.id)
        
        # Assert
        assert result.user_id == user.id
        assert result.title == "Test Session"
```

---

## 5. 端到端测试

### 5.1 Playwright 配置

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
});
```

### 5.2 E2E 测试用例

```typescript
// e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('should login successfully', async ({ page }) => {
    // Arrange
    await page.goto('/login');
    
    // Act
    await page.fill('[data-testid="username-input"]', 'testuser');
    await page.fill('[data-testid="password-input"]', 'testpassword');
    await page.click('[data-testid="login-button"]');
    
    // Assert
    await expect(page).toHaveURL('/');
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
  });
  
  test('should show error for invalid credentials', async ({ page }) => {
    // Arrange
    await page.goto('/login');
    
    // Act
    await page.fill('[data-testid="username-input"]', 'wronguser');
    await page.fill('[data-testid="password-input"]', 'wrongpassword');
    await page.click('[data-testid="login-button"]');
    
    // Assert
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toContainText('Invalid credentials');
  });
});

// e2e/chat.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Chat', () => {
  test.beforeEach(async ({ page }) => {
    // 登录
    await page.goto('/login');
    await page.fill('[data-testid="username-input"]', 'testuser');
    await page.fill('[data-testid="password-input"]', 'testpassword');
    await page.click('[data-testid="login-button"]');
    await page.waitForURL('/');
  });
  
  test('should create new session', async ({ page }) => {
    // Act
    await page.click('[data-testid="new-session-button"]');
    
    // Assert
    await expect(page.locator('[data-testid="chat-window"]')).toBeVisible();
    await expect(page.locator('[data-testid="session-list"]')).toContainText('新会话');
  });
  
  test('should send message and receive response', async ({ page }) => {
    // Arrange
    await page.click('[data-testid="new-session-button"]');
    
    // Act
    await page.fill('[data-testid="message-input"]', 'Hello, AI!');
    await page.click('[data-testid="send-button"]');
    
    // Assert
    await expect(page.locator('[data-testid="message-list"]')).toContainText('Hello, AI!');
    await expect(page.locator('[data-testid="ai-message"]')).toBeVisible({ timeout: 30000 });
  });
  
  test('should switch between sessions', async ({ page }) => {
    // Arrange
    await page.click('[data-testid="new-session-button"]');
    await page.fill('[data-testid="message-input"]', 'Message 1');
    await page.click('[data-testid="send-button"]');
    
    await page.click('[data-testid="new-session-button"]');
    await page.fill('[data-testid="message-input"]', 'Message 2');
    await page.click('[data-testid="send-button"]');
    
    // Act
    const sessions = page.locator('[data-testid="session-item"]');
    await sessions.first().click();
    
    // Assert
    await expect(page.locator('[data-testid="message-list"]')).toContainText('Message 1');
  });
});

// e2e/admin.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Admin Panel', () => {
  test.beforeEach(async ({ page }) => {
    // 以管理员身份登录
    await page.goto('/login');
    await page.fill('[data-testid="username-input"]', 'admin');
    await page.fill('[data-testid="password-input"]', 'adminpassword');
    await page.click('[data-testid="login-button"]');
    await page.waitForURL('/');
  });
  
  test('should access admin dashboard', async ({ page }) => {
    // Act
    await page.click('[data-testid="admin-menu"]');
    
    // Assert
    await expect(page).toHaveURL('/admin');
    await expect(page.locator('[data-testid="admin-dashboard"]')).toBeVisible();
  });
  
  test('should manage users', async ({ page }) => {
    // Arrange
    await page.goto('/admin/users');
    
    // Act
    await page.click('[data-testid="create-user-button"]');
    await page.fill('[data-testid="username-input"]', 'newuser');
    await page.fill('[data-testid="email-input"]', 'new@example.com');
    await page.click('[data-testid="save-button"]');
    
    // Assert
    await expect(page.locator('[data-testid="user-list"]')).toContainText('newuser');
  });
});
```

---

## 6. 性能测试

### 6.1 k6 测试脚本

```javascript
// performance/load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 },   //  ramp up
    { duration: '5m', target: 100 },   //  steady state
    { duration: '2m', target: 200 },   //  ramp up
    { duration: '5m', target: 200 },   //  steady state
    { duration: '2m', target: 0 },     //  ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],   // 95% 请求 < 500ms
    http_req_failed: ['rate<0.01'],      // 错误率 < 1%
  },
};

const BASE_URL = 'https://api.aigateway.example.com/api/v1';

export function setup() {
  // 登录获取 token
  const loginRes = http.post(`${BASE_URL}/auth/login`, {
    username: 'testuser',
    password: 'YOUR_PASSWORD',
  });
  
  check(loginRes, {
    'login successful': (r) => r.status === 200,
  });
  
  return {
    token: YOUR_SECRET'data.access_token'),
  };
}

export default function (data) {
  const params = {
    headers: {
      'Authorization': `Bearer ${data.token}`,
      'Content-Type': 'application/json',
    },
  };
  
  // 获取会话列表
  const sessionsRes = http.get(`${BASE_URL}/sessions`, params);
  check(sessionsRes, {
    'get sessions status is 200': (r) => r.status === 200,
    'get sessions response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  sleep(1);
  
  // 创建会话
  const createRes = http.post(`${BASE_URL}/sessions`, JSON.stringify({
    title: `Load Test Session ${__VU}-${__ITER}`,
  }), params);
  check(createRes, {
    'create session status is 200': (r) => r.status === 200,
  });
  
  const sessionId = createRes.json('data.id');
  sleep(2);
  
  // 获取消息列表
  const messagesRes = http.get(
    `${BASE_URL}/sessions/${sessionId}/messages`,
    params
  );
  check(messagesRes, {
    'get messages status is 200': (r) => r.status === 200,
  });
  
  sleep(1);
}
```

### 6.2 性能基准

| 指标 | 目标值 | 测试方法 |
|------|--------|----------|
| **并发用户数** | 500 | k6 压测 |
| **响应时间 P95** | < 500ms | k6 压测 |
| **响应时间 P99** | < 1s | k6 压测 |
| **错误率** | < 1% | k6 压测 |
| **吞吐量** | 1000 RPS | k6 压测 |
| **SSE 连接数** | 500+ | 手动测试 |
| **首字延迟** | < 3s | 手动测试 |

---

## 7. 安全测试

### 7.1 OWASP ZAP 扫描

```bash
# 启动 ZAP 守护进程
docker run -t owasp/zap2docker-stable zap-baseline.py \
    -t https://api.aigateway.example.com \
    -r zap-report.html

# 完整扫描
docker run -t owasp/zap2docker-stable zap-full-scan.py \
    -t https://api.aigateway.example.com \
    -r zap-full-report.html
```

### 7.2 安全测试用例

```python
# tests/security/test_auth_security.py
import pytest
from httpx import AsyncClient

@pytest.mark.security
class TestAuthSecurity:
    async def test_sql_injection_login(self, client: AsyncClient):
        """测试登录 SQL 注入防护"""
        # Arrange
        payloads = [
            "' OR '1'='1",
            "admin'--",
            "1'; DROP TABLE users; --",
        ]
        
        for payload in payloads:
            # Act
            response = await client.post("/api/v1/auth/login", json={
                "username": payload,
                "password": payload,
            })
            
            # Assert
            assert response.status_code == 401
            assert "Invalid credentials" in response.json()["message"]
    
    async def test_brute_force_protection(self, client: AsyncClient):
        """测试暴力破解防护"""
        # Arrange
        attempts = 6
        
        # Act
        for i in range(attempts):
            response = await client.post("/api/v1/auth/login", json={
                "username": "testuser",
                "password": f"wrongpassword{i}",
            })
        
        # Assert
        assert response.status_code == 403
        assert "Account locked" in response.json()["message"]
    
    async def test_jwt_tampering(self, client: AsyncClient):
        """测试 JWT 篡改防护"""
        # Arrange
        tampered_token = "YOUR_SECRET"
        
        # Act
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {tampered_token}"}
        )
        
        # Assert
        assert response.status_code == 401

@pytest.mark.security
class TestInputValidation:
    async def test_xss_prevention(self, client: AsyncClient, auth_token: str):
        """测试 XSS 防护"""
        # Arrange
        xss_payload = '<script>alert("xss")</script>'
        
        # Act
        response = await client.post(
            "/api/v1/chat/stream",
            json={"message": xss_payload},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Assert - 响应中不应包含未转义的脚本
        response_text = response.text
        assert "<script>" not in response_text
```

---

## 8. 测试自动化

### 8.1 CI/CD 集成

```yaml
# .github/workflows/test.yml
name: Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  backend-test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          cd gateway
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run unit tests
        run: |
          cd gateway
          pytest tests/unit -v --cov=app --cov-report=xml
      
      - name: Run integration tests
        run: |
          cd gateway
          pytest tests/integration -v
        env:
          DATABASE_URL: postgresql+asyncpg://test:test@localhost:5432/test
          REDIS_URL: redis://localhost:6379/0
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./gateway/coverage.xml

  frontend-test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run unit tests
        run: |
          cd frontend
          npm test -- --coverage
      
      - name: Run e2e tests
        run: |
          cd frontend
          npx playwright install
          npm run test:e2e
      
      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: frontend/playwright-report/
```

### 8.2 测试覆盖率要求

| 模块 | 单元测试覆盖率 | 集成测试覆盖率 |
|------|---------------|---------------|
| **认证模块** | >= 90% | >= 80% |
| **会话模块** | >= 90% | >= 80% |
| **对话模块** | >= 85% | >= 80% |
| **Agent 模块** | >= 85% | >= 75% |
| **MCP 模块** | >= 80% | >= 75% |
| **管理后台** | >= 80% | >= 70% |
| **前端组件** | >= 80% | >= 70% |

---

## 9. 测试报告

### 9.1 测试报告模板

```markdown
# 测试报告 - v1.0.0

## 测试概况
- **测试时间**: 2026-04-21 ~ 2026-04-28
- **测试范围**: 全部功能模块
- **测试环境**: 测试环境
- **测试人员**: QA 团队

## 测试结果统计

| 测试类型 | 用例总数 | 通过 | 失败 | 跳过 | 通过率 |
|----------|---------|------|------|------|--------|
| 单元测试 | 500 | 495 | 3 | 2 | 99.0% |
| 集成测试 | 150 | 145 | 4 | 1 | 96.7% |
| E2E 测试 | 80 | 78 | 2 | 0 | 97.5% |
| 性能测试 | 20 | 18 | 2 | 0 | 90.0% |
| 安全测试 | 50 | 50 | 0 | 0 | 100% |

## 缺陷统计

| 严重程度 | 数量 | 状态 |
|----------|------|------|
| 致命 | 0 | - |
| 严重 | 2 | 已修复 |
| 一般 | 5 | 已修复 3，待修复 2 |
| 轻微 | 8 | 已修复 6，待修复 2 |

## 风险与建议

1. **性能风险**: 并发 500 用户时 P95 响应时间接近阈值
   - 建议：优化数据库查询，增加缓存

2. **安全风险**: 无高危漏洞
   - 建议：定期进行安全扫描

## 测试结论

系统功能基本满足需求，性能需要优化，建议修复剩余缺陷后发布。
```

---

**文档结束**
