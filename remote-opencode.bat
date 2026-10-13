@echo off
REM 远程OpenCode快捷脚本
REM 用法: remote-opencode "你的命令"

if "%~1"=="" (
    echo 用法: remote-opencode "你的命令"
    echo 或直接运行: remote-opencode 进入交互模式
    ssh opencode-remote -t "opencode"
) else (
    ssh opencode-remote "opencode %*"
)
