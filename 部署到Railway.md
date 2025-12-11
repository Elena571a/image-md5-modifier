# 部署到Railway - 详细步骤

Railway是最简单的免费部署方案，提供$5/月的免费额度，足够使用。

## 准备工作

1. 注册GitHub账号（如果没有）
2. 将代码上传到GitHub

## 步骤一：上传代码到GitHub

1. 在GitHub创建新仓库
2. 在本地执行：
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/你的用户名/仓库名.git
git push -u origin main
```

## 步骤二：部署到Railway

1. **访问Railway**
   - 打开 https://railway.app
   - 点击"Start a New Project"

2. **登录**
   - 选择"Login with GitHub"
   - 授权Railway访问你的GitHub

3. **部署项目**
   - 选择"Deploy from GitHub repo"
   - 选择你刚创建的仓库
   - Railway会自动检测Flask应用

4. **配置环境变量（可选）**
   - 在项目设置中可以配置环境变量
   - 如：`PORT=5001`

5. **获取访问地址**
   - Railway会自动分配一个域名
   - 格式：`你的项目名.up.railway.app`
   - 点击域名即可访问

## 步骤三：修改代码以适配Railway

Railway会自动检测Flask应用，但可能需要小调整：

### 修改 app.py

```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port)
```

### 创建 Procfile（可选）

在项目根目录创建 `Procfile` 文件：
```
web: python app.py
```

或者使用gunicorn（推荐生产环境）：
```
web: gunicorn app:app
```

## 步骤四：安装gunicorn（生产环境推荐）

在 `requirements.txt` 添加：
```
gunicorn>=20.1.0
```

修改启动方式，使用gunicorn更稳定。

## 自动部署

Railway支持自动部署：
- 每次push代码到GitHub
- Railway会自动重新部署
- 无需手动操作

## 查看日志

在Railway控制台可以查看：
- 应用日志
- 部署历史
- 资源使用情况

## 免费额度

- $5/月免费额度
- 足够个人使用
- 超出后按使用量付费

## 常见问题

**Q: 部署后无法访问？**
A: 检查日志，可能是端口配置问题

**Q: 如何更新代码？**
A: 直接push到GitHub，Railway会自动部署

**Q: 文件存储在哪里？**
A: Railway的临时存储，重启会丢失，建议使用云存储服务

