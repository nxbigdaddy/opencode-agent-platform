---
description: "发送标准化周报邮件"
agent: "build"
model: "qwen3.6-plus"
---

读取当前目录下的 weekly_report.md 文件内容，调用系统终端的邮件发送命令，发送到 $1 邮箱，邮件主题固定为"[部门] 周工作总结"。
