# 更新日志

本项目在公开发布前的开发历史未逐条迁移到本仓库；以下记录自首次公开发布起的版本变更。

## [0.1.0] - 2026-10-13

首次公开发布。

### 主要能力

- AI Agent 对话平台：把 OpenCode CLI 封装为可远程访问的 Agent 引擎。
- Gateway 服务端（Python）：提供 API、核心调度、数据模型与服务层分层结构。
- 前端应用（TypeScript + Vite + Tailwind CSS）：对话与任务界面。
- 容器化部署：提供 `docker-compose.yml` 与各服务镜像配置。
- 远程接入脚本：`opencode-remote`、`remote-opencode` 等批处理与 PowerShell/Node 脚本，便于在远端拉起会话。
- 常驻服务定义：`opencode-server.service`，可用于 systemd 托管。
- 多租户相关能力：配套 `test_multitenant.sh` 等验证脚本。
- 外部模型接入：提供 `opencode-aliyun.jsonc` 等配置模板（模板内不含真实密钥）。
- 配置模板化：敏感配置统一以 `.env.example` 形式提供，需自行复制并填写。
- 设计文档体系：`docs/` 下 01–11 共 11 篇，覆盖架构、需求、数据库、API、OpenCode 集成、前端、安全、部署运维、开发规范、测试策略与实施计划。
- 项目计划：`PROJECT-PLAN.md` 给出四阶段开发计划、技术栈详情、验收标准与风险管理。
- 验证脚本：提供 Gateway、登录、注册、功能与特性等 shell 验证脚本。

### 已知限制

- 平台依赖 OpenCode CLI 作为底层 Agent 引擎，需自行准备并保持版本兼容。
- 仓库内的文档以设计稿与计划为主，部分章节描述的是目标状态而非已交付功能。
- 模型服务、对象存储、数据库等外部依赖均需自行部署与配置，仓库不包含任何可用凭据。
- 部署脚本与示例配置面向 Linux 服务器环境，未在其他平台验证。
- README 未声明其他额外限制。

### 许可证

- 本项目采用 Apache-2.0，见 [LICENSE](LICENSE)。
