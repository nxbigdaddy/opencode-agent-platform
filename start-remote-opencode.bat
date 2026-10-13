@echo off
REM 启动 SSH 隧道，将远程 OpenCode 端口映射到本地
REM 注意：需要先在远程服务器上运行 opencode 服务

echo 正在建立 SSH 隧道到远程服务器...
echo 远程服务器: 203.0.113.10
echo 本地端口: 1776

ssh -i "<workspace>\opencodes\id_ed25519_1panel-160" -L 1776:localhost:1776 root@203.0.113.10 -N
