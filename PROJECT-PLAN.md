# AI Agent 对话平台 - 完整项目开发计划

**项目名称**: AI Agent 对话平台  
**版本**: v1.0  
**创建日期**: 2026-04-21  
**计划完成**: 2026-06-30  
**总工期**: 10周

---

## 📊 项目概览

| 维度 | 说明 |
|------|------|
| **目标** | 将 OpenCode CLI 转化为生产级远程 Agent 引擎 |
| **核心功能** | 多用户、多会话、多工具的 AI 对话服务平台 |
| **技术栈** | React 18 + FastAPI + OpenCode + PostgreSQL + Redis |
| **团队规模** | 8人（1PM + 1架构师 + 3后端 + 2前端 + 1DevOps + 1QA） |
| **部署环境** | Ubuntu 22.04/24.04 LTS + Docker + Nginx |

---

## 🗓️ 详细开发计划

### Phase 1: 基础验证（第1-2周）

#### Week 1: 环境搭建与原型开发

| 任务 | 负责人 | 工时 | 产出 | 状态 |
|------|--------|------|------|------|
| 环境搭建 | DevOps | 2d | Docker Compose、CI/CD | ✅ 完成 |
| OpenCode 部署 | Backend | 2d | serve 模式运行 | ⏳ 进行中 |
| Gateway 原型 | Backend | 3d | FastAPI SSE 透传 | ⏳ 进行中 |
| 前端原型 | Frontend | 3d | React 单页面聊天 | ⏳ 进行中 |

**Week 1 交付物**:
- `docker-compose.yml` - PostgreSQL + Redis 部署配置
- `gateway/main.py` - FastAPI 最小应用
- `gateway/opencode_client.py` - OpenCode SSE 客户端
- `frontend/` - React + Vite 项目骨架

#### Week 2: 基础功能验证

| 任务 | 负责人 | 工时 | 产出 | 状态 |
|------|--------|------|------|------|
| 工作区隔离验证 | Backend | 2d | 多目录测试通过 | ⏳ 待开始 |
| 基础认证 | Backend | 2d | JWT 登录/注册 | ⏳ 待开始 |
| 消息持久化 | Backend | 2d | PostgreSQL 消息表 | ⏳ 待开始 |
| 原型集成测试 | QA | 2d | 测试报告 | ⏳ 待开始 |

**里程碑 M1** (2026-05-02): OpenCode SSE 接口可用，端到端对话原型跑通

---

### Phase 2: 核心功能（第3-5周）

#### Week 3: 用户与认证

| 任务 | 负责人 | 工时 | 产出 |
|------|--------|------|------|
| 用户注册/登录 | Backend | 2d | JWT 认证体系 |
| OAuth 集成 | Backend | 2d | 企业微信/钉钉登录 |
| 用户管理 API | Backend | 2d | CRUD 接口 |
| 登录页面 | Frontend | 2d | React 登录/注册 |
| 用户中心 | Frontend | 2d | 个人信息、用量 |

#### Week 4: 会话与对话

| 任务 | 负责人 | 工时 | 产出 |
|------|--------|------|------|
| 会话管理 API | Backend | 2d | CRUD + 搜索 |
| 消息管理 API | Backend | 2d | 分页、历史 |
| SSE 代理优化 | Backend | 2d | 连接池、重连 |
| 会话侧边栏 | Frontend | 2d | 列表、搜索 |
| 对话窗口 | Frontend | 3d | 消息列表、输入框 |
| 流式响应 | Frontend | 2d | SSE 接收、打字机效果 |

#### Week 5: Agent 与工具

| 任务 | 负责人 | 工时 | 产出 |
|------|--------|------|------|
| Agent 管理 API | Backend | 2d | CRUD、权限 |
| MCP 注册中心 | Backend | 2d | 服务发现 |
| Agent 列表 | Frontend | 2d | 展示、切换 |
| 自定义 Agent | Frontend | 2d | 配置表单 |
| MCP 管理 | Frontend | 2d | 注册、状态 |
| 集成测试 | QA | 3d | 测试报告 |

**里程碑 M2** (2026-05-23): MVP 完成，核心功能可用，内部测试通过

---

### Phase 3: 生产加固（第6-7周）

#### Week 6: 安全与性能

| 任务 | 负责人 | 工时 | 产出 |
|------|--------|------|------|
| 安全审计 | Security | 3d | 漏洞扫描报告 |
| 权限系统 | Backend | 2d | RBAC 实现 |
| 输入过滤 | Backend | 2d | XSS/SQL 注入防护 |
| MCP 沙箱 | Backend | 2d | Firejail 隔离 |
| Redis 缓存 | Backend | 2d | 热点数据缓存 |
| 数据库优化 | Backend | 2d | 索引、连接池 |

#### Week 7: 部署与监控

| 任务 | 负责人 | 工时 | 产出 |
|------|--------|------|------|
| Docker Compose | DevOps | 2d | 开发环境 |
| 生产部署脚本 | DevOps | 2d | 自动化部署 |
| Nginx 配置 | DevOps | 1d | SSL、负载均衡 |
| Prometheus | DevOps | 2d | 指标采集 |
| Grafana 大盘 | DevOps | 2d | 可视化 |
| 告警配置 | DevOps | 2d | 企业微信机器人 |
| 性能压测 | QA | 2d | 性能报告 |

**里程碑 M3** (2026-06-06): 生产就绪，安全审计通过，性能达标

---

### Phase 4: 生态扩展（第8-10周）

#### Week 8: 企业集成

| 任务 | 负责人 | 工时 | 产出 |
|------|--------|------|------|
| 企业微信机器人 | Backend | 3d | Webhook 接入 |
| 钉钉机器人 | Backend | 3d | Webhook 接入 |
| 消息推送 | Backend | 2d | 异步通知 |
| 移动端适配 | Frontend | 3d | 响应式/PWA |

#### Week 9: 高级功能

| 任务 | 负责人 | 工时 | 产出 |
|------|--------|------|------|
| NL2SQL MCP | Backend | 3d | PostgreSQL 查询 |
| NL2API MCP | Backend | 3d | 内部 API 封装 |
| 多模型路由 | Backend | 2d | 自动选择模型 |
| 文件上传 | Frontend | 2d | 拖拽上传 |
| 代码操作 | Frontend | 2d | 复制、插入 |

#### Week 10: 发布准备

| 任务 | 负责人 | 工时 | 产出 |
|------|--------|------|------|
| 用户验收测试 | QA + 用户 | 3d | UAT 报告 |
| 文档完善 | Tech Writer | 3d | 用户手册 |
| 生产部署 | DevOps | 2d | 上线 |
| 监控验证 | DevOps | 2d | 告警测试 |
| 正式发布 | PM | 1d | 发布公告 |

**里程碑 M4** (2026-06-30): 正式发布，生产环境稳定运行

---

## 📁 项目目录结构

```
aigateway/
├── docker-compose.yml          # 开发环境编排
├── .env.example                # 环境变量模板
├── PROJECT-PLAN.md             # 本文件
├── docs/                       # 项目文档
│   ├── 01-architecture.md
│   ├── 02-requirements.md
│   └── ...
├── gateway/                    # FastAPI 后端
│   ├── main.py                 # 应用入口
│   ├── api/                    # API 路由
│   │   ├── auth.py             # 认证接口
│   │   ├── sessions.py         # 会话管理
│   │   ├── messages.py         # 消息接口
│   │   ├── agents.py           # Agent 管理
│   │   └── mcp.py              # MCP 工具
│   ├── core/                   # 核心配置
│   │   ├── config.py           # 配置管理
│   │   ├── security.py         # 安全相关
│   │   └── database.py         # 数据库连接
│   ├── models/                 # 数据模型
│   │   ├── user.py
│   │   ├── session.py
│   │   └── message.py
│   ├── services/               # 业务逻辑
│   │   ├── auth_service.py
│   │   ├── session_service.py
│   │   └── opencode_client.py  # OpenCode 客户端
│   └── tests/                  # 测试代码
├── frontend/                   # React 前端
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── src/
│   │   ├── main.tsx            # 应用入口
│   │   ├── App.tsx             # 根组件
│   │   ├── components/         # 通用组件
│   │   │   ├── ChatWindow.tsx
│   │   │   ├── MessageList.tsx
│   │   │   └── MessageInput.tsx
│   │   ├── pages/              # 页面组件
│   │   │   ├── Login.tsx
│   │   │   ├── Chat.tsx
│   │   │   └── Admin.tsx
│   │   ├── stores/             # Zustand 状态管理
│   │   │   ├── authStore.ts
│   │   │   └── chatStore.ts
│   │   ├── api/                # API 客户端
│   │   │   ├── client.ts
│   │   │   └── endpoints.ts
│   │   └── types/              # TypeScript 类型
│   │       ├── user.ts
│   │       └── chat.ts
│   └── public/                 # 静态资源
├── mcp-servers/                # MCP 工具服务
│   ├── filesystem/
│   ├── sqlite/
│   └── api-client/
└── deploy/                     # 部署配置
    ├── docker/
    ├── k8s/
    └── nginx/
```

---

## 🔧 技术栈详情

### 后端 (Gateway)

| 组件 | 技术 | 版本 | 说明 |
|------|------|------|------|
| **Web 框架** | FastAPI | 0.115+ | 异步原生、自动 OpenAPI |
| **语言** | Python | 3.12+ | 异步生态丰富 |
| **ORM** | SQLAlchemy | 2.0+ | 异步支持、类型安全 |
| **数据库驱动** | asyncpg | 0.29+ | 高性能 PostgreSQL |
| **缓存** | Redis (redis-py) | 7.x | Pub/Sub、Stream |
| **认证** | python-jose | 3.3+ | JWT 实现 |
| **密码哈希** | bcrypt | 4.1+ | 安全密码存储 |
| **HTTP 客户端** | httpx | 0.27+ | 异步 HTTP，用于 OpenCode 通信 |

### 前端

| 组件 | 技术 | 版本 | 说明 |
|------|------|------|------|
| **框架** | React | 18.x | 组件化、Concurrent Features |
| **语言** | TypeScript | 5.x | 类型安全 |
| **样式** | Tailwind CSS | 3.x | 原子化 CSS |
| **UI 组件** | shadcn/ui | 最新 | 可定制、源码开放 |
| **构建工具** | Vite | 5.x | 快速热更新 |
| **状态管理** | Zustand | 4.x | 轻量、简洁 |
| **服务端状态** | React Query | 5.x | 缓存、重试 |
| **HTTP 客户端** | Axios | 1.x | 拦截器、取消请求 |
| **Markdown** | react-markdown | 9.x | Markdown 渲染 |
| **代码高亮** | react-syntax-highlighter | 15.x | 代码展示 |

### 基础设施

| 组件 | 技术 | 版本 | 说明 |
|------|------|------|------|
| **数据库** | PostgreSQL | 15+ | JSONB、全文检索 |
| **缓存** | Redis | 7+ | 高性能缓存 |
| **反向代理** | Nginx | 1.24+ | SSL、负载均衡 |
| **容器化** | Docker + Compose | 24.x | 环境一致性 |
| **监控** | Prometheus + Grafana | 2.x/10.x | 云原生标准 |
| **日志** | Loki + Grafana | 2.x | 日志聚合 |

---

## 🎯 验收标准

### 功能验收

| 功能模块 | 验收标准 | 测试方法 |
|----------|----------|----------|
| 用户认证 | 注册、登录、OAuth 可用 | 手动测试 |
| 会话管理 | CRUD、搜索、分页正常 | 自动化测试 |
| 实时对话 | SSE 流式响应、首字 < 3s | 手动测试 |
| Agent 切换 | Tab 切换、配置生效 | 手动测试 |
| MCP 工具 | filesystem + sqlite 可用 | 集成测试 |
| 管理后台 | 用户管理、用量统计 | 手动测试 |

### 性能验收

| 指标 | 目标值 | 测试方法 |
|------|--------|----------|
| 并发用户 | 500+ | k6 压测 |
| API P95 | < 500ms | k6 压测 |
| SSE 首字 | < 3s | 手动测试 |
| 页面加载 | < 2s | Lighthouse |
| 可用性 | 99.9% | 监控数据 |

### 安全验收

| 检查项 | 标准 | 方法 |
|--------|------|------|
| 漏洞扫描 | 无高危漏洞 | OWASP ZAP |
| 渗透测试 | 无严重漏洞 | 人工测试 |
| 代码审计 | 无安全缺陷 | SonarQube |
| 合规检查 | 符合等保要求 | 自查 |

---

## ⚠️ 风险管理

| 风险 ID | 风险描述 | 可能性 | 影响 | 风险等级 | 应对策略 |
|---------|----------|--------|------|----------|----------|
| R1 | OpenCode API 变更 | 中 | 高 | 高 | 封装抽象层，关注官方 Changelog |
| R2 | LLM API 响应慢 | 高 | 中 | 中 | 超时控制、流式返回、降级策略 |
| R3 | Token 费用暴涨 | 中 | 高 | 高 | 用量配额、实时监控、告警 |
| R4 | MCP 权限逃逸 | 低 | 高 | 中 | 沙箱化、白名单、审计 |
| R5 | 并发性能不足 | 中 | 中 | 中 | 压测、优化、扩容 |
| R6 | 团队成员离职 | 低 | 中 | 低 | 文档完善、知识共享 |
| R7 | 第三方服务故障 | 中 | 中 | 中 | 降级策略、多供应商 |
| R8 | 安全漏洞 | 低 | 高 | 中 | 安全扫描、渗透测试 |

---

## 📅 会议计划

| 会议 | 频率 | 参与者 | 目的 |
|------|------|--------|------|
| 站会 | 每日 9:30 | 开发团队 | 同步进度、阻塞问题 |
| 迭代评审 | 每周五 | 全员 | 演示成果、收集反馈 |
| 迭代计划 | 每周一 | 技术团队 | 计划下周任务 |
| 技术评审 | 按需 | 架构师 + 相关开发 | 技术方案评审 |
| 项目周报 | 每周五 | PM + 管理层 | 汇报进度、风险 |

---

**文档版本**: v1.0  
**最后更新**: 2026-04-21  
**维护人**: AI Agent 团队
