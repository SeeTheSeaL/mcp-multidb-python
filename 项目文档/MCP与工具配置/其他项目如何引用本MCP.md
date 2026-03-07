# 其他项目如何引用本 MCP（mcp-multidb-python）

本 MCP 以 **stdio 传输** 运行，任何支持 MCP 的客户端通过「启动子进程 + 读写标准输入输出」即可使用。其他项目/工作区引用方式如下。

---

## 0. 推荐：零安装直接运行（引用方无需编译/安装）

**引用本 MCP 的项目不需要执行任何 pip install 或编译**，只需在 MCP 配置里指向本仓库的启动脚本即可。

1. **本仓库**只需做一次环境准备（克隆后在本仓库目录执行）：
   ```bash
   cd /path/to/mcp-multidb-python
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```
2. **引用方**在 Cursor 等客户端的 MCP 配置中填写（路径改为本机实际路径）：

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

- **macOS/Linux**：`command` 填 **`run.sh` 的绝对路径**，`args` 留空 `[]`。
- **Windows**：`command` 填 **`run.bat` 的绝对路径**（或 `cmd /c run.bat` 等按客户端要求），`cwd` 仍为本仓库根目录。

脚本会自动设置 `PYTHONPATH=src` 并优先使用本仓库的 `.venv`，因此**无需在本仓库执行 `pip install -e .`**，引用方也无需安装本包。

---

## 1. 在 Cursor 中引用（其他写法）

### 1.1 全局配置（所有项目都能用）

若已在本仓库执行过 `pip install -e .` 或使用系统/其它 Python 安装过本包，也可用以下方式（路径以你本机为准）：

- **macOS**：`~/.cursor/mcp.json`
- **或**：Cursor 设置 → MCP → 编辑配置文件

```json
{
  "mcpServers": {
    "multidb-python": {
      "command": "/path/to/mcp-multidb-python/.venv/bin/python",
      "args": ["-m", "mcp_multidb.main"],
      "cwd": "/path/to/mcp-multidb-python"
    }
  }
}
```

- 将 `/path/to/mcp-multidb-python` 换成**本仓库的绝对路径**。
- **更推荐**用上一节的 `run.sh` / `run.bat` 方式，引用方零配置、无需编译。

### 1.2 仅当前项目使用（工作区配置）

在**要使用多库查询的那个项目**根目录下建 `.cursor/mcp.json`（或项目内 Cursor 指定的 MCP 配置路径），内容同上，只保留 `multidb-python` 这一段即可。  
`cwd` 仍指向本 MCP 项目目录，这样只有打开该项目时才会启动本 MCP。

---

## 2. 在其他 MCP 客户端中引用（Claude Desktop、自定义客户端等）

思路相同：在客户端的 MCP 配置里，用「命令 + 工作目录」启动本服务。

### Claude Desktop

在 Claude Desktop 的 MCP 配置（如 `~/Library/Application Support/Claude/claude_desktop_config.json`）中增加：

```json
{
  "mcpServers": {
    "multidb-python": {
      "command": "/path/to/mcp-multidb-python/.venv/bin/python",
      "args": ["-m", "mcp_multidb.main"],
      "cwd": "/path/to/mcp-multidb-python"
    }
  }
}
```

### 通用要点

- **command**：能执行 Python 且已安装本包的解释器（推荐用本仓库 `.venv` 的 `python`）。
- **args**：`["-m", "mcp_multidb.main"]`，固定即可。
- **cwd**：**必须**是本 MCP 项目根目录，因为：
  - 会在这里找 `lib/`（JDBC 驱动 jar）
  - 会在这里找 `connections.json`（除非用环境变量覆盖，见下）。

---

## 3. 连接配置放在「其他项目」里（同一台机器）

若希望连接信息放在**业务项目**里，而不是写在 mcp-multidb-python 的 `connections.json` 中，可以：

- 在业务项目里维护自己的 `connections.json`（或任意路径、任意文件名）。
- 启动本 MCP 时通过环境变量指定该文件，例如：

```json
{
  "mcpServers": {
    "multidb-python": {
      "command": "/path/to/mcp-multidb-python/.venv/bin/python",
      "args": ["-m", "mcp_multidb.main"],
      "cwd": "/path/to/mcp-multidb-python",
      "env": {
        "MULTIDB_CONFIG_PATH": "/path/to/other-project/connections.json"
      }
    }
  }
}
```

- 或把整份连接 JSON 放进环境变量（适合 CI/临时环境）：
  - `MULTIDB_CONNECTIONS='{"conn1":{"url":"jdbc:...","user":"...","password":"..."}}'`

这样「引用」的仍是本 MCP 项目（command + cwd），只是**数据源配置**来自其他项目。

---

## 4. 作为 Python 依赖被其他项目安装并启动

其他 Python 项目也可以把本仓库当作依赖安装，在代码里启动 MCP 进程（例如用 subprocess 或 MCP SDK 的 StdioServerTransport）。

### 4.1 安装方式

在**其他项目**的虚拟环境中：

```bash
# 从本地路径安装（开发/引用本仓库）
pip install -e /path/to/mcp-multidb-python
```

或发布到内网 PyPI 后：

```bash
pip install mcp-multidb-python
```

### 4.2 在其它项目中启动本 MCP

- **方式 A**：在**本 MCP 项目根目录**下启动（保证 `lib/`、`connections.json` 可被找到）：

```bash
cd /path/to/mcp-multidb-python
/path/to/other-project/.venv/bin/python -m mcp_multidb.main
```

- **方式 B**：在任意目录启动，通过环境变量指定配置和（若需要）驱动路径；当前实现是通过 `cwd` 找 `lib/`，因此若不在本仓库根目录运行，需要保证 `cwd` 或代码里对 `lib` 的解析指向正确目录（或后续在项目里扩展支持通过环境变量指定 lib 路径）。

推荐：由**其他项目**在配置或脚本里写死「本 MCP 项目根路径」，然后用 subprocess 以该路径为 `cwd` 启动 `python -m mcp_multidb.main`，这样无需改本 MCP 代码即可引用。

---

## 5. 小结

| 场景           | 引用方式 |
|----------------|----------|
| **零安装（推荐）** | `command` 填 **`run.sh`（或 Windows 下 `run.bat`）的绝对路径**，`args` 为 `[]`，`cwd` 为本仓库根目录；引用方无需编译或安装本包。 |
| Cursor 全局    | 在 `~/.cursor/mcp.json` 中配置 command + args + cwd 指向本仓库。 |
| Cursor 某项目  | 在该项目下 `.cursor/mcp.json` 中配置同上。 |
| Claude Desktop | 在 Claude 的 MCP 配置里添加同上的一段。 |
| 连接配置在别处 | 使用 `MULTIDB_CONFIG_PATH` 或 `MULTIDB_CONNECTIONS`，command/cwd 仍指向本 MCP。 |
| 其他 Python 项目 | 可同样用 `run.sh`/`run.bat` 路径启动，或 `pip install -e` 后以本仓库根为 cwd 启动 `python -m mcp_multidb.main`。 |

**注意**：  
- `cwd` 必须指向本 MCP 项目根目录，否则找不到 `lib/` 和默认的 `connections.json`。  
- 使用本仓库自带的 `.venv` 可避免与其他项目的 Python 依赖冲突。  
- 使用 **run.sh / run.bat** 时，本仓库内无需执行 `pip install -e .`，只需 `pip install -r requirements.txt`（在 .venv 中）即可。
