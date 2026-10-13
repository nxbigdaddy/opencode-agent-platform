#!/bin/bash
# 测试多租户聊天接口

TOKEN="YOUR_SECRET"

echo "=== 测试 1: 获取当前用户信息 ==="
curl -s http://localhost:8001/api/v1/auth/me -H "Authorization: Bearer $TOKEN"

echo ""
echo "=== 测试 2: 发送聊天消息（带认证） ==="
curl -s -X POST http://localhost:8001/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d @/tmp/test_aliyun.json

echo ""
echo "=== 测试 3: 获取会话列表 ==="
curl -s http://localhost:8001/api/v1/sessions -H "Authorization: Bearer $TOKEN"

echo ""
echo "=== 测试 4: 无认证访问（应该失败） ==="
curl -s -X POST http://localhost:8001/api/v1/chat \
  -H "Content-Type: application/json" \
  -d @/tmp/test_aliyun.json

echo ""
echo "=== 测试完成 ==="
