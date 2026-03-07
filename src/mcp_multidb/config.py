# -*- coding: utf-8 -*-
"""从 connections.json 或环境变量加载配置，与 Java 版格式兼容。"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_CONFIG_PATH = "connections.json"


def _get_jdbc_url(entry: Dict[str, Any]) -> Optional[str]:
    url = entry.get("url")
    if url and str(url).strip():
        return str(url).strip()
    t = (entry.get("type") or "").strip().lower()
    if t == "oracle":
        cs = entry.get("connectString") or ""
        if cs.strip():
            prefix = "" if "//" in cs else "//"
            return "jdbc:oracle:thin:@" + prefix + cs.strip()
        host, port = entry.get("host"), entry.get("port") or 1521
        sn = entry.get("serviceName")
        if host and sn:
            return f"jdbc:oracle:thin:@//{host}:{port}/{sn}"
    if t == "mysql":
        host = entry.get("host") or "localhost"
        port = entry.get("port") or 3306
        db = entry.get("database") or ""
        return f"jdbc:mysql://{host}:{port}/{db}?useUnicode=true&characterEncoding=utf-8&useSSL=false"
    if t in ("postgres", "postgresql"):
        host = entry.get("host") or "localhost"
        port = entry.get("port") or 5432
        db = entry.get("database") or ""
        return f"jdbc:postgresql://{host}:{port}/{db}"
    if t in ("sqlserver", "mssql"):
        host = entry.get("host") or "localhost"
        port = entry.get("port") or 1433
        db = entry.get("database") or ""
        return f"jdbc:sqlserver://{host}:{port};databaseName={db}" if db else f"jdbc:sqlserver://{host}:{port}"
    if t in ("dm", "dameng"):
        host = entry.get("host") or "localhost"
        port = entry.get("port") or 5236
        return f"jdbc:dm://{host}:{port}"
    return None


def load_config() -> Dict[str, Dict[str, Any]]:
    raw = os.environ.get("MULTIDB_CONNECTIONS")
    if raw and raw.strip():
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}
    path = os.environ.get("MULTIDB_CONFIG_PATH") or str(Path.cwd() / DEFAULT_CONFIG_PATH)
    p = Path(path)
    if not p.is_file():
        return {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def get_jdbc_url(connection_id: str, config: Dict[str, Dict[str, Any]]) -> Optional[str]:
    entry = config.get(connection_id)
    return entry and _get_jdbc_url(entry)
