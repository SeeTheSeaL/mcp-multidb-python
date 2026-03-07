# 推送到 GitHub 步骤

本地已完成首次提交，可按以下方式推到 GitHub。

## 方式一：网页创建仓库后推送

1. 在 GitHub 上新建仓库：
   - 打开 https://github.com/new
   - **Repository name** 填：`mcp-multidb-python`（或你喜欢的名字）
   - 选择 **Public**，**不要**勾选 “Add a README file”
   - 点击 **Create repository**

2. 在项目根目录添加远程并推送（将 `YOUR_USERNAME` 换成你的 GitHub 用户名）：

   ```bash
   cd /path/to/mcp-multidb-python
   git remote add origin https://github.com/YOUR_USERNAME/mcp-multidb-python.git
   git branch -M main
   git push -u origin main
   ```

   若使用 SSH：

   ```bash
   git remote add origin git@github.com:YOUR_USERNAME/mcp-multidb-python.git
   git push -u origin main
   ```

## 方式二：使用 GitHub CLI

若已安装 [GitHub CLI](https://cli.github.com/)（`gh`）并登录：

```bash
cd /path/to/mcp-multidb-python
gh repo create mcp-multidb-python --public --source=. --remote=origin --push
```

会自动创建仓库、添加远程并推送。
