# 08 - 部署与运维文档

**项目名称**：AI Agent 对话平台  
**版本**：v1.0  
**日期**：2026-04-21  
**编写人**：AI Agent 团队  
**目标读者**：DevOps、运维工程师、系统管理员

---

## 目录

1. [部署架构](#1-部署架构)
2. [环境准备](#2-环境准备)
3. [Docker Compose 部署](#3-docker-compose-部署)
4. [生产环境部署](#4-生产环境部署)
5. [OpenCode Server 部署](#5-opencode-server-部署)
6. [Nginx 配置](#6-nginx-配置)
7. [SSL/TLS 配置](#7-ssltls-配置)
8. [监控告警](#8-监控告警)
9. [日志管理](#9-日志管理)
10. [备份恢复](#10-备份恢复)
11. [运维脚本](#11-运维脚本)
12. [故障排查](#12-故障排查)

---

## 1. 部署架构

### 1.1 生产环境拓扑

```
                      ┌─────────────┐
                      │   公网用户   │
                      └──────┬──────┘
                             │
                      ┌──────▼──────┐
                      │  Cloudflare │  ← DDoS 防护 + CDN（可选）
                      │   / 企业防火墙 │
                      └──────┬──────┘
                             │
                      ┌──────▼──────┐
                      │    Nginx    │  ← SSL 终结、静态资源、反向代理
                      │  (443端口)  │
                      └──────┬──────┘
                             │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
    ┌────▼────┐        ┌─────▼─────┐       ┌────▼────┐
    │  React  │        │  FastAPI  │       │  React  │
    │ 静态资源 │        │  Gateway  │       │ Admin   │
    │(Nginx直出)│       │ (8000端口)│       │ 后台    │
    └─────────┘        └─────┬─────┘       └─────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
               ┌────▼────┐      ┌────▼────┐
               │PostgreSQL│      │  Redis  │
               │ (5432)  │      │ (6379)  │
               └─────────┘      └─────────┘
                    │
               ┌────▼────┐
               │OpenCode  │
               │Server    │
               │(4096本地) │
               └─────────┘
                    │
               ┌────▼────┐
               │ MCP Svrs │
               └─────────┘
```

### 1.2 服务器规划

| 服务器 | 配置 | 用途 | 数量 |
|--------|------|------|------|
| **Web 服务器** | 4核 8G | Nginx + 静态资源 | 1-2 |
| **应用服务器** | 8核 16G | FastAPI Gateway | 2+ |
| **数据库服务器** | 8核 32G | PostgreSQL + Redis | 1-2 |
| **AI 引擎服务器** | 16核 64G | OpenCode + MCP | 2+ |

---

## 2. 环境准备

### 2.1 系统要求

- **操作系统**：Ubuntu 22.04/24.04 LTS
- **内核版本**：5.15+
- **Docker**：24.x
- **Docker Compose**：2.x

### 2.2 系统初始化

```bash
#!/bin/bash
# init-server.sh

# 更新系统
sudo apt-get update && sudo apt-get upgrade -y

# 安装基础工具
sudo apt-get install -y \
    curl \
    wget \
    git \
    vim \
    htop \
    tree \
    jq \
    net-tools \
    dnsutils \
    certbot \
    python3-certbot-nginx

# 安装 Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 安装 Node.js (for OpenCode)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 系统优化
echo "fs.file-max = 65535" | sudo tee -a /etc/sysctl.conf
echo "net.core.somaxconn = 65535" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# 配置时区
sudo timedatectl set-timezone Asia/Shanghai

# 创建用户
sudo useradd -r -s /bin/false opencode
sudo useradd -r -s /bin/false mcp

# 创建目录
sudo mkdir -p /opt/aigateway/{gateway,frontend,admin,mcp-servers,workspaces,logs,backups}
sudo chown -R opencode:opencode /opt/aigateway
```

---

## 3. Docker Compose 部署

### 3.1 项目结构

```
aigateway/
├── docker-compose.yml
├── .env
├── gateway/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
├── frontend/
│   ├── Dockerfile
│   └── dist/
├── admin/
│   ├── Dockerfile
│   └── dist/
├── nginx/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── ssl/
├── postgres/
│   └── init.sql
└── redis/
    └── redis.conf
```

### 3.2 docker-compose.yml

```yaml
version: "3.8"

services:
  # Gateway 服务
  gateway:
    build:
      context: ./gateway
      dockerfile: Dockerfile
    container_name: aigateway-gateway
    restart: always
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/aigateway
      - REDIS_URL=redis://redis:6379/0
      - OPENCODE_SERVER=http://host.docker.internal:4096
      - OPENCODE_USERNAME=gateway
      - OPENCODE_PASSWORD=YOUR_PASSWORD}
      - JWT_SECRET=${JWT_SECRET}
      - ENVIRONMENT=production
    volumes:
      - /opt/aigateway/logs:/app/logs
      - /opt/aigateway/workspaces:/app/workspaces
    depends_on:
      - postgres
      - redis
    networks:
      - aigateway-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # PostgreSQL 数据库
  postgres:
    image: postgres:15-alpine
    container_name: aigateway-postgres
    restart: always
    environment:
      POSTGRES_DB: aigateway
      POSTGRES_USER: aigateway
      POSTGRES_PASSWORD: YOUR_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
      - /opt/aigateway/backups:/backups
    ports:
      - "5432:5432"
    networks:
      - aigateway-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U aigateway -d aigateway"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis 缓存
  redis:
    image: redis:7-alpine
    container_name: aigateway-redis
    restart: always
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
      - ./redis/redis.conf:/usr/local/etc/redis/redis.conf
    ports:
      - "6379:6379"
    networks:
      - aigateway-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # 前端应用
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: aigateway-frontend
    restart: always
    depends_on:
      - gateway
    networks:
      - aigateway-network

  # 管理后台
  admin:
    build:
      context: ./admin
      dockerfile: Dockerfile
    container_name: aigateway-admin
    restart: always
    depends_on:
      - gateway
    networks:
      - aigateway-network

  # Nginx 反向代理
  nginx:
    image: nginx:1.24-alpine
    container_name: aigateway-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - /opt/aigateway/logs/nginx:/var/log/nginx
    depends_on:
      - gateway
      - frontend
      - admin
    networks:
      - aigateway-network

volumes:
  postgres_data:
  redis_data:

networks:
  aigateway-network:
    driver: bridge
```

### 3.3 环境变量文件

```bash
# .env
# 数据库密码
POSTGRES_PASSWORD=YOUR_PASSWORD

# OpenCode 认证
OPENCODE_PASSWORD=YOUR_PASSWORD

# JWT 密钥
JWT_SECRET=your-super-secret-jwt-key-min-32-characters

# 环境
ENVIRONMENT=production

# 域名
DOMAIN=api.aigateway.example.com
ADMIN_DOMAIN=admin.aigateway.example.com
```

### 3.4 启动命令

```bash
# 构建并启动
docker-compose up -d --build

# 查看日志
docker-compose logs -f gateway

# 停止服务
docker-compose down

# 重启服务
docker-compose restart gateway

# 更新服务
docker-compose pull
docker-compose up -d
```

---

## 4. 生产环境部署

### 4.1 裸机部署

#### 4.1.1 Gateway 部署

```bash
# 创建虚拟环境
python3 -m venv /opt/aigateway/gateway/venv
source /opt/aigateway/gateway/venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置 systemd 服务
sudo tee /etc/systemd/system/aigateway-gateway.service <<EOF
[Unit]
Description=AI Gateway FastAPI Service
After=network.target

[Service]
Type=simple
User=opencode
Group=opencode
WorkingDirectory=/opt/aigateway/gateway
Environment="PATH=/opt/aigateway/gateway/venv/bin"
Environment="DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/aigateway"
Environment="REDIS_URL=redis://localhost:6379/0"
Environment="OPENCODE_SERVER=http://127.0.0.1:4096"
ExecStart=/opt/aigateway/gateway/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable aigateway-gateway
sudo systemctl start aigateway-gateway
```

#### 4.1.2 前端部署

```bash
# 构建前端
cd /opt/aigateway/frontend
npm install
npm run build

# Nginx 配置静态资源
sudo tee /etc/nginx/conf.d/frontend.conf <<EOF
server {
    listen 80;
    server_name app.aigateway.example.com;
    
    location / {
        root /opt/aigateway/frontend/dist;
        try_files \$uri \$uri/ /index.html;
        
        # 缓存静态资源
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
EOF

sudo nginx -t
sudo systemctl reload nginx
```

---

## 5. OpenCode Server 部署

### 5.1 安装 OpenCode

```bash
# 安装 opencode-ai
npm install -g opencode-ai

# 验证安装
opencode --version
```

### 5.2 配置 systemd 服务

```bash
sudo tee /etc/systemd/system/opencode.service <<EOF
[Unit]
Description=OpenCode Agent Server
After=network.target

[Service]
Type=simple
User=opencode
Group=opencode
WorkingDirectory=/opt/opencode

Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="OPENCODE_SERVER_PASSWORD=YOUR_PASSWORD}"
Environment="OPENCODE_SERVER_USERNAME=gateway"
Environment="OPENCODE_API_KEY=YOUR_SECRET}"
Environment="OPENCODE_MODEL=anthropic/claude-sonnet-4-20250514"
Environment="HOME=/opt/opencode"

ExecStart=/usr/local/bin/opencode serve --port 4096 --hostname 127.0.0.1
ExecReload=/bin/kill -HUP \$MAINPID

Restart=always
RestartSec=5
StartLimitInterval=60s
StartLimitBurst=3

# 资源限制
LimitNOFILE=65536
LimitNPROC=4096

# 安全选项
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/aigateway/workspaces

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable opencode
sudo systemctl start opencode
```

### 5.3 配置工作区

```bash
# 创建工作区目录结构
sudo mkdir -p /opt/aigateway/workspaces/{templates,backups}

# 创建工作区模板
sudo tee /opt/aigateway/workspaces/templates/config.json <<EOF
{
  "\$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-20250514",
  "permission": {
    "edit": "ask",
    "bash": "ask"
  },
  "tools": {
    "read": true,
    "write": true,
    "edit": true,
    "bash": true
  }
}
EOF

# 设置权限
sudo chown -R opencode:opencode /opt/aigateway/workspaces
sudo chmod -R 755 /opt/aigateway/workspaces
```

---

## 6. Nginx 配置

### 6.1 主配置文件

```nginx
# /etc/nginx/nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    '$request_time $upstream_response_time';

    access_log /var/log/nginx/access.log main;

    # 性能优化
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # 限流
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    # 包含站点配置
    include /etc/nginx/conf.d/*.conf;
}
```

### 6.2 API 站点配置

```nginx
# /etc/nginx/conf.d/api.conf
upstream gateway {
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
    # 多实例时添加
    # server 127.0.0.1:8001 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name api.aigateway.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.aigateway.example.com;

    # SSL 证书
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # 安全头
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # 限流
    limit_req zone=api burst=20 nodelay;

    # API 代理
    location / {
        proxy_pass http://gateway;
        proxy_http_version 1.1;
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # SSE 支持
        proxy_set_header Connection '';
        proxy_buffering off;
        proxy_cache off;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 健康检查
    location /health {
        proxy_pass http://gateway/health;
        access_log off;
    }
}
```

---

## 7. SSL/TLS 配置

### 7.1 Let's Encrypt 证书

```bash
# 安装 Certbot
sudo apt-get install certbot python3-certbot-nginx

# 申请证书
sudo certbot --nginx -d api.aigateway.example.com -d app.aigateway.example.com

# 自动续期
sudo certbot renew --dry-run

# 添加定时任务
sudo tee /etc/cron.d/certbot-renew <<EOF
0 2 * * * root /usr/bin/certbot renew --quiet --deploy-hook "systemctl reload nginx"
EOF
```

### 7.2 自签名证书（开发环境）

```bash
# 生成私钥
openssl genrsa -out /etc/nginx/ssl/key.pem 2048

# 生成证书请求
openssl req -new -key /etc/nginx/ssl/key.pem -out /etc/nginx/ssl/csr.pem \
    -subj "/C=CN/ST=Beijing/L=Beijing/O=AI Gateway/OU=Dev/CN=localhost"

# 生成自签名证书
openssl x509 -req -days 365 -in /etc/nginx/ssl/csr.pem \
    -signkey /etc/nginx/ssl/key.pem -out /etc/nginx/ssl/cert.pem

# 设置权限
sudo chmod 600 /etc/nginx/ssl/key.pem
sudo chmod 644 /etc/nginx/ssl/cert.pem
```

---

## 8. 监控告警

### 8.1 Prometheus 配置

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']

rule_files:
  - /etc/prometheus/rules/*.yml

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'gateway'
    static_configs:
      - targets: ['gateway:8000']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```

### 8.2 告警规则

```yaml
# rules/alerts.yml
groups:
  - name: aigateway
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is above 10% for 5 minutes"

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          description: "P95 latency is above 10 seconds"

      - alert: OpenCodeDown
        expr: up{job="opencode"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "OpenCode Server is down"
          description: "OpenCode Server has been down for more than 1 minute"

      - alert: HighTokenUsage
        expr: rate(tokens_total[1h]) > 100000
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High token usage"
          description: "Token usage is above 100k per hour"
```

### 8.3 Grafana 仪表盘

```json
{
  "dashboard": {
    "title": "AI Gateway Overview",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{status}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "P95"
          },
          {
            "expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "P99"
          }
        ]
      },
      {
        "title": "Active Sessions",
        "type": "stat",
        "targets": [
          {
            "expr": "active_sessions_total",
            "legendFormat": "Active Sessions"
          }
        ]
      },
      {
        "title": "Token Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(tokens_total[1h])",
            "legendFormat": "Tokens/hour"
          }
        ]
      }
    ]
  }
}
```

---

## 9. 日志管理

### 9.1 日志配置

```python
# logging_config.py
import logging
import logging.handlers
from pythonjsonlogger import jsonlogger

LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s %(message)s'
JSON_FORMAT = '%(timestamp)s %(level)s %(name)s %(message)s'

def setup_logging():
    # 根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    root_logger.addHandler(console_handler)
    
    # 文件处理器（JSON 格式）
    file_handler = logging.handlers.RotatingFileHandler(
        '/opt/aigateway/logs/app.log',
        maxBytes=100*1024*1024,  # 100MB
        backupCount=10
    )
    json_formatter = jsonlogger.JsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s '
        '%(user_id)s %(session_id)s %(trace_id)s'
    )
    file_handler.setFormatter(json_formatter)
    root_logger.addHandler(file_handler)
    
    # 错误日志单独文件
    error_handler = logging.handlers.RotatingFileHandler(
        '/opt/aigateway/logs/error.log',
        maxBytes=100*1024*1024,
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(json_formatter)
    root_logger.addHandler(error_handler)
```

### 9.2 日志轮转

```bash
# /etc/logrotate.d/aigateway
/opt/aigateway/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 opencode opencode
    sharedscripts
    postrotate
        /bin/kill -HUP $(cat /var/run/syslogd.pid 2> /dev/null) > /dev/null 2>&1 || true
    endscript
}
```

---

## 10. 备份恢复

### 10.1 数据库备份

```bash
#!/bin/bash
# backup-db.sh

BACKUP_DIR="/opt/aigateway/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="aigateway"
DB_USER="postgres"
RETENTION_DAYS=30

# 全量备份
echo "Starting database backup..."
pg_dump -h localhost -U $DB_USER -d $DB_NAME \
    -F c -f "$BACKUP_DIR/db_${DATE}.dump"

# 验证备份
if pg_restore -l "$BACKUP_DIR/db_${DATE}.dump" > /dev/null 2>&1; then
    echo "Backup verified successfully"
else
    echo "Backup verification failed!"
    exit 1
fi

# 清理旧备份
find $BACKUP_DIR -name "db_*.dump" -mtime +$RETENTION_DAYS -delete

# 上传到 S3（可选）
aws s3 cp "$BACKUP_DIR/db_${DATE}.dump" s3://aigateway-backups/db/

echo "Backup completed: db_${DATE}.dump"
```

### 10.2 恢复脚本

```bash
#!/bin/bash
# restore-db.sh

BACKUP_FILE=$1
DB_NAME="aigateway"
DB_USER="postgres"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# 停止应用
docker-compose stop gateway

# 恢复数据库
echo "Restoring database from $BACKUP_FILE..."
pg_restore -h localhost -U $DB_USER -d $DB_NAME --clean --if-exists "$BACKUP_FILE"

# 启动应用
docker-compose start gateway

echo "Database restored successfully"
```

### 10.3 工作区备份

```bash
#!/bin/bash
# backup-workspaces.sh

BACKUP_DIR="/opt/aigateway/backups/workspaces"
SOURCE_DIR="/opt/aigateway/workspaces"
DATE=$(date +%Y%m%d)

# 创建压缩备份
tar -czf "$BACKUP_DIR/workspaces_${DATE}.tar.gz" -C "$SOURCE_DIR" .

# 清理 7 天前的备份
find $BACKUP_DIR -name "workspaces_*.tar.gz" -mtime +7 -delete

echo "Workspaces backup completed"
```

---

## 11. 运维脚本

### 11.1 健康检查脚本

```bash
#!/bin/bash
# health-check.sh

HEALTH_URL="http://localhost:8000/health"
WEBHOOK_URL="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"

check_service() {
    local name=$1
    local url=$2
    
    if curl -sf "$url" > /dev/null 2>&1; then
        echo "✓ $name is healthy"
        return 0
    else
        echo "✗ $name is down"
        return 1
    fi
}

# 检查 Gateway
if ! check_service "Gateway" "$HEALTH_URL"; then
    # 发送告警
    curl -s "$WEBHOOK_URL" \
        -H 'Content-Type: application/json' \
        -d '{"msgtype": "text", "text": {"content": "🚨 Gateway 服务异常"}}'
fi

# 检查 OpenCode
if ! check_service "OpenCode" "http://127.0.0.1:4096/global/health"; then
    # 自动重启
    systemctl restart opencode
    
    # 发送告警
    curl -s "$WEBHOOK_URL" \
        -H 'Content-Type: application/json' \
        -d '{"msgtype": "text", "text": {"content": "🔄 OpenCode Server 已自动重启"}}'
fi

# 检查数据库
if ! pg_isready -U postgres -d aigateway > /dev/null 2>&1; then
    echo "✗ PostgreSQL is down"
    # 发送告警
fi

# 检查 Redis
if ! redis-cli ping > /dev/null 2>&1; then
    echo "✗ Redis is down"
    # 发送告警
fi
```

### 11.2 清理脚本

```bash
#!/bin/bash
# cleanup.sh

# 清理旧日志
find /opt/aigateway/logs -name "*.log" -mtime +30 -delete

# 清理已删除会话的工作区
find /opt/aigateway/workspaces -type d -empty -delete

# 清理临时文件
find /tmp -name "aigateway-*" -mtime +1 -delete

# 清理 Docker 镜像
docker system prune -f

echo "Cleanup completed"
```

---

## 12. 故障排查

### 12.1 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| Gateway 无法启动 | 数据库连接失败 | 检查数据库配置和网络 |
| SSE 连接断开 | 超时或网络问题 | 检查 Nginx 超时配置 |
| OpenCode 无响应 | LLM API 配额用完 | 检查 API Key 和配额 |
| 内存不足 | MCP 进程泄漏 | 重启 MCP 服务，检查内存限制 |
| 磁盘空间满 | 日志文件过大 | 清理日志，配置日志轮转 |

### 12.2 调试命令

```bash
# 查看服务状态
systemctl status aigateway-gateway
systemctl status opencode

# 查看日志
journalctl -u aigateway-gateway -f
journalctl -u opencode -f

# 查看网络连接
ss -tlnp | grep -E '8000|4096'

# 查看进程
ps aux | grep -E 'uvicorn|opencode'

# 查看资源使用
top -p $(pgrep -d',' uvicorn)

# 数据库连接
psql -U aigateway -d aigateway -c "SELECT count(*) FROM sessions;"

# Redis 连接
redis-cli info clients
```

### 12.3 性能调优

```bash
# 增加文件描述符限制
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# 优化内核参数
echo "net.core.somaxconn = 65535" | sudo tee -a /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65535" | sudo tee -a /etc/sysctl.conf
echo "vm.overcommit_memory = 1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# PostgreSQL 优化
# /etc/postgresql/15/main/postgresql.conf
max_connections = 200
shared_buffers = 4GB
effective_cache_size = 12GB
work_mem = 20MB
maintenance_work_mem = 512MB
```

---

**文档结束**
