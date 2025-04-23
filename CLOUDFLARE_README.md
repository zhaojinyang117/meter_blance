# 电表余额监控网站

这是一个基于Cloudflare Pages的电表余额监控网站，用于可视化展示每日电表余额和用电量数据。

## 功能特点

- 实时显示当前电表余额
- 展示近7天的用电量图表
- 显示余额变化趋势
- 计算平均日用电量
- 预估剩余电量可用天数
- 详细的历史数据表格

## 部署步骤

### 1. 准备Cloudflare账号

1. 注册或登录 [Cloudflare](https://dash.cloudflare.com/) 账号
2. 记录你的Cloudflare账号ID（在右侧边栏可以找到）
3. 创建API令牌:
   - 进入 `My Profile > API Tokens`
   - 点击 `Create Token`
   - 选择 `Edit Cloudflare Workers` 模板
   - 确保包含 `Pages: Edit` 权限
   - 创建令牌并保存

### 2. 配置GitHub Secrets

在你的GitHub仓库中添加以下Secrets:

- `CLOUDFLARE_API_TOKEN`: 你创建的Cloudflare API令牌
- `CLOUDFLARE_ACCOUNT_ID`: 你的Cloudflare账号ID

### 3. 启用GitHub Actions

确保仓库中的两个GitHub Actions工作流都已启用:

1. `meter_balance.yml` - 电表余额查询工作流
2. `cloudflare_deploy.yml` - Cloudflare Pages部署工作流

### 4. 初始部署

手动触发 `cloudflare_deploy.yml` 工作流进行初始部署:

1. 进入仓库的 `Actions` 标签页
2. 选择 `电表余额监控网站部署` 工作流
3. 点击 `Run workflow` 按钮
4. 等待部署完成

部署完成后，你可以在Cloudflare Pages仪表板中找到你的网站URL。

## 工作原理

1. `meter_balance.yml` 工作流每天运行，查询电表余额并保存日志
2. `cloudflare_deploy.yml` 工作流在电表余额查询完成后自动触发
3. 部署工作流从日志中提取电表余额数据
4. 使用 `update_meter_data.py` 脚本更新 `data.json` 文件
5. 将网站文件部署到Cloudflare Pages

## 自定义配置

### 修改余额警告阈值

在 `script.js` 文件中修改以下配置:

```javascript
const CONFIG = {
    // 低余额警告阈值（度）
    LOW_BALANCE_THRESHOLD: 50,
    // 中等余额警告阈值（度）
    MEDIUM_BALANCE_THRESHOLD: 100,
    // ...
};
```

### 修改网站样式

编辑 `styles.css` 文件自定义网站外观。

### 修改图表配置

在 `script.js` 文件中修改图表相关的配置和函数。

## 故障排除

### 部署失败

1. 检查Cloudflare API令牌是否有效
2. 确认Cloudflare账号ID是否正确
3. 查看GitHub Actions运行日志了解详细错误信息

### 数据不更新

1. 检查 `meter_balance.yml` 工作流是否成功运行
2. 确认日志中是否包含电表余额信息
3. 检查 `cloudflare_deploy.yml` 工作流是否被正确触发

### 网站显示错误

1. 检查浏览器控制台是否有JavaScript错误
2. 确认 `data.json` 文件格式是否正确
3. 尝试清除浏览器缓存后重新加载页面

## 技术栈

- HTML/CSS/JavaScript - 前端网站
- Chart.js - 数据可视化图表
- Python - 数据处理脚本
- GitHub Actions - 自动化工作流
- Cloudflare Pages - 网站托管

## 许可证

与主项目相同的许可证