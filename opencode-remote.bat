@echo off
REM OpenCode Remote - 远程OpenCode控制器
REM 用法: opencode-remote [命令]
REM 
REM 示例:
REM   opencode-remote              - 进入交互模式
REM   opencode-remote -p "你好"    - 执行单个命令

powershell -ExecutionPolicy Bypass -File "<workspace>\opencodes\opencode-remote.ps1" %*
