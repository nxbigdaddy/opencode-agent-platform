#!/bin/bash
# 测试 Gateway API

echo "=== 测试 1: 健康检查 ==="
curl -s http://localhost:8001/health

echo ""
echo "=== 测试 2: 发送聊天消息 ==="
curl -s -X POST http://localhost:8001/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, please reply briefly"}'

echo ""
echo "=== 测试 3: 获取会话列表 ==="
curl -s http://localhost:8001/api/v1/sessions

echo ""
echo "=== 测试完成 ==="
