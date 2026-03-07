---
name: multidb-sql-analysis
description: When analyzing code that involves database access, SQL queries, JDBC, or ORM usage, invokes the mcp-multidb-python MCP (multidb_list_connections, multidb_list_tables, multidb_query) to list connections, list tables, and run read-only SQL for database call analysis. Use when reviewing or understanding code that contains SQL, database queries, or data access logic.
---

# 数据库 SQL 调用分析（多库 MCP）

本项目已配置 **mcp-multidb-python** MCP。在分析涉及数据库访问、SQL 查询或数据访问的代码时，应调用该 MCP 对数据库调用进行实际连接与只读分析。

## 何时使用

- 代码中出现 **SQL 语句**（原生 SQL、拼接 SQL、预编译语句等）
- 代码涉及 **JDBC**、**ORM**（如 MyBatis、JPA、Hibernate）、**数据源/连接池** 等
- 需要理解某段代码访问了哪些**表、字段**，或查询逻辑与实际数据是否一致
- 需要**验证表结构、列名**或**执行只读查询**以辅助代码分析

## 分析流程

1. **识别数据访问点**：在目标代码中定位 SQL 文本、Mapper 方法、Repository 调用、JDBC 使用等。
2. **调用 MCP**：使用 **multidb_list_connections** 查看已配置连接 ID，根据代码中的库名/数据源确定 `connectionId`。
3. **查看表结构**：使用 **multidb_list_tables**（传入 `connectionId`）列出表；必要时用 **multidb_query** 执行只读 SQL（如 `SELECT * FROM 表名 WHERE 1=0` 或 `DESCRIBE 表名`）确认列信息。
4. **结合结果分析**：将代码中的表名、列名与 MCP 返回结果对照，判断 SQL 是否访问不存在的表/列或逻辑是否符合实际库结构。

## MCP 工具

| 工具 | 用途 |
|------|------|
| multidb_list_connections | 列出已配置连接 ID 及类型 |
| multidb_list_tables | 按 connectionId 列出该库下所有表名 |
| multidb_query | 按 connectionId + sql 执行只读 SQL，返回行数据 |

仅执行只读 SQL，不进行写操作。连接由本项目的 MCP 配置（如 `MULTIDB_CONFIG_PATH` 或 `connections.json`）决定。
