#!/usr/bin/env bash
# 直接运行本 MCP，无需在引用方或本仓库执行 pip install。
# 使用方式：在 Cursor 等客户端中 command 填本脚本绝对路径，args 留空，cwd 填本仓库根目录。
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}"
if [ -x "${ROOT}/.venv/bin/python" ]; then
  exec "${ROOT}/.venv/bin/python" -m mcp_multidb.main
else
  exec python3 -m mcp_multidb.main
fi
