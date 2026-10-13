# 07 - 安全设计文档

**项目名称**：AI Agent 对话平台  
**版本**：v1.0  
**日期**：2026-04-21  
**编写人**：AI Agent 团队  
**目标读者**：安全工程师、后端开发、DevOps、架构师

---

## 目录

1. [安全概述](#1-安全概述)
2. [威胁模型](#2-威胁模型)
3. [认证与授权](#3-认证与授权)
4. [传输安全](#4-传输安全)
5. [数据安全](#5-数据安全)
6. [MCP 工具安全](#6-mcp-工具安全)
7. [OpenCode Server 安全](#7-opencode-server-安全)
8. [输入验证与防护](#8-输入验证与防护)
9. [审计与监控](#9-审计与监控)
10. [安全响应](#10-安全响应)
11. [合规要求](#11-合规要求)

---

## 1. 安全概述

### 1.1 安全目标

1. **保密性**：保护用户数据和对话内容不被未授权访问
2. **完整性**：确保数据在传输和存储过程中不被篡改
3. **可用性**：防止服务被拒绝访问（DoS/DDoS）
4. **可追溯性**：记录所有关键操作，支持审计追踪

### 1.2 安全原则

- **纵深防御**：多层安全控制，单点失效不导致整体沦陷
- **最小权限**：每个组件和用户仅拥有必要的最小权限
- **安全默认**：所有功能默认关闭，显式启用
- ** fail-safe**：故障时进入安全状态
- **不信任输入**：所有外部输入视为不可信

---

## 2. 威胁模型

### 2.1 威胁参与者

| 威胁参与者 | 能力 | 动机 |
|-----------|------|------|
| **外部攻击者** | 互联网访问、自动化工具 | 数据窃取、服务破坏 |
| **恶意用户** | 合法账号访问 | 越权访问、资源滥用 |
| **内部人员** | 系统内部访问 | 数据泄露、权限提升 |
| **供应链攻击者** | MCP/依赖组件 | 植入后门、数据窃取 |

### 2.2 威胁矩阵

| 威胁 | 影响 | 可能性 | 风险等级 | 缓解措施 |
|------|------|--------|----------|----------|
| **会话劫持** | 高 | 中 | 高 | JWT + HTTPS + 短时效 |
| **Prompt 注入** | 高 | 高 | 高 | 输入过滤 + 权限隔离 |
| **MCP 权限逃逸** | 高 | 中 | 高 | 沙箱 + 白名单 |
| **数据泄露** | 高 | 低 | 中 | 加密 + 访问控制 |
| **DoS 攻击** | 中 | 高 | 中 | 速率限制 + CDN |
| **供应链攻击** | 高 | 低 | 中 | 依赖扫描 + 签名验证 |

---

## 3. 认证与授权

### 3.1 认证架构

```
用户登录 → 验证凭据 → 颁发 Token → 后续请求携带 Token
    ↓
Token 验证 → 权限检查 → 访问资源
```

### 3.2 JWT 设计

**Token 结构**：

```
Header: { "alg": "RS256", "typ": "JWT" }
Payload: {
  "sub": "user-uuid",
  "username": "john_doe",
  "role": "user",
  "iat": 1713691800,
  "exp": 1713692700,      // 15 分钟
  "jti": "token-uuid"     // 唯一标识，用于黑名单
}
Signature: RS256(private_key, header + payload)
```

**Token 类型**：

| Token 类型 | 有效期 | 用途 | 存储位置 |
|-----------|--------|------|----------|
| **Access Token** | 15 分钟 | API 访问 | 内存（前端） |
| **Refresh Token** | 7 天 | 刷新 Access Token | httpOnly Cookie |
| **Remember Token** | 30 天 | "记住我"功能 | httpOnly Cookie |

**密钥管理**：

```python
# 使用非对称加密（RS256）
# 私钥：仅服务端持有，用于签发 Token
# 公钥：可分发，用于验证 Token

import jwt
from cryptography.hazmat.primitives import serialization

# 加载私钥
with open("private_key.pem", "rb") as f:
    private_key = YOUR_SECRET), password=None)

# 加载公钥
with open("public_key.pem", "rb") as f:
    public_key = serialization.load_pem_public_key(f.read())

# 签发 Token
def create_access_token(user_id: str, username: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "username": username,
        "role": role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=15),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, private_key, algorithm="RS256")

# 验证 Token
def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, public_key, algorithms=["RS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")
```

### 3.3 黑名单机制

```python
import redis

class TokenBlacklist:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.key_prefix = "token:YOUR_SECRET"
    
    def blacklist_token(self, jti: str, exp: datetime) -> None:
        """
        将 Token 加入黑名单
        
        有效期 = Token 过期时间 - 当前时间
        """
        ttl = int((exp - datetime.utcnow()).total_seconds())
        if ttl > 0:
            self.redis.setex(f"{self.key_prefix}:{jti}", ttl, "blacklisted")
    
    def is_blacklisted(self, jti: str) -> bool:
        """检查 Token 是否在黑名单中"""
        return self.redis.exists(f"{self.key_prefix}:{jti}") > 0

# 登出时加入黑名单
@app.post("/auth/logout")
async def logout(token_payload: dict = Depends(get_current_token)):
    """用户登出"""
    jti = token_payload["jti"]
    exp = datetime.fromtimestamp(token_payload["exp"])
    
    # 加入黑名单
    token_blacklist.blacklist_token(jti, exp)
    
    return {"message": "Successfully logged out"}
```

### 3.4 OAuth 集成安全

**企业微信 OAuth**：

```python
from fastapi import HTTPException
import httpx

class WechatOAuth:
    def __init__(self, corp_id: str, corp_secret: str):
        self.corp_id = corp_id
        self.corp_secret = corp_secret
        self.token_url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        self.user_info_url = "https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo"
    
    async def get_access_token(self) -> str:
        """获取企业微信 Access Token"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.token_url,
                params={
                    "corpid": self.corp_id,
                    "corpsecret": self.corp_secret,
                }
            )
            data = response.json()
            
            if data.get("errcode") != 0:
                raise HTTPException(status_code=400, detail=data.get("errmsg"))
            
            return data["access_token"]
    
    async def get_user_info(self, code: str) -> dict:
        """通过 code 获取用户信息"""
        access_token = YOUR_SECRET self.get_access_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.user_info_url,
                params={
                    "access_token": access_token,
                    "code": code,
                }
            )
            data = response.json()
            
            if data.get("errcode") != 0:
                raise HTTPException(status_code=400, detail=data.get("errmsg"))
            
            return {
                "user_id": data["UserId"],
                "device_id": data.get("DeviceId"),
            }
```

### 3.5 权限模型

**RBAC（基于角色的访问控制）**：

```python
from enum import Enum
from functools import wraps

class Role(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class Permission(str, Enum):
    # 用户管理
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    
    # 会话管理
    SESSION_CREATE = "session:create"
    SESSION_READ = "session:read"
    SESSION_DELETE = "session:delete"
    SESSION_READ_ALL = "session:read:all"
    
    # Agent 管理
    AGENT_CREATE = "agent:create"
    AGENT_READ = "agent:read"
    AGENT_UPDATE = "agent:update"
    AGENT_DELETE = "agent:delete"
    
    # MCP 管理
    MCP_CREATE = "mcp:create"
    MCP_READ = "mcp:read"
    MCP_UPDATE = "mcp:update"
    MCP_DELETE = "mcp:delete"
    
    # 系统管理
    SYSTEM_CONFIG = "system:config"
    AUDIT_READ = "audit:read"

# 角色权限映射
ROLE_PERMISSIONS = {
    Role.SUPERADMIN: list(Permission),  # 所有权限
    Role.ADMIN: [
        Permission.USER_CREATE,
        Permission.USER_READ,
        Permission.USER_UPDATE,
        Permission.SESSION_READ_ALL,
        Permission.AGENT_CREATE,
        Permission.AGENT_READ,
        Permission.AGENT_UPDATE,
        Permission.MCP_CREATE,
        Permission.MCP_READ,
        Permission.MCP_UPDATE,
        Permission.AUDIT_READ,
    ],
    Role.USER: [
        Permission.USER_READ,
        Permission.SESSION_CREATE,
        Permission.SESSION_READ,
        Permission.SESSION_DELETE,
        Permission.AGENT_CREATE,
        Permission.AGENT_READ,
        Permission.AGENT_UPDATE,
        Permission.MCP_READ,
    ],
    Role.GUEST: [
        Permission.SESSION_READ,
    ],
}

def require_permission(permission: Permission):
    """权限检查装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取当前用户
            user = kwargs.get("current_user")
            if not user:
                raise HTTPException(status_code=401, detail="Not authenticated")
            
            # 检查权限
            user_permissions = ROLE_PERMISSIONS.get(user.role, [])
            if permission not in user_permissions:
                raise HTTPException(status_code=403, detail="Permission denied")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# 使用示例
@app.post("/admin/users")
@require_permission(Permission.USER_CREATE)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user)
):
    """创建用户（需要 user:create 权限）"""
    pass
```

---

## 4. 传输安全

### 4.1 TLS 配置

**Nginx SSL 配置**：

```nginx
server {
    listen 443 ssl http2;
    server_name api.aigateway.example.com;
    
    # SSL 证书
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # TLS 1.3 only
    ssl_protocols TLSv1.3;
    ssl_prefer_server_ciphers off;
    
    # 强加密套件
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';" always;
    
    location / {
        proxy_pass http://gateway:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name api.aigateway.example.com;
    return 301 https://$server_name$request_uri;
}
```

### 4.2 CORS 配置

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.aigateway.example.com",
        "https://admin.aigateway.example.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Request-ID",
    ],
    expose_headers=["X-Request-ID"],
    max_age=600,  # 预检请求缓存 10 分钟
)
```

---

## 5. 数据安全

### 5.1 数据分类

| 数据级别 | 数据类型 | 加密要求 | 访问控制 |
|---------|---------|---------|---------|
| **极高** | 密码哈希、API Key | bcrypt / AES-256 | 仅限系统 |
| **高** | 对话内容、用户配置 | AES-256-GCM | 用户本人 + 管理员 |
| **中** | 用户信息、审计日志 | TLS 传输加密 | 授权用户 |
| **低** | 公开配置、Agent 模板 | TLS 传输加密 | 所有用户 |

### 5.2 密码存储

```python
import bcrypt

class PasswordManager:
    @staticmethod
    def hash_password(password: str) -> str:
        """使用 bcrypt 哈希密码"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode(), salt).decode()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(password.encode(), hashed.encode())

# 使用示例
hashed_password = YOUR_PASSWORD"user_password")
is_valid = PasswordManager.verify_password("user_password", hashed_password)
```

### 5.3 敏感数据脱敏

```python
import re
from typing import Optional

class DataMasker:
    @staticmethod
    def mask_phone(phone: Optional[str]) -> Optional[str]:
        """手机号脱敏：138****1234"""
        if not phone:
            return None
        return re.sub(r'(\d{3})\d{4}(\d{4})', r'\1****\2', phone)
    
    @staticmethod
    def mask_email(email: Optional[str]) -> Optional[str]:
        """邮箱脱敏：j***@example.com"""
        if not email:
            return None
        local, domain = email.split('@')
        if len(local) <= 2:
            return f'{local[0]}***@{domain}'
        return f'{local[0]}{"*" * (len(local) - 2)}{local[-1]}@{domain}'
    
    @staticmethod
    def mask_id_card(id_card: Optional[str]) -> Optional[str]:
        """身份证号脱敏"""
        if not id_card:
            return None
        return id_card[:4] + '*' * (len(id_card) - 8) + id_card[-4:]
    
    @staticmethod
    def mask_api_key(api_key: str) -> str:
        """API Key 脱敏：sk-****abcd"""
        if len(api_key) <= 8:
            return '*' * len(api_key)
        return api_key[:4] + '*' * (len(api_key) - 8) + api_key[-4:]

# 在 API 响应中使用
@app.get("/users/me")
async def get_current_user(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "username": user.username,
        "email": DataMasker.mask_email(user.email),
        "phone": DataMasker.mask_phone(user.phone),
    }
```

### 5.4 数据库加密

**透明数据加密（TDE）配置**：

```sql
-- PostgreSQL pgcrypto 扩展
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 加密列示例
CREATE TABLE secrets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data BYTEA NOT NULL,  -- 加密后的数据
    encrypted_at TIMESTAMPTZ DEFAULT NOW()
);

-- 插入加密数据
INSERT INTO secrets (data)
VALUES (pgp_sym_encrypt('sensitive data', 'encryption_key'));

-- 查询解密数据
SELECT pgp_sym_decrypt(data, 'encryption_key') as plain_data
FROM secrets;
```

---

## 6. MCP 工具安全

### 6.1 MCP 沙箱化

**使用 Firejail 沙箱运行 MCP**：

```bash
# 安装 Firejail
sudo apt-get install firejail

# 创建 MCP 沙箱配置
# /etc/firejail/mcp-filesystem.profile
include /etc/firejail/default.profile

# 限制网络访问
net none

# 限制文件系统访问
whitelist /opt/aigateway/workspaces
read-only /opt/aigateway/workspaces

# 禁止访问敏感目录
blacklist /etc
blacklist /root
blacklist /home

# 资源限制
rlimit-as 512000000  # 512MB 内存
rlimit-cpu 60        # 60 秒 CPU 时间
rlimit-fsize 10485760 # 10MB 文件大小
rlimit-nofile 64     # 64 个文件描述符
```

**systemd 服务配置**：

```ini
# /etc/systemd/system/mcp-filesystem.service
[Unit]
Description=MCP Filesystem Service
After=network.target

[Service]
Type=simple
User=mcp
Group=mcp

# 使用 Firejail 沙箱
ExecStart=/usr/bin/firejail --profile=/etc/firejail/mcp-filesystem.profile \
    python /opt/aigateway/mcp-servers/filesystem.py

# 安全选项
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/aigateway/workspaces

# 资源限制
MemoryMax=512M
CPUQuota=50%
TasksMax=10

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 6.2 命令白名单

```python
# mcp_shell.py
import subprocess
import re
from typing import List, Tuple

class ShellExecutor:
    # 允许的命令白名单
    ALLOWED_COMMANDS = {
        'git': ['status', 'log', 'diff', 'branch', 'clone', 'pull', 'push'],
        'python': ['--version', '-m', '-c'],
        'ls': ['-la', '-l', '-a'],
        'cat': [],
        'grep': ['-r', '-i', '-n'],
        'find': ['-name', '-type', '-size'],
        'wc': ['-l', '-w', '-c'],
        'head': ['-n'],
        'tail': ['-n'],
        'sort': [],
        'uniq': ['-c'],
    }
    
    # 禁止的模式
    FORBIDDEN_PATTERNS = [
        r'rm\s+-rf',
        r'>&/dev/tcp',
        r'bash\s+-i',
        r'nc\s+-e',
        r'curl\s+.*\|',
        r'wget\s+.*\|',
        r'eval\s*\(',
        r'exec\s*\(',
    ]
    
    @classmethod
    def validate_command(cls, command: str) -> Tuple[bool, str]:
        """验证命令是否允许执行"""
        # 检查禁止模式
        for pattern in cls.FORBIDDEN_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return False, f"Command contains forbidden pattern: {pattern}"
        
        # 解析命令
        parts = command.split()
        if not parts:
            return False, "Empty command"
        
        cmd = parts[0]
        
        # 检查命令是否在白名单
        if cmd not in cls.ALLOWED_COMMANDS:
            return False, f"Command '{cmd}' is not in whitelist"
        
        # 检查参数
        allowed_args = cls.ALLOWED_COMMANDS[cmd]
        for arg in parts[1:]:
            if arg.startswith('-') and arg not in allowed_args:
                return False, f"Argument '{arg}' is not allowed for command '{cmd}'"
        
        return True, ""
    
    @classmethod
    def execute(cls, command: str, timeout: int = 30) -> dict:
        """安全执行命令"""
        # 验证命令
        is_valid, error = cls.validate_command(command)
        if not is_valid:
            return {
                "success": False,
                "error": error,
                "stdout": "",
                "stderr": "",
            }
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd="/opt/aigateway/workspaces",  # 限制工作目录
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds",
                "stdout": "",
                "stderr": "",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": "",
            }
```

### 6.3 文件系统隔离

```python
import os
from pathlib import Path

class WorkspaceManager:
    BASE_PATH = Path("/opt/aigateway/workspaces")
    
    @classmethod
    def get_workspace_path(cls, user_id: str, session_id: str) -> Path:
        """获取用户会话工作区路径"""
        return cls.BASE_PATH / user_id / session_id
    
    @classmethod
    def validate_path(cls, user_id: str, session_id: str, requested_path: str) -> Path:
        """
        验证并解析路径
        
        防止目录遍历攻击
        """
        workspace = cls.get_workspace_path(user_id, session_id)
        
        # 解析请求路径
        if requested_path.startswith('/'):
            # 绝对路径：必须是工作区子目录
            requested = Path(requested_path).resolve()
        else:
            # 相对路径：相对于工作区
            requested = (workspace / requested_path).resolve()
        
        # 确保路径在工作区内
        try:
            requested.relative_to(workspace)
        except ValueError:
            raise PermissionError(f"Path '{requested_path}' is outside workspace")
        
        return requested
    
    @classmethod
    def read_file(cls, user_id: str, session_id: str, file_path: str) -> str:
        """安全读取文件"""
        path = cls.validate_path(user_id, session_id, file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        # 检查文件大小（防止读取大文件导致内存溢出）
        max_size = 10 * 1024 * 1024  # 10MB
        if path.stat().st_size > max_size:
            raise ValueError(f"File too large (max {max_size} bytes)")
        
        return path.read_text()
    
    @classmethod
    def write_file(cls, user_id: str, session_id: str, file_path: str, content: str) -> None:
        """安全写入文件"""
        path = cls.validate_path(user_id, session_id, file_path)
        
        # 确保父目录存在
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        path.write_text(content)
```

---

## 7. OpenCode Server 安全

### 7.1 网络隔离

```bash
# 使用防火墙限制访问
sudo ufw allow from 127.0.0.1 to any port 4096 proto tcp
sudo ufw deny from any to any port 4096 proto tcp

# 或使用 iptables
sudo iptables -A INPUT -p tcp --dport 4096 -s 127.0.0.1 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 4096 -j DROP
```

### 7.2 认证加固

```python
# 强密码策略
import secrets
import string

def generate_secure_password(length: int = 32) -> str:
    """生成强密码"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# 定期轮换密码
import schedule
import time

def rotate_opencode_password():
    """定期轮换 OpenCode Server 密码"""
    new_password = YOUR_PASSWORD)
    
    # 更新环境变量
    os.environ['OPENCODE_SERVER_PASSWORD'] = new_password
    
    # 重启服务
    subprocess.run(['sudo', 'systemctl', 'restart', 'opencode'])
    
    # 更新网关配置
    update_gateway_config(new_password)
    
    # 记录日志
    audit_log.info("OpenCode Server password rotated")

# 每周轮换一次
schedule.every().sunday.at("02:00").do(rotate_opencode_password)
```

### 7.3 输入过滤

```python
import re
from typing import List

class PromptFilter:
    # 危险关键词
    DANGEROUS_PATTERNS = [
        r'ignore\s+(?:previous|all|the)\s+instructions',
        r'forget\s+(?:previous|all|the)\s+instructions',
        r'disregard\s+(?:previous|all|the)\s+instructions',
        r'you\s+are\s+now\s+(?:a|an)\s+',
        r'system\s*:\s*',
        r'user\s*:\s*',
        r'assistant\s*:\s*',
        r'\u003c\s*system\s*\u003e',
        r'\u003c\s*instructions\s*\u003e',
        r'DAN\s*\(Do\s+Anything\s+Now\)',
        r'jailbreak',
        r'prompt\s+injection',
    ]
    
    @classmethod
    def filter_prompt(cls, prompt: str) -> tuple[bool, str, List[str]]:
        """
        过滤用户输入
        
        Returns:
            (is_safe, filtered_prompt, matched_patterns)
        """
        matched_patterns = []
        
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, prompt, re.IGNORECASE):
                matched_patterns.append(pattern)
        
        if matched_patterns:
            # 发现危险模式，可以选择：
            # 1. 拒绝请求
            # 2. 过滤危险内容
            # 3. 记录并告警
            
            # 这里选择过滤
            filtered = prompt
            for pattern in cls.DANGEROUS_PATTERNS:
                filtered = re.sub(pattern, '[FILTERED]', filtered, flags=re.IGNORECASE)
            
            return False, filtered, matched_patterns
        
        return True, prompt, []

# 在网关层使用
@app.post("/api/v1/chat/stream")
async def chat_stream(request: ChatRequest):
    # 过滤用户输入
    is_safe, filtered_message, patterns = PromptFilter.filter_prompt(request.message)
    
    if not is_safe:
        # 记录安全事件
        security_log.warning(
            f"Potential prompt injection detected",
            extra={
                "user_id": current_user.id,
                "patterns": patterns,
                "original_message": request.message,
            }
        )
        
        # 可选：拒绝请求或继续处理过滤后的内容
        # return JSONResponse(
        #     status_code=400,
        #     content={"error": "Potentially dangerous content detected"}
        # )
    
    # 使用过滤后的消息
    request.message = filtered_message
    
    # 继续处理...
```

---

## 8. 输入验证与防护

### 8.1 SQL 注入防护

```python
from sqlalchemy import text
from sqlalchemy.orm import Session

# 错误示例（不要这样做）
# query = f"SELECT * FROM users WHERE username = '{username}'"

# 正确做法：使用参数化查询
def get_user_by_username(db: Session, username: str):
    query = text("SELECT * FROM users WHERE username = :username")
    result = db.execute(query, {"username": username})
    return result.fetchone()

# 使用 ORM
def get_user_by_username_orm(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()
```

### 8.2 XSS 防护

```python
from html import escape

class XSSFilter:
    @staticmethod
    def sanitize_html(content: str) -> str:
        """转义 HTML 特殊字符"""
        return escape(content)
    
    @staticmethod
    def sanitize_markdown(content: str) -> str:
        """
        清理 Markdown 中的危险内容
        
        注意：前端使用 react-markdown 渲染时，
        已经默认转义了 HTML，这里做二次防护
        """
        # 移除危险的 HTML 标签
        import re
        dangerous_tags = ['script', 'iframe', 'object', 'embed', 'form']
        for tag in dangerous_tags:
            content = re.sub(
                rf'<{tag}[^\u003e]*\u003e.*?</{tag}\u003e',
                '',
                content,
                flags=re.DOTALL | re.IGNORECASE
            )
        
        return content

# 在 API 响应中使用
@app.get("/api/v1/sessions/{session_id}/messages")
async def get_messages(session_id: str):
    messages = await message_service.get_messages(session_id)
    
    # 清理内容
    for message in messages:
        message.content = XSSFilter.sanitize_markdown(message.content)
    
    return {"items": messages}
```

### 8.3 文件上传安全

```python
import magic
from pathlib import Path
from typing import Optional

class FileUploadValidator:
    # 允许的文件类型
    ALLOWED_MIME_TYPES = {
        'text/plain',
        'text/markdown',
        'text/x-python',
        'application/javascript',
        'application/json',
        'application/yaml',
        'text/csv',
        'application/pdf',
        'image/png',
        'image/jpeg',
    }
    
    # 允许的文件扩展名
    ALLOWED_EXTENSIONS = {
        '.txt', '.md', '.py', '.js', '.ts', '.json', '.yaml', '.yml',
        '.csv', '.pdf', '.png', '.jpg', '.jpeg'
    }
    
    # 最大文件大小：10MB
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    @classmethod
    def validate_file(cls, file: bytes, filename: str) -> tuple[bool, str]:
        """验证上传文件"""
        # 检查文件大小
        if len(file) > cls.MAX_FILE_SIZE:
            return False, f"File too large (max {cls.MAX_FILE_SIZE} bytes)"
        
        # 检查文件扩展名
        ext = Path(filename).suffix.lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            return False, f"File type '{ext}' is not allowed"
        
        # 检查 MIME 类型（使用 python-magic）
        mime_type = magic.from_buffer(file, mime=True)
        if mime_type not in cls.ALLOWED_MIME_TYPES:
            return False, f"MIME type '{mime_type}' is not allowed"
        
        # 检查文件内容（防止伪造扩展名）
        # 例如：检查 PNG 文件头
        if ext == '.png' and not file.startswith(b'\x89PNG'):
            return False, "Invalid PNG file"
        
        return True, ""
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """清理文件名"""
        import re
        
        # 移除路径遍历
        filename = Path(filename).name
        
        # 移除危险字符
        filename = re.sub(r'[^\w\-.]', '_', filename)
        
        # 限制长度
        if len(filename) > 255:
            name = Path(filename).stem[:250]
            ext = Path(filename).suffix
            filename = f"{name}{ext}"
        
        return filename
```

---

## 9. 审计与监控

### 9.1 审计日志

```python
import json
import logging
from datetime import datetime
from typing import Any, Optional

class AuditLogger:
    def __init__(self):
        self.logger = logging.getLogger("audit")
        
        # 配置审计日志处理器
        handler = logging.FileHandler("/var/log/aigateway/audit.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log(
        self,
        action: str,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None,
    ):
        """记录审计日志"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "user_id": user_id,
            "username": username,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
            "ip_address": ip_address,
            "user_agent": user_agent,
            "status": status,
            "error_message": error_message,
        }
        
        # 记录为 JSON
        self.logger.info(json.dumps(log_entry))
        
        # 同时写入数据库
        asyncio.create_task(self._persist_to_db(log_entry))
    
    async def _persist_to_db(self, log_entry: dict):
        """持久化到数据库"""
        # 使用异步写入
        pass

# 全局实例
audit_logger = AuditLogger()

# 使用示例
@app.post("/api/v1/sessions")
async def create_session(
    request: Request,
    user: User = Depends(get_current_user)
):
    session = await session_service.create(user.id)
    
    audit_logger.log(
        action="create_session",
        user_id=user.id,
        username=user.username,
        resource_type="session",
        resource_id=str(session.id),
        details={"title": session.title},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )
    
    return session
```

### 9.2 安全监控

```python
from prometheus_client import Counter, Histogram, Gauge

# 安全相关指标
security_events_total = Counter(
    'security_events_total',
    'Total security events',
    ['event_type', 'severity']
)

failed_logins_total = Counter(
    'failed_logins_total',
    'Total failed login attempts',
    ['username', 'ip_address']
)

rate_limit_hits_total = Counter(
    'rate_limit_hits_total',
    'Total rate limit hits',
    ['endpoint', 'user_id']
)

suspicious_activities_total = Counter(
    'suspicious_activities_total',
    'Total suspicious activities',
    ['activity_type']
)

# 使用示例
@app.post("/api/v1/auth/login")
async def login(request: LoginRequest, http_request: Request):
    user = await authenticate_user(request.username, request.password)
    
    if not user:
        # 记录失败登录
        failed_logins_total.labels(
            username=request.username,
            ip_address=http_request.client.host
        ).inc()
        
        # 检查是否需要锁定账号
        await check_account_lockout(request.username)
        
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"access_token": create_token(user)}
```

---

## 10. 安全响应

### 10.1 应急响应流程

```
检测异常 → 确认事件 → 遏制影响 → 根除威胁 → 恢复服务 → 事后总结
    ↑        |          |          |          |           |
    └────────┴──────────┴──────────┴──────────┘           |
         ↑                                               |
         └───────────────────────────────────────────────┘
                    持续监控
```

### 10.2 自动响应机制

```python
import asyncio
from datetime import datetime, timedelta

class SecurityResponder:
    def __init__(self):
        self.blocked_ips = set()
        self.suspicious_users = {}
    
    async def handle_failed_login(self, username: str, ip_address: str):
        """处理失败登录"""
        # 记录失败次数
        key = f"{username}:{ip_address}"
        
        if key not in self.suspicious_users:
            self.suspicious_users[key] = {
                "count": 0,
                "first_attempt": datetime.now(),
            }
        
        self.suspicious_users[key]["count"] += 1
        
        # 检查是否需要锁定
        if self.suspicious_users[key]["count"] >= 5:
            # 锁定账号 30 分钟
            await self.lock_account(username, timedelta(minutes=30))
            
            # 发送告警
            await self.send_alert(
                f"Account {username} locked due to multiple failed login attempts"
            )
        
        # 检查是否需要封禁 IP
        if self.suspicious_users[key]["count"] >= 10:
            await self.block_ip(ip_address)
    
    async def lock_account(self, username: str, duration: timedelta):
        """锁定账号"""
        # 写入 Redis
        await redis.setex(
            f"lockout:{username}",
            int(duration.total_seconds()),
            "locked"
        )
    
    async def block_ip(self, ip_address: str):
        """封禁 IP"""
        self.blocked_ips.add(ip_address)
        
        # 写入防火墙
        subprocess.run([
            "iptables", "-A", "INPUT", "-s", ip_address, "-j", "DROP"
        ])
    
    async def send_alert(self, message: str):
        """发送安全告警"""
        # 发送到企业微信
        await send_wechat_alert(message)
        
        # 发送邮件
        await send_email_alert(
            to="security@example.com",
            subject="Security Alert",
            body=message
        )

# 初始化响应器
security_responder = SecurityResponder()
```

---

## 11. 合规要求

### 11.1 数据保护

- **GDPR**（如适用）：用户数据可删除、可导出
- **网络安全法**：数据本地化存储
- **等保 2.0**：三级等保要求

### 11.2 密码策略

```python
import re
from typing import Tuple

class PasswordPolicy:
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        验证密码复杂度
        
        要求：
        - 至少 8 位
        - 包含大写字母
        - 包含小写字母
        - 包含数字
        - 包含特殊字符
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain digit"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>\-_=+\[\]\\;/`~]', password):
            return False, "Password must contain special character"
        
        # 检查常见弱密码
        common_passwords = ['password', '123456', 'qwerty', 'admin']
        if password.lower() in common_passwords:
            return False, "Password is too common"
        
        return True, "Password is valid"
```

### 11.3 日志保留

| 日志类型 | 保留期限 | 存储位置 |
|----------|----------|----------|
| 访问日志 | 1 年 | 文件系统 |
| 审计日志 | 7 年 | 数据库 + 对象存储 |
| 错误日志 | 90 天 | 日志系统 |
| 安全事件 | 永久 | 数据库 + 对象存储 |

---

**文档结束**
