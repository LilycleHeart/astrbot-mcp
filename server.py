"""
AstrBot MCP Server
用于连接远程 AstrBot 服务器，查看日志和实时调试
支持 proot Ubuntu 环境
"""

import asyncio
import json
import os
from typing import Any, Optional
from datetime import datetime

import paramiko
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# 服务器配置
SERVER_CONFIG = {
    "host": "192.168.50.71",
    "port": 8022,
    "username": "u0_a275",
    "password": os.getenv("ASTRBOT_SSH_PASSWORD", "kyoko"),
    # proot 环境配置
    "proot_root": "/data/data/com.termux/files/usr/var/lib/proot-distro/installed-rootfs/ubuntu-22.04",
    "astrbot_path": "/root/AstrBot",  # proot 环境中的路径
}


def proot_command(cmd: str) -> str:
    """包装命令为 proot 命令"""
    proot_base = (
        f'unset LD_PRELOAD && proot -0 -r {SERVER_CONFIG["proot_root"]} '
        f'-w /root '
        f'-b {SERVER_CONFIG["proot_root"]}/sys/.empty:/sys/fs/selinux '
        f'-b /proc -b /sys -b /data/data/com.termux/files/home/proot_shm:/dev/shm -b /dev '
        f'--sysvipc --link2symlink --kill-on-exit '
        f'/usr/bin/env -i PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin '
        f'TERM=dumb HOME=/root USER=root '
        f'/bin/bash -c "{cmd}"'
    )
    return proot_base


class AstrBotMCPServer:
    """AstrBot MCP 服务器"""
    
    def __init__(self):
        self.server = Server("astrbot-mcp")
        self.ssh_client: Optional[paramiko.SSHClient] = None
        self._setup_tools()
    
    def _get_ssh_client(self) -> paramiko.SSHClient:
        """获取或创建 SSH 连接"""
        if self.ssh_client is None:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                hostname=SERVER_CONFIG["host"],
                port=SERVER_CONFIG["port"],
                username=SERVER_CONFIG["username"],
                password=SERVER_CONFIG["password"],
                timeout=10
            )
        return self.ssh_client
    
    def _execute_command(self, command: str, use_proot: bool = False) -> tuple[str, str, int]:
        """执行远程命令"""
        try:
            client = self._get_ssh_client()
            if use_proot:
                command = proot_command(command)
            stdin, stdout, stderr = client.exec_command(command, timeout=60)
            exit_code = stdout.channel.recv_exit_status()
            return stdout.read().decode('utf-8', errors='replace'), stderr.read().decode('utf-8', errors='replace'), exit_code
        except Exception as e:
            return "", str(e), -1
    
    def _setup_tools(self):
        """设置 MCP 工具"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """列出所有可用工具"""
            return [
                Tool(
                    name="astrbot_status",
                    description="获取 AstrBot 运行状态",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="astrbot_logs",
                    description="获取 AstrBot 日志（最近 N 行）",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "lines": {
                                "type": "integer",
                                "description": "获取最近多少行日志，默认 50",
                                "default": 50
                            },
                            "filter": {
                                "type": "string",
                                "description": "过滤关键词（可选）",
                                "default": ""
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="astrbot_logs_realtime",
                    description="实时监控 AstrBot 日志（持续 N 秒）",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "duration": {
                                "type": "integer",
                                "description": "监控时长（秒），默认 30",
                                "default": 30
                            },
                            "filter": {
                                "type": "string",
                                "description": "过滤关键词（可选）",
                                "default": ""
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="astrbot_restart",
                    description="重启 AstrBot 服务",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="astrbot_config",
                    description="查看 AstrBot 配置",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "config_file": {
                                "type": "string",
                                "description": "配置文件名，默认 cmd_config.json",
                                "default": "cmd_config.json"
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="astrbot_plugins",
                    description="列出已安装的插件",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="astrbot_plugin_config",
                    description="查看指定插件的配置",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "plugin_name": {
                                "type": "string",
                                "description": "插件名称"
                            }
                        },
                        "required": ["plugin_name"]
                    }
                ),
                Tool(
                    name="astrbot_execute",
                    description="在 AstrBot 服务器上执行命令",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "要执行的命令"
                            },
                            "use_proot": {
                                "type": "boolean",
                                "description": "是否在 proot 环境中执行，默认 true",
                                "default": True
                            }
                        },
                        "required": ["command"]
                    }
                ),
                Tool(
                    name="astrbot_check_errors",
                    description="检查 AstrBot 最近的错误日志",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "lines": {
                                "type": "integer",
                                "description": "检查最近多少行日志，默认 200",
                                "default": 200
                            }
                        },
                        "required": []
                    }
                ),
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """调用工具"""
            try:
                if name == "astrbot_status":
                    return await self._get_status()
                elif name == "astrbot_logs":
                    return await self._get_logs(
                        lines=arguments.get("lines", 50),
                        filter_text=arguments.get("filter", "")
                    )
                elif name == "astrbot_logs_realtime":
                    return await self._get_logs_realtime(
                        duration=arguments.get("duration", 30),
                        filter_text=arguments.get("filter", "")
                    )
                elif name == "astrbot_restart":
                    return await self._restart()
                elif name == "astrbot_config":
                    return await self._get_config(
                        config_file=arguments.get("config_file", "cmd_config.json")
                    )
                elif name == "astrbot_plugins":
                    return await self._get_plugins()
                elif name == "astrbot_plugin_config":
                    return await self._get_plugin_config(
                        plugin_name=arguments["plugin_name"]
                    )
                elif name == "astrbot_execute":
                    return await self._execute(
                        command=arguments["command"],
                        use_proot=arguments.get("use_proot", True)
                    )
                elif name == "astrbot_check_errors":
                    return await self._check_errors(
                        lines=arguments.get("lines", 200)
                    )
                else:
                    return [TextContent(type="text", text=f"未知工具: {name}")]
            except Exception as e:
                return [TextContent(type="text", text=f"错误: {str(e)}")]
    
    async def _get_status(self) -> list[TextContent]:
        """获取 AstrBot 运行状态"""
        # 检查进程是否运行
        stdout, stderr, exit_code = self._execute_command(
            "ps aux | grep -i astrbot | grep -v grep"
        )
        
        if "astrbot" in stdout.lower() or "wrapper" in stdout.lower():
            status = "运行中"
            # 获取进程信息
            lines = stdout.strip().split('\n')
            process_info = '\n'.join(lines[:3]) if lines else ""
        else:
            status = "未运行"
            process_info = ""
        
        # 获取系统信息（在 proot 环境中）
        uptime_out, _, _ = self._execute_command("uptime", use_proot=True)
        memory_out, _, _ = self._execute_command("free -h | head -2", use_proot=True)
        
        result = f"""AstrBot 状态: {status}

进程信息:
{process_info}

系统信息:
{uptime_out.strip()}

内存使用:
{memory_out.strip()}"""
        
        return [TextContent(type="text", text=result)]
    
    async def _get_logs(self, lines: int = 50, filter_text: str = "") -> list[TextContent]:
        """获取 AstrBot 日志"""
        log_path = f"{SERVER_CONFIG['astrbot_path']}/data/astrbot.log"
        
        if filter_text:
            command = f"tail -n {lines} {log_path} 2>/dev/null | grep -i '{filter_text}' || echo '日志为空或不存在'"
        else:
            command = f"tail -n {lines} {log_path} 2>/dev/null || echo '日志为空或不存在'"
        
        stdout, stderr, exit_code = self._execute_command(command, use_proot=True)
        
        if not stdout or stdout.strip() == "日志为空或不存在":
            # 尝试其他日志路径
            command = f"find {SERVER_CONFIG['astrbot_path']}/data -name '*.log' -type f 2>/dev/null"
            stdout, stderr, exit_code = self._execute_command(command, use_proot=True)
            
            if stdout:
                log_files = stdout.strip().split('\n')
                if log_files:
                    log_path = log_files[0]
                    if filter_text:
                        command = f"tail -n {lines} {log_path} | grep -i '{filter_text}'"
                    else:
                        command = f"tail -n {lines} {log_path}"
                    stdout, stderr, exit_code = self._execute_command(command, use_proot=True)
        
        if not stdout:
            return [TextContent(type="text", text="未找到日志文件或日志为空")]
        
        return [TextContent(type="text", text=stdout)]
    
    async def _get_logs_realtime(self, duration: int = 30, filter_text: str = "") -> list[TextContent]:
        """实时监控 AstrBot 日志"""
        log_path = f"{SERVER_CONFIG['astrbot_path']}/data/astrbot.log"
        
        if filter_text:
            command = f"timeout {duration} tail -f {log_path} 2>/dev/null | grep --line-buffered -i '{filter_text}'"
        else:
            command = f"timeout {duration} tail -f {log_path} 2>/dev/null"
        
        stdout, stderr, exit_code = self._execute_command(command, use_proot=True)
        
        if not stdout:
            return [TextContent(type="text", text=f"监控 {duration} 秒，未捕获到日志")]
        
        return [TextContent(type="text", text=f"监控 {duration} 秒的日志:\n\n{stdout}")]
    
    async def _restart(self) -> list[TextContent]:
        """重启 AstrBot 服务"""
        # 杀掉现有进程
        self._execute_command("pkill -f wrapper_astrbot")
        self._execute_command("pkill -f 'python.*main.py'")
        await asyncio.sleep(2)
        
        # 重新启动
        stdout, stderr, exit_code = self._execute_command(
            "nohup /data/data/com.termux/files/home/wrapper_astrbot.sh &"
        )
        
        await asyncio.sleep(3)
        
        # 检查是否启动成功
        stdout, stderr, exit_code = self._execute_command(
            "ps aux | grep -i astrbot | grep -v grep"
        )
        
        if "wrapper" in stdout.lower() or "astrbot" in stdout.lower():
            return [TextContent(type="text", text="AstrBot 重启成功")]
        else:
            return [TextContent(type="text", text=f"重启可能失败，请手动检查")]
    
    async def _get_config(self, config_file: str = "cmd_config.json") -> list[TextContent]:
        """查看 AstrBot 配置"""
        config_path = f"{SERVER_CONFIG['astrbot_path']}/data/{config_file}"
        command = f"cat {config_path}"
        
        stdout, stderr, exit_code = self._execute_command(command, use_proot=True)
        
        if exit_code != 0:
            return [TextContent(type="text", text=f"无法读取配置文件: {stderr}")]
        
        try:
            # 尝试格式化 JSON
            config = json.loads(stdout)
            formatted = json.dumps(config, indent=2, ensure_ascii=False)
            return [TextContent(type="text", text=formatted)]
        except:
            return [TextContent(type="text", text=stdout)]
    
    async def _get_plugins(self) -> list[TextContent]:
        """列出已安装的插件"""
        plugins_path = f"{SERVER_CONFIG['astrbot_path']}/data/plugins"
        command = f"ls -la {plugins_path}/"
        
        stdout, stderr, exit_code = self._execute_command(command, use_proot=True)
        
        if exit_code != 0:
            return [TextContent(type="text", text=f"无法列出插件: {stderr}")]
        
        return [TextContent(type="text", text=f"已安装的插件:\n\n{stdout}")]
    
    async def _get_plugin_config(self, plugin_name: str) -> list[TextContent]:
        """查看指定插件的配置"""
        config_path = f"{SERVER_CONFIG['astrbot_path']}/data/config/{plugin_name}_config.json"
        command = f"cat {config_path}"
        
        stdout, stderr, exit_code = self._execute_command(command, use_proot=True)
        
        if exit_code != 0:
            return [TextContent(type="text", text=f"无法读取插件配置: {stderr}")]
        
        try:
            config = json.loads(stdout)
            formatted = json.dumps(config, indent=2, ensure_ascii=False)
            return [TextContent(type="text", text=f"插件 {plugin_name} 的配置:\n\n{formatted}")]
        except:
            return [TextContent(type="text", text=f"插件 {plugin_name} 的配置:\n\n{stdout}")]
    
    async def _execute(self, command: str, use_proot: bool = True) -> list[TextContent]:
        """执行远程命令"""
        stdout, stderr, exit_code = self._execute_command(command, use_proot=use_proot)
        
        result = f"命令: {command}\n退出码: {exit_code}\n\n"
        
        if stdout:
            result += f"输出:\n{stdout}\n"
        
        if stderr:
            result += f"错误:\n{stderr}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def _check_errors(self, lines: int = 200) -> list[TextContent]:
        """检查 AstrBot 最近的错误日志"""
        log_path = f"{SERVER_CONFIG['astrbot_path']}/data/astrbot.log"
        command = f"tail -n {lines} {log_path} 2>/dev/null | grep -i -E '(error|exception|traceback|failed|失败|错误)'"
        
        stdout, stderr, exit_code = self._execute_command(command, use_proot=True)
        
        if not stdout:
            return [TextContent(type="text", text="未发现错误日志")]
        
        return [TextContent(type="text", text=f"发现错误日志:\n\n{stdout}")]
    
    async def run(self):
        """运行 MCP 服务器"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )
    
    def close(self):
        """关闭 SSH 连接"""
        if self.ssh_client:
            self.ssh_client.close()


async def main():
    """主函数"""
    server = AstrBotMCPServer()
    try:
        await server.run()
    finally:
        server.close()


if __name__ == "__main__":
    asyncio.run(main())