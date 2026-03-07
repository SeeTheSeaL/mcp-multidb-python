# -*- coding: utf-8 -*-
"""通过 JPype 调用 JVM，使用 lib/*.jar 中的 JDBC 驱动连接数据库。"""
from __future__ import annotations

import glob
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

_jvm_started = False
_driver_manager = None
_result_set = None
_connection = None


def _lib_classpath() -> str:
    # 优先使用当前工作目录下的 lib/（运行时常在项目根）
    for root in [Path.cwd(), Path(__file__).resolve().parent.parent.parent]:
        lib = root / "lib"
        if lib.is_dir():
            jars = list(lib.glob("*.jar"))
            if jars:
                sep = ";" if os.name == "nt" else ":"
                return sep.join(str(j) for j in jars)
    return ""


def ensure_jvm():
    global _jvm_started
    if _jvm_started:
        return
    import jpype
    if jpype.isJVMStarted():
        _jvm_started = True
        return
    cp = _lib_classpath()
    if not cp:
        raise RuntimeError("lib/ 目录下未找到任何 .jar，请将 JDBC 驱动（如 ojdbc8.jar）放入 lib/")
    jpype.startJVM(jpype.getDefaultJVMPath(), classpath=[cp], convertStrings=True)
    _jvm_started = True


def _jvalue(val: Any) -> Any:
    """将 Java 对象转为 Python 可序列化类型。"""
    if val is None:
        return None
    try:
        if hasattr(val, "toString"):
            return val.toString()
    except Exception:
        pass
    try:
        return float(val) if isinstance(val, (int, float)) else str(val)
    except Exception:
        return str(val)


def run_query(
    jdbc_url: str,
    user: str,
    password: str,
    sql: str,
) -> Dict[str, Any]:
    """执行只读 SQL，返回 { columns, rows, rowCount }。"""
    import jpype
    ensure_jvm()
    DriverManager = jpype.JClass("java.sql.DriverManager")
    conn = DriverManager.getConnection(jdbc_url, user or "", password or "")
    try:
        stmt = conn.createStatement()
        rs = stmt.executeQuery(sql.strip())
        meta = rs.getMetaData()
        n = meta.getColumnCount()
        columns = [meta.getColumnLabel(i + 1) for i in range(n)]
        rows: List[Dict[str, Any]] = []
        while rs.next():
            row = {}
            for i in range(n):
                v = rs.getObject(i + 1)
                row[columns[i]] = _jvalue(v)
            rows.append(row)
        return {"columns": columns, "rows": rows, "rowCount": len(rows)}
    finally:
        conn.close()


def list_tables(
    jdbc_url: str,
    user: str,
    password: str,
    schema: Optional[str] = None,
) -> List[str]:
    """返回表名列表。Oracle 可传 schema=user，PostgreSQL 默认 public。"""
    import jpype
    ensure_jvm()
    DriverManager = jpype.JClass("java.sql.DriverManager")
    conn = DriverManager.getConnection(jdbc_url, user or "", password or "")
    try:
        meta = conn.getMetaData()
        catalog = None
        schema_pattern = schema or ("public" if "postgresql" in jdbc_url.lower() else None)
        if "oracle" in jdbc_url.lower() and user:
            schema_pattern = user.upper()
        rs = meta.getTables(catalog, schema_pattern, None, ["TABLE", "VIEW"])
        tables = []
        while rs.next():
            tables.append(rs.getString(3))
        return sorted(tables)
    finally:
        conn.close()
