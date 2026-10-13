# AI Agent 对话平台 - FastAPI Gateway

## 项目结构

```
gateway/
├── main.py                 # 应用入口
├── requirements.txt        # 依赖
├── .env                    # 环境变量
├── core/
│   ├── config.py           # 配置管理
│   └── database.py         # 数据库连接
├── api/
│   └── chat.py             # 聊天接口（SSE）
├── services/
│   └── opencode_client.py  # OpenCode 客户端
└── models/
    └── chat.py             # 数据模型
```

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn main:app --reload --port 8000
```

## API 文档

启动后访问: http://localhost:8000/docs
