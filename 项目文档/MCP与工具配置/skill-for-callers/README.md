# 给「引用本 MCP 的项目」使用的 Skill（拷贝即用）

本目录提供现成 Skill，供**已配置 mcp-multidb-python MCP** 的项目使用。拷贝到你的项目后，在分析涉及数据库/SQL 的代码时，Agent 会优先调用该 MCP 做数据库调用分析。

## 使用方法

1. 将 **`multidb-sql-analysis`** 整个文件夹拷贝到你的项目下：
   ```text
   你的项目/
   └── .cursor/
       └── skills/
           └── multidb-sql-analysis/
               └── SKILL.md    ← 从本目录拷贝
   ```

2. 确保你的项目已按 [其他项目如何引用本MCP.md](../其他项目如何引用本MCP.md) 配置好 MCP（在 `.cursor/mcp.json` 或全局 MCP 中指向 mcp-multidb-python 的 `run.sh`/`run.bat` 等）。

3. 无需其他配置，Cursor 会识别 `.cursor/skills/` 下的 Skill；分析含 SQL/数据库访问的代码时会自动使用本 MCP。

## 目录说明

| 名称 | 说明 |
|------|------|
| multidb-sql-analysis/ | 技能目录，整体拷贝到你的项目的 `.cursor/skills/` 下 |
| multidb-sql-analysis/SKILL.md | 技能定义：分析代码中的数据库/SQL 时调用 MCP 做连接与只读查询分析 |
