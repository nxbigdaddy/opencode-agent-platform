# AI Agent 对话平台 - 文档索引

**版本**：v1.0  
**日期**：2026-04-21  
**项目状态**：设计阶段

---

## 文档列表

### 核心设计文档

| 文档 | 说明 | 目标读者 |
|------|------|----------|
| [01-architecture.md](01-architecture.md) | 项目总览与架构设计 | 架构师、技术负责人、开发团队 |
| [02-requirements.md](02-requirements.md) | 需求规格说明书 | 产品经理、开发团队、测试团队 |
| [03-database-design.md](03-database-design.md) | 数据库设计文档 | 后端开发、DBA、运维团队 |
| [04-api-design.md](04-api-design.md) | API 接口设计文档 | 前端开发、后端开发、测试团队 |
| [05-opencode-integration.md](05-opencode-integration.md) | OpenCode 集成设计文档 | 后端开发、DevOps、架构师 |

### 专项设计文档

| 文档 | 说明 | 目标读者 |
|------|------|----------|
| [06-frontend-design.md](06-frontend-design.md) | 前端设计文档 | 前端开发、UI/UX 设计师 |
| [07-security-design.md](07-security-design.md) | 安全设计文档 | 安全工程师、后端开发、DevOps |
| [08-deployment-ops.md](08-deployment-ops.md) | 部署与运维文档 | DevOps、运维工程师、系统管理员 |

### 规范与计划文档

| 文档 | 说明 | 目标读者 |
|------|------|----------|
| [09-development-guidelines.md](09-development-guidelines.md) | 开发规范与约定 | 开发团队 |
| [10-testing-strategy.md](10-testing-strategy.md) | 测试策略文档 | 测试团队、开发团队 |
| [11-implementation-plan.md](11-implementation-plan.md) | 实施计划文档 | 项目经理、技术负责人 |

---

## 快速导航

### 按角色查找

**架构师/技术负责人**：
1. [01-architecture.md](01-architecture.md) - 了解整体架构
2. [05-opencode-integration.md](05-opencode-integration.md) - 理解 OpenCode 集成方案
3. [07-security-design.md](07-security-design.md) - 审查安全设计

**后端开发**：
1. [03-database-design.md](03-database-design.md) - 数据库设计
2. [04-api-design.md](04-api-design.md) - API 接口规范
3. [05-opencode-integration.md](05-opencode-integration.md) - OpenCode 集成
4. [09-development-guidelines.md](09-development-guidelines.md) - 开发规范

**前端开发**：
1. [04-api-design.md](04-api-design.md) - API 接口规范
2. [06-frontend-design.md](06-frontend-design.md) - 前端架构与组件
3. [09-development-guidelines.md](09-development-guidelines.md) - 开发规范

**DevOps/运维**：
1. [08-deployment-ops.md](08-deployment-ops.md) - 部署与运维指南
2. [05-opencode-integration.md](05-opencode-integration.md) - OpenCode Server 部署
3. [07-security-design.md](07-security-design.md) - 安全加固

**测试团队**：
1. [02-requirements.md](02-requirements.md) - 需求规格
2. [10-testing-strategy.md](10-testing-strategy.md) - 测试策略
3. [04-api-design.md](04-api-design.md) - API 测试参考

**项目经理**：
1. [02-requirements.md](02-requirements.md) - 需求规格
2. [11-implementation-plan.md](11-implementation-plan.md) - 实施计划
3. [01-architecture.md](01-architecture.md) - 架构概览

---

## OpenCode 官方文档引用

本文档集中所有涉及 OpenCode API 的部分均参考官方文档：

| 官方文档 | URL |
|----------|-----|
| OpenCode 官方首页 | https://opencode.ai |
| OpenCode 文档中心 | https://opencode.ai/docs |
| OpenCode Server API | https://opencode.ai/docs/server/ |
| OpenCode SDK | https://opencode.ai/docs/sdk/ |
| OpenCode Agents | https://opencode.ai/docs/agents/ |
| OpenCode MCP Servers | https://opencode.ai/docs/mcp-servers/ |
| OpenCode Tools | https://opencode.ai/docs/tools/ |
| OpenCode Custom Tools | https://opencode.ai/docs/custom-tools/ |
| OpenCode Permissions | https://opencode.ai/docs/permissions/ |
| OpenCode Config | https://opencode.ai/docs/config/ |

---

## 文档使用建议

1. **新成员入职**：按顺序阅读 01 → 02 → 09，快速了解项目
2. **开发阶段**：根据任务查阅对应专项文档
3. **代码审查**：参考 09 开发规范
4. **测试阶段**：参考 10 测试策略
5. **上线部署**：参考 08 部署运维文档
6. **安全审计**：重点阅读 07 安全设计

---

**文档结束**
