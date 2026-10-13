# OpenCode Agent 对话平台

> 由内部工程脱敏整理后开源。原目录：`opencodes` ｜ 领域：AI 开发工具

## 项目简介

AI Agent 对话平台（将 OpenCode CLI 转为远程 Agent 引擎，Gateway + 前端）

## 技术栈

docker / node / python / ts / vite

## 目录结构

```text
├── .env.example
├── PROJECT-PLAN.md
├── commands/
├── docker-compose.yml
├── docs/
├── fix_key_permission.ps1
├── frontend/
├── gateway/
├── opencode-aliyun.jsonc
├── opencode-remote.bat
├── opencode-remote.ps1
├── opencode-server.service
├── remote-opencode.bat
├── remote-opencode.js
├── start-remote-opencode.bat
├── test_aliyun.json
├── test_chat.json
├── test_features.sh
├── test_gateway.sh
├── test_login.txt
├── test_multitenant.sh
├── test_register.json
├── 想法.txt
```

## 快速开始

```bash
git clone <你的仓库地址>
cd opencode-agent-platform
```

- 依赖安装与启动方式请参考仓库内各子目录的 README 与配置文件。
- 所有配置模板均以 `*.example` 形式提供，请复制后填入你自己的密钥与地址。

## 脱敏说明

本仓库由内部工程导出，导出时已执行以下处理：

- **删除**：私钥与证书（`*.pem` / `*.key` / `*.pfx` / `id_rsa*` / `id_ed25519*`）、`.env` 实例文件、
  数据库与备份（`*.sql` 数据导出 / `*.db` / `*.sqlite` / `*.bak` / `*.mdf`）、cookie 与本地配置、
  依赖目录与构建产物、压缩包与安装程序、大体积媒体文件。
- **替换**：口令、API Key、Token、连接串密码、内网 IP、企业域名与企业名称，均替换为占位符。
- **保留**：可公开的源码、配置模板（`.env.example`）、文档、测试与少量必要素材。

如仍发现遗漏的敏感信息，请提交 Issue，我们会立即处理。

## 许可证

Apache-2.0
