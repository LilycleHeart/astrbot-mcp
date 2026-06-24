@echo off
REM AstrBot MCP Server 启动脚本

echo ========================================
echo AstrBot MCP Server
echo ========================================
echo.

REM 检查环境变量
if "%ASTRBOT_SSH_PASSWORD%"=="" (
    echo 错误: 未设置 ASTRBOT_SSH_PASSWORD 环境变量
    echo.
    echo 请设置环境变量:
    echo   set ASTRBOT_SSH_PASSWORD=你的SSH密码
    echo.
    pause
    exit /b 1
)

echo 服务器配置:
echo   主机: 192.168.50.71
echo   端口: 8022
echo   用户: u0_a275
echo   AstrBot路径: %ASTRBOT_PATH%
echo.

echo 启动 MCP 服务器...
echo.

python server.py