# AstrBot MCP Server

用于连接远程 AstrBot 服务器的 MCP 服务器，支持查看日志和实时调试。

## 功能

- ✅ 获取 AstrBot 运行状态
- ✅ 查看日志（最近 N 行）
- ✅ 实时监控日志
- ✅ 重启 AstrBot 服务
- ✅ 查看配置文件
- ✅ 列出已安装插件
- ✅ 查看插件配置
- ✅ 执行远程命令
- ✅ 检查错误日志

## 安装

```bash
pip install -r requirements.txt
```

## 配置

设置环境变量：

```bash
# Windows PowerShell
$env:ASTRBOT_SSH_PASSWORD="你的SSH密码"
$env:ASTRBOT_PATH="~/astrbot"

# Linux/Mac
export ASTRBOT_SSH_PASSWORD="你的SSH密码"
export ASTRBOT_PATH="~/astrbot"
```

或者直接修改 `server.py` 中的 `SERVER_CONFIG`。

## 使用方法

### 1. 直接运行

```bash
python server.py
```

### 2. 配置 OpenCode 使用

在 OpenCode 配置文件中添加：

```json
{
  "mcp": {
    "servers": {
      "astrbot": {
        "command": "python",
        "args": ["D:\\opencode\\随便玩玩\\astrbot-mcp\\server.py"],
        "env": {
          "ASTRBOT_SSH_PASSWORD": "你的SSH密码",
          "ASTRBOT_PATH": "~/astrbot"
        }
      }
    }
  }
}
```

## 可用工具

| 工具名称 | 描述 |
|----------|------|
| `astrbot_status` | 获取 AstrBot 运行状态 |
| `astrbot_logs` | 获取最近 N 行日志 |
| `astrbot_logs_realtime` | 实时监控日志（持续 N 秒） |
| `astrbot_restart` | 重启 AstrBot 服务 |
| `astrbot_config` | 查看配置文件 |
| `astrbot_plugins` | 列出已安装插件 |
| `astrbot_plugin_config` | 查看指定插件配置 |
| `astrbot_execute` | 执行远程命令 |
| `astrbot_check_errors` | 检查错误日志 |

## 示例

### 获取状态
```json
{
  "name": "astrbot_status",
  "arguments": {}
}
```

### 查看日志
```json
{
  "name": "astrbot_logs",
  "arguments": {
    "lines": 100,
    "filter": "error"
  }
}
```

### 实时监控
```json
{
  "name": "astrbot_logs_realtime",
  "arguments": {
    "duration": 60,
    "filter": "mimo_search"
  }
}
```

### 查看插件配置
```json
{
  "name": "astrbot_plugin_config",
  "arguments": {
    "plugin_name": "mimo_search"
  }
}
```