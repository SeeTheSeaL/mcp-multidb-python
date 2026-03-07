# mcp-multidb-python

基于 **Python + JPype** 的多数据源 MCP 服务：通过 **JDBC 驱动（.jar）** 连接数据库，与 Java 项目共用同一套驱动，无需改本仓库代码，只需在 `lib/` 放入对应驱动即可。

- **MCP 协议**：stdio 传输，协议版本 2024-11-05  
- **能力**：只读（列举连接、列举表、执行只读 SQL）  
- **连接配置**：支持本仓库默认配置，或由引用方通过环境变量指定「项目自有」配置

---

## 依赖

| 依赖 | 说明 |
|------|------|
| Python | 3.8+ |
| JDK | 已安装，供 JPype 启动 JVM |
| 驱动 jar | 放入项目根目录 **`lib/`**，与 Java 项目一致 |

---

## 项目结构

```
mcp-multidb-python/
├── run.sh             # 直接运行脚本（零安装，推荐给引用方使用）
├── run.bat            # Windows 直接运行脚本
├── src/mcp_multidb/
│   ├── main.py        # MCP 入口（stdio JSON-RPC）
│   ├── config.py      # 连接配置加载
│   └── jdbc_bridge.py # JVM + JDBC 桥接
├── lib/               # JDBC 驱动 jar（需自行放入）
├── connections.json   # 默认连接配置（可选，可被环境变量覆盖）
├── connections.json.example
├── pyproject.toml
├── requirements.txt
├── scripts/           # 测试脚本（如 scripts/test_connection.py）
└── 项目文档/           # 说明与引用方式
    ├── MCP与工具配置/
    │   ├── 其他项目如何引用本MCP.md
    │   ├── 连接测试说明.md
    │   ├── 推送到GitHub步骤.md
    │   └── skill-for-callers/        # 给引用方拷贝的 Cursor Skill
    │       ├── README.md
    │       └── multidb-sql-analysis/
    │           └── SKILL.md
    └── 项目分析/
        └── mcp-multidb-python 项目分析.md
```

---

## 安装与运行

### 方式一：零安装直接运行（推荐，引用方无需编译）

**其他项目引用本 MCP 时不需要在本仓库执行 `pip install -e .`**，只需：

1. 在本仓库目录**一次性**准备环境并安装依赖：
   ```bash
   cd /path/to/mcp-multidb-python
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```
2. 将需要的 JDBC 驱动放入 `lib/`。
3. 在 Cursor 等客户端的 MCP 配置中，**command** 填 **`run.sh`（Linux/macOS）或 `run.bat`（Windows）的绝对路径**，**args** 留空 `[]`，**cwd** 填本仓库根目录。

脚本会自动设置 `PYTHONPATH` 并优先使用本仓库的 `.venv`，引用方无需安装或编译本包。详见 [其他项目如何引用本 MCP](项目文档/MCP与工具配置/其他项目如何引用本MCP.md)。

### 方式二：安装后运行

```bash
# 克隆或进入项目目录后
pip install -e .

# 将需要的 JDBC 驱动放入 lib/

# 以前台方式运行（供 MCP 客户端通过 stdio 调用）
python -m mcp_multidb.main
# 或安装后
mcp-multidb-python
```

实际使用时由 **Cursor、Claude Desktop 等 MCP 客户端** 按配置启动上述命令，无需在终端常驻运行。

---

## 连接配置

配置来源（按优先级）：

1. **环境变量 `MULTIDB_CONNECTIONS`**：整份连接 JSON 字符串（适合 CI/临时环境）
2. **环境变量 `MULTIDB_CONFIG_PATH`**：配置文件的**绝对路径**（推荐给「每个项目一份配置」）
3. **默认路径**：`cwd` 下的 `connections.json`（本仓库或客户端启动时的工作目录）

### 配置格式

与常见 Java JDBC 配置兼容。可直接写 JDBC URL，或按 `type` 拼 URL：

```json
{
  "conn_id": {
    "url": "jdbc:oracle:thin:@//host:1521/service",
    "user": "user",
    "password": "pass"
  },
  "mysql_db": {
    "type": "mysql",
    "host": "localhost",
    "port": 3306,
    "database": "mydb",
    "user": "user",
    "password": "pass"
  },
  "dm_db": {
    "url": "jdbc:dm://host:5236",
    "user": "user",
    "password": "pass"
  }
}
```

### 支持的数据库类型

| type | 说明 |
|------|------|
| 直接写 `url` | 任意 JDBC URL，只要 `lib/` 中有对应驱动 |
| `oracle` | Oracle（connectString 或 host + serviceName） |
| `mysql` | MySQL |
| `postgres` / `postgresql` | PostgreSQL |
| `sqlserver` / `mssql` | SQL Server |
| `dm` / `dameng` | 达梦 |

---

## lib/ 驱动

将对应数据库的 **JDBC 驱动 jar** 放入 **`lib/`** 即可，与 Java 项目使用同一批文件。例如：

- **Oracle**：ojdbc8.jar、ojdbc6.jar 等  
- **MySQL**：mysql-connector-j-8.x.x.jar  
- **PostgreSQL**：postgresql-42.x.x.jar  
- **SQL Server**：mssql-jdbc-xxx.jar  
- **达梦**：DmJdbcDriver18-xxx.jar  

未放入的驱动对应的数据库无法连接，无需改代码。

---

## MCP 工具

| 工具 | 说明 | 参数 |
|------|------|------|
| **multidb_list_connections** | 列出已配置的连接 ID 及类型 | 无 |
| **multidb_list_tables** | 列出指定连接下的表名 | `connectionId`（必填） |
| **multidb_query** | 在指定连接上执行只读 SQL | `connectionId`、`sql`（必填） |

所有查询均为只读，不执行写操作。

### 给引用方用的 Cursor Skill（拷贝即用）

已配置本 MCP 的项目，可从本仓库拷贝现成 Skill，在分析涉及数据库/SQL 的代码时让 Agent 自动调用本 MCP 做数据库调用分析：

- **拷贝**：将 **`项目文档/MCP与工具配置/skill-for-callers/multidb-sql-analysis`** 整个文件夹拷贝到你的项目的 **`.cursor/skills/`** 下。
- **说明**：[skill-for-callers/README.md](项目文档/MCP与工具配置/skill-for-callers/README.md)

---

## 在 Cursor 等客户端中使用

推荐使用 **run.sh / run.bat**（零安装），将 `/path/to/mcp-multidb-python` 换成你本机上的本仓库路径。

### 使用本仓库默认配置

`cwd` 指向本仓库根目录，连接从本仓库的 `connections.json` 读取：

```json
{
  "mcpServers": {
    "multidb-python": {
      "command": "/path/to/mcp-multidb-python/run.sh",
      "args": [],
      "cwd": "/path/to/mcp-multidb-python"
    }
  }
}
```

Windows 下可将 `run.sh` 改为 `run.bat` 的绝对路径。

### 使用项目自有连接配置（推荐）

每个引用本 MCP 的项目各自维护一份连接配置，通过 **`MULTIDB_CONFIG_PATH`** 指定**绝对路径**：

```json
{
  "mcpServers": {
    "multidb-python": {
      "command": "/path/to/mcp-multidb-python/run.sh",
      "args": [],
      "cwd": "/path/to/mcp-multidb-python",
      "env": {
        "MULTIDB_CONFIG_PATH": "/path/to/your-project/.cursor/multidb-connections.json"
      }
    }
  }
}
```

将上述配置写在**该项目**的 `.cursor/mcp.json` 中，连接文件加入 `.gitignore`，避免密码入库。

---

## 文档

| 文档 | 说明 |
|------|------|
| [其他项目如何引用本 MCP](项目文档/MCP与工具配置/其他项目如何引用本MCP.md) | 全局/工作区配置、Claude Desktop、零安装与 Python 依赖 |
| [skill-for-callers 使用说明](项目文档/MCP与工具配置/skill-for-callers/README.md) | 引用方拷贝 Skill 到 `.cursor/skills/` 的步骤 |
| [连接测试说明](项目文档/MCP与工具配置/连接测试说明.md) | 用 MCP 工具验证连接、lib/ 驱动 |
| [推送到 GitHub 步骤](项目文档/MCP与工具配置/推送到GitHub步骤.md) | 本地提交后推送到 GitHub |
| [项目分析](项目文档/项目分析/mcp-multidb-python%20项目分析.md) | 项目结构与模块说明 |

---

## 许可证与说明

- 本服务仅提供**只读**能力，不执行 DML/DDL。
- 连接配置含账号密码，请勿提交到公共仓库；建议使用环境变量或项目内 `.gitignore` 的配置文件。
