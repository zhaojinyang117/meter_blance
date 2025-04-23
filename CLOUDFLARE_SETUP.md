# Cloudflare Pages 设置指南

本文档详细说明如何设置Cloudflare账号和API令牌，以便成功部署电表余额监控网站。

## 1. 创建Cloudflare账号

如果你还没有Cloudflare账号，请先注册：

1. 访问 [Cloudflare官网](https://www.cloudflare.com/)
2. 点击"Sign Up"按钮
3. 按照提示完成注册流程

## 2. 获取Cloudflare账号ID

1. 登录Cloudflare仪表板
2. 在右侧边栏底部找到你的账号ID
3. 复制此ID，稍后将用于GitHub Secrets

## 3. 创建API令牌

Cloudflare Pages需要一个具有特定权限的API令牌：

1. 在Cloudflare仪表板中，点击右上角的个人头像
2. 选择"My Profile"
3. 在左侧导航栏中选择"API Tokens"
4. 点击"Create Token"按钮
5. 选择"Create Custom Token"
6. 设置令牌名称，例如"GitHub Actions Pages Deploy"
7. 在"Permissions"部分，添加以下权限：
   - Account > Account Settings > Read
   - Account > Cloudflare Pages > Edit
   - User > User Details > Read
8. 在"Account Resources"部分，选择"Include > Specific account"并选择你的账号
9. 点击"Continue to summary"按钮
10. 点击"Create Token"按钮
11. 复制生成的令牌，稍后将用于GitHub Secrets（注意：此令牌只会显示一次）

## 4. 在GitHub仓库中添加Secrets

1. 访问你的GitHub仓库
2. 点击"Settings"标签
3. 在左侧导航栏中选择"Secrets and variables" > "Actions"
4. 点击"New repository secret"按钮
5. 添加以下两个Secrets：
   - 名称：`CLOUDFLARE_ACCOUNT_ID`，值：你的Cloudflare账号ID
   - 名称：`CLOUDFLARE_API_TOKEN`，值：你创建的API令牌

## 5. 手动触发部署工作流

1. 在GitHub仓库中，切换到`cloudflare`分支
2. 点击"Actions"标签
3. 在左侧找到"电表余额监控网站部署"工作流
4. 点击"Run workflow"按钮
5. 确认选择的是`cloudflare`分支
6. 点击绿色的"Run workflow"按钮

## 6. 验证部署

1. 工作流成功运行后，访问Cloudflare仪表板
2. 点击左侧导航栏中的"Pages"
3. 你应该能看到新创建的"meter-balance-monitor"项目
4. 点击项目名称查看详情
5. 在"Deployments"标签下，你可以找到部署的URL
6. 点击URL访问你的电表余额监控网站

## 常见问题排查

### API令牌验证失败

- 确保API令牌具有正确的权限（Account Settings Read, Cloudflare Pages Edit, User Details Read）
- 确保令牌未过期
- 尝试创建一个新的API令牌

### 账号ID无效

- 确保复制的是完整的账号ID
- 账号ID通常是一串32位的字母数字组合
- 在Cloudflare仪表板右侧边栏底部可以找到

### 部署失败

- 检查GitHub Actions运行日志以获取详细错误信息
- 确保所有网站文件（index.html, styles.css, script.js, data.json）都存在
- 尝试在本地使用Wrangler CLI测试部署
