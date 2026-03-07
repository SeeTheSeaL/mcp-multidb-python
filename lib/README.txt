本目录用于存放 JDBC 驱动 jar。Python 通过 JPype 调用 JVM 加载这些驱动连接数据库。

当前已预置（从 Maven Central 下载）：
  - Oracle：ojdbc8-21.9.0.0.jar（com.oracle.database.jdbc:ojdbc8）
  - MySQL：mysql-connector-j-8.2.0.jar（com.mysql:mysql-connector-j）
  - SQL Server：mssql-jdbc-12.10.0.jre8.jar（com.microsoft.sqlserver:mssql-jdbc）

可按需自行添加其他驱动，例如：
  - PostgreSQL：postgresql-42.x.x.jar

无需修改工程代码，与 Java 项目使用同一批驱动文件。
