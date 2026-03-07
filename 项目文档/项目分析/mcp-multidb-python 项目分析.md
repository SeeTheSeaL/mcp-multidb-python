# mcp-multidb-python 项目分析

## 1. 项目概述

**mcp-multidb-python** 是一个基于 **Python + JPype** 的多数据源 MCP（Model Context Protocol）服务。它通过 **JDBC 驱动 jar** 连接数据库，与 Java 项目共用同一套驱动（如 Oracle 的 ojdbc8.jar），无需在 Python 侧维护另一套数据库驱动。

- **定位**：MCP 服务端，供 Cursor 等客户端通过 stdio 调用，对多个数据库执行只读查询、列表等操作。
- **技术栈**：Python 3.8+、JPype1、JDBC（通过 JVM 加载 lib/*.jar）。
- **配置**：`connections.json` 或环境变量，与 Java 版格式兼容。

---

## 2. 目录与文件结构

```
mcp-multidb-python/
├── pyproject.toml          # 项目元数据、依赖、入口脚本
├── requirements.txt        # 依赖：jpype1>=1.4.0
├── README.md               # 使用说明
├── lib/                    # JDBC 驱动 jar 存放目录（当前仅有 .gitkeep + README.txt）
│   ├── .gitkeep
│   └── README.txt
└── src/
    └── mcp_multidb/
        ├── __init__.py     # 版本号 __version__ = "1.0.0"
        ├── main.py         # MCP 服务入口、JSON-RPC 分发、工具实现
        ├── config.py       # 配置加载、JDBC URL 拼装
        └── jdbc_bridge.py  # JPype 桥接、JVM 启动、执行 SQL / 列表
```

- **无** `connections.json` 示例文件（需用户自建或通过环境变量提供）。
- **mcps/**：为 Cursor 的 MCP 描述符目录，与本项目“多库 MCP 服务”代码分离，用于暴露工具给 IDE。

---

## 3. 核心模块说明

### 3.1 `main.py` — MCP 服务与工具

- **传输**：stdio，一行一个 JSON-RPC 请求。
- **协议**：MCP，`protocolVersion: "2024-11-05"`。
- **支持方法**：
  - `initialize`：返回协议版本与 serverInfo。
  - `tools/list`：返回三个工具定义。
  - `tools/call`：根据 `name` 调用对应工具，传入 `arguments`。
- **工具**：
  1. **multidb_list_connections**  
     列出已配置连接 ID 及类型（mysql/postgres/oracle），无入参。
  2. **multidb_list_tables**  
     入参：`connectionId`。返回该连接下所有表名（Oracle 会按 user 作 schema）。
  3. **multidb_query**  
     入参：`connectionId`、`sql`。在指定连接上执行只读 SQL，返回 `rowCount` 与 `rows`（列表 of 字典）。

错误统一通过 `isError: true` 与 `content[].text` 返回；正常结果以 JSON 文本放在 `content[].text`。

### 3.2 `config.py` — 配置与 JDBC URL

- **配置来源**（优先级从高到低）：
  1. 环境变量 `MULTIDB_CONNECTIONS`（整份 JSON 字符串）。
  2. 环境变量 `MULTIDB_CONFIG_PATH` 指定文件路径。
  3. 默认路径：当前工作目录下的 `connections.json`。
- **连接条目**：支持两种形式：
  - 直接写 **url**：`"url": "jdbc:oracle:thin:@//host:port/servicename"` 等。
  - 按 **type** 拼 URL：`type` 为 `oracle` / `mysql` / `postgres`(或`postgresql`)，配合 `host`、`port`、`database`、`connectString`（Oracle）、`serviceName` 等。
- **get_jdbc_url(connection_id, config)**：根据 connection_id 从 config 取条目并得到最终 JDBC URL，供 `jdbc_bridge` 使用。

### 3.3 `jdbc_bridge.py` — JVM 与 JDBC

- **classpath**：在 `Path.cwd()` 与包所在项目根之间查找 `lib/`，将所有 `*.jar` 拼成 classpath（Windows 用 `;`，其余用 `:`）。
- **JVM**：通过 JPype 启动一次，`convertStrings=True`，未找到 jar 则抛 `RuntimeError`。
- **run_query**：  
  `DriverManager.getConnection(url, user, password)` → `createStatement()` → `executeQuery(sql)`，遍历 ResultSet，用 `getMetaData()` 取列名，`getObject` 取值并经 `_jvalue()` 转为 Python 可序列化类型，返回 `{ columns, rows, rowCount }`。
- **list_tables**：  
  同样 getConnection，然后 `conn.getMetaData().getTables(...)`；Oracle 用 user 作 schema，PostgreSQL 默认 schema 为 `public`，返回排序后的表名列表。

---

## 4. 依赖与运行

- **依赖**：`jpype1>=1.4.0`；需本机已安装 JDK（JPype 会启动 JVM）。
- **安装**：`pip install -e .` 或 `pip install -r requirements.txt`。
- **运行**：在项目根目录执行 `python -m mcp_multidb.main`（或安装后命令 `mcp-multidb-python`），确保当前工作目录下能找到 `lib/` 与 `connections.json`（或通过环境变量提供配置）。

---

## 5. 与 Cursor 的集成

在 Cursor 的 MCP 配置中指定解释器与工作目录，例如：

```json
{
  "mcpServers": {
    "multidb-python": {
      "command": "python",
      "args": ["-m", "mcp_multidb.main"],
      "cwd": "/path/to/mcp-multidb-python"
    }
  }
}
```

这样 Cursor 会以 stdio 方式启动该进程，并可通过 MCP 工具 `multidb_list_connections`、`multidb_list_tables`、`multidb_query` 访问已配置的数据库。

---

## 6. 小结与可改进点

- **优点**：与 Java 共用 JDBC 驱动、配置格式兼容、实现集中、只读安全（仅查询与列表）。
- **当前缺失**：
  - 仓库内无 `connections.json` 示例（可增加 `connections.json.example` 并加入 .gitignore 对 `connections.json` 的说明）。
  - `lib/` 下暂无真实 jar（仅有说明），需用户自行放入驱动。
- **可扩展方向**：更多数据库 type 的 URL 拼装、连接池、超时与只读强制校验、日志与审计等；若需在 Cursor 中更好发现，可核对 mcps 中工具名与参数是否与 `_tools_list()` 一致。

以上为对当前 mcp-multidb-python 项目的整体分析。
