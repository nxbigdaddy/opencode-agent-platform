#!/bin/bash
# 测试配额和工作区隔离（先登录获取新 Token）

echo "=== 步骤 1: 登录获取 Token ==="
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=YOUR_PASSWORD")

echo "$LOGIN_RESPONSE"

TOKEN=YOUR_SECRET "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo ""
echo "=== 步骤 2: 获取配额信息 ==="
curl -s http://localhost:8001/api/v1/quota -H "Authorization: Bearer $TOKEN"

echo ""
echo "=== 步骤 3: 获取预设指令列表 ==="
curl -s http://localhost:8001/api/v1/commands

echo ""
echo "=== 步骤 4: 检查工作区目录（发送前） ==="
ls -la /workspaces/ 2>/dev/null || echo "工作区目录尚未创建"

echo ""
echo "=== 步骤 5: 发送消息（触发工作区创建） ==="
curl -s -X POST http://localhost:8001/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message": "你好，请简单回复"}'

echo ""
echo "=== 步骤 6: 检查工作区目录（发送后） ==="
ls -laR /workspaces/ 2>/dev/null || echo "工作区目录尚未创建"

echo ""
echo "=== 步骤 7: 再次获取配额（检查扣减） ==="
curl -s http://localhost:8001/api/v1/quota -H "Authorization: Bearer $TOKEN"

echo ""
echo "=== 测试完成 ==="
