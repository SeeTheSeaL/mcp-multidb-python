# -*- coding: utf-8 -*-
"""MCP 服务：stdio 传输，一行一个 JSON-RPC。使用 lib/ 下 JDBC 驱动连接数据库。"""
from __future__ import annotations

import json
import sys
from typing import Any, Dict, List

from .config import load_config, get_jdbc_url
from .jdbc_bridge import list_tables as jdbc_list_tables, run_query as jdbc_run_query


def _tools_list() -> List[Dict[str, Any]]:
    return [
        {
            "name": "multidb_list_connections",
            "description": "列出已配置的数据库连接 ID 及其类型（mysql/postgres/oracle）。",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "multidb_list_tables",
            "description": "列出指定连接下的所有表名。",
            "inputSchema": {
                "type": "object",
                "properties": {"connectionId": {"type": "string", "description": "连接 ID"}},
                "required": ["connectionId"],
            },
        },
        {
            "name": "multidb_query",
            "description": "在指定连接上执行只读 SQL。connectionId 为 list_connections 返回的 ID。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "connectionId": {"type": "string", "description": "连接 ID"},
                    "sql": {"type": "string", "description": "SQL 语句"},
                },
                "required": ["connectionId", "sql"],
            },
        },
    ]


def _call_tool(name: str, arguments: Dict[str, Any], config: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if name == "multidb_list_connections":
        list_conn = [
            {"connectionId": cid, "type": (e.get("type") or "unknown")}
            for cid, e in config.items()
        ]
        return {"content": [{"type": "text", "text": json.dumps(list_conn, ensure_ascii=False, indent=2)}]}

    if name == "multidb_list_tables":
        cid = (arguments.get("connectionId") or "").strip()
        if not cid:
            return {
                "content": [{"type": "text", "text": "connectionId 不能为空"}],
                "isError": True,
            }
        entry = config.get(cid)
        if not entry:
            return {
                "content": [{"type": "text", "text": f"未找到连接: {cid}"}],
                "isError": True,
            }
        url = get_jdbc_url(cid, config)
        if not url:
            return {
                "content": [{"type": "text", "text": f"无效配置: {cid}"}],
                "isError": True,
            }
        try:
            schema = None
            if (entry.get("type") or "").lower() == "oracle" and entry.get("user"):
                schema = entry["user"].upper()
            tables = jdbc_list_tables(url, entry.get("user") or "", entry.get("password") or "", schema)
            return {"content": [{"type": "text", "text": json.dumps(tables, ensure_ascii=False, indent=2)}]}
        except Exception as e:
            return {
                "content": [{"type": "text", "text": str(e)}],
                "isError": True,
            }

    if name == "multidb_query":
        cid = (arguments.get("connectionId") or "").strip()
        sql = (arguments.get("sql") or "").strip()
        if not cid or not sql:
            return {
                "content": [{"type": "text", "text": "connectionId 和 sql 均为必填"}],
                "isError": True,
            }
        entry = config.get(cid)
        if not entry:
            return {
                "content": [{"type": "text", "text": f"未找到连接: {cid}"}],
                "isError": True,
            }
        url = get_jdbc_url(cid, config)
        if not url:
            return {
                "content": [{"type": "text", "text": f"无效配置: {cid}"}],
                "isError": True,
            }
        try:
            out = jdbc_run_query(
                url,
                entry.get("user") or "",
                entry.get("password") or "",
                sql,
            )
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {"rowCount": out["rowCount"], "rows": out["rows"]},
                            ensure_ascii=False,
                            indent=2,
                        ),
                    }
                ],
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": str(e)}],
                "isError": True,
            }

    return {
        "content": [{"type": "text", "text": f"未知工具: {name}"}],
        "isError": True,
    }


def _handle_request(req: Dict[str, Any], config: Dict[str, Dict[str, Any]]) -> str:
    method = req.get("method") or ""
    rid = req.get("id")
    out = {"jsonrpc": "2.0", "id": rid}

    if method == "initialize":
        out["result"] = {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "mcp-multidb-python", "version": "1.0.0"},
            "capabilities": {"tools": {"listChanged": False}},
        }
        return json.dumps(out, ensure_ascii=False)

    if method == "tools/list":
        out["result"] = {"tools": _tools_list()}
        return json.dumps(out, ensure_ascii=False)

    if method == "tools/call":
        params = req.get("params") or {}
        name = params.get("name") or ""
        arguments = params.get("arguments") or {}
        result = _call_tool(name, arguments, config)
        out["result"] = result
        return json.dumps(out, ensure_ascii=False)

    out["error"] = {"code": -32601, "message": f"Method not found: {method}"}
    return json.dumps(out, ensure_ascii=False)


def run():
    config = load_config()
    # 不向 stderr 写启动日志，避免部分 MCP 客户端把 stderr 与 stdout 混读导致解析错误
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        req = None
        try:
            req = json.loads(line)
        except Exception:
            pass
        try:
            if req is None:
                # 解析失败，返回错误且 id 用 0（客户端不接受 id: null）
                err = {"jsonrpc": "2.0", "id": 0, "error": {"code": -32700, "message": "Invalid JSON"}}
                print(json.dumps(err), flush=True)
                continue
            # MCP 规定：无 id 的为 Notification，服务器不得回复，否则客户端会解析到 id:null 报错
            if "id" not in req or req["id"] is None:
                continue
            resp = _handle_request(req, config)
            print(resp, flush=True)
        except Exception as e:
            # Cursor 等客户端要求 id 为 string 或 number，不能为 null
            rid = req.get("id") if isinstance(req, dict) else None
            if rid is None:
                rid = 0
            err = {"jsonrpc": "2.0", "id": rid, "error": {"code": -32700, "message": str(e)}}
            print(json.dumps(err), flush=True)


if __name__ == "__main__":
    run()
