# AstrBot MCP Server 启动脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AstrBot MCP Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查环境变量
if (-not $env:ASTRBOT_SSH_PASSWORD) {
    Write-Host "错误: 未设置 ASTRBOT_SSH_PASSWORD 环境变量" -ForegroundColor Red
    Write-Host ""
    Write-Host "请设置环境变量:" -ForegroundColor Yellow
    Write-Host '  $env:ASTRBOT_SSH_PASSWORD="你的SSH密码"' -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "服务器配置:" -ForegroundColor Green
Write-Host "  主机: 192.168.50.71"
Write-Host "  端口: 8022"
Write-Host "  用户: u0_a275"
Write-Host "  AstrBot路径: $env:ASTRBOT_PATH"
Write-Host ""

Write-Host "启动 MCP 服务器..." -ForegroundColor Green
Write-Host ""

python server.py