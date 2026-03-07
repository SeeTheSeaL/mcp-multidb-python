@echo off
REM 直接运行本 MCP，无需在引用方或本仓库执行 pip install。
REM 使用方式：在 Cursor 等客户端中 command 填本脚本绝对路径，args 留空，cwd 填本仓库根目录。
cd /d "%~dp0"
set "PYTHONPATH=%CD%\src;%PYTHONPATH%"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m mcp_multidb.main
) else (
  python -m mcp_multidb.main
)
