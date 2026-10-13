# OpenCode Remote Controller
# 在远程服务器上执行OpenCode命令

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)

$RemoteHost = "opencode-remote"
$RemoteOpencode = "/usr/bin/opencode"

# 构建命令
$cmd = $Arguments -join ' '

if (-not $cmd) {
    # 进入交互模式
    Write-Host "[Remote] 连接到远程OpenCode交互模式..." -ForegroundColor Green
    ssh -t $RemoteHost $RemoteOpencode
} else {
    # 执行单个命令
    Write-Host "[Remote] 在服务器上执行: opencode $cmd" -ForegroundColor Green
    ssh $RemoteHost "$RemoteOpencode $cmd"
}
