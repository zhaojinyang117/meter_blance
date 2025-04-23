# 电表余额查询自动化

这个项目包含两个脚本用于自动查询电表余额，当余额低于设定值时自动发送邮件提醒：

1. `meter_blance.py` - 本地运行的脚本
2. `meter_balance_action.py` - 为GitHub Actions优化的脚本

## 功能特点

- 自动登录查询电表余额
- 当余额低于50度时自动发送邮件提醒
- 支持本地运行和GitHub Actions自动运行
- 完整的日志记录和错误处理
- 无需人工干预的自动化流程
- Cloudflare Pages可视化网站展示用电数据和统计信息

## GitHub Actions 部署步骤

1. **Fork 或克隆本仓库**

2. **设置 GitHub Secrets**

   在仓库的 Settings > Secrets and variables > Actions 中添加以下 Secrets：

   - `SENDER_EMAIL`: 发送邮件的Gmail邮箱
   - `SENDER_PASSWORD`: Gmail应用密码（不是普通密码，需要在Gmail安全设置中创建）
   - `RECEIVER_EMAIL`: 接收提醒的邮箱地址
   - `METER_OPENID`: 电表查询微信OpenID
   - `METER_ID`: 电表ID
   - `METER_TYPE_REMARK`: 电表类型备注

3. **启用 GitHub Actions**

   GitHub Actions 会按照 `.github/workflows/meter_balance.yml` 文件中的设置自动运行。默认设置为每天北京时间晚上21:30运行一次。

   您也可以在仓库的 Actions 标签页中手动触发工作流运行。

## 本地运行

1. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

2. 设置环境变量或直接在脚本中配置相关参数。

3. 运行脚本：
   ```
   python meter_blance.py
   ```

## 注意事项

- 请确保Gmail账户已启用"不太安全的应用访问"或使用应用专用密码
- 首次运行脚本时请本地测试，确保所有参数正确配置
- 如果遇到 GitHub Actions 运行失败，请查看运行日志以诊断问题

## 自定义配置

您可以修改以下参数来自定义脚本行为：

- 余额阈值：默认为50度，可在脚本中修改
- 运行频率：在 `.github/workflows/meter_balance.yml` 中修改cron表达式
- 邮件内容：可在脚本的 `send_alert_email` 函数中自定义

## 脚本文件说明

- `meter_blance.py`: 原始本地运行脚本，保持不变
- `meter_balance_action.py`: 为GitHub Actions环境优化的脚本
- `requirements.txt`: 依赖项列表
- `.github/workflows/meter_balance.yml`: GitHub Actions工作流配置
- `.github/workflows/cloudflare_deploy.yml`: Cloudflare Pages部署工作流配置
- `index.html`, `styles.css`, `script.js`: Cloudflare Pages网站前端文件
- `update_meter_data.py`: 更新电表数据的脚本
- `data.json`: 存储电表余额历史数据的JSON文件
- `CLOUDFLARE_README.md`: Cloudflare Pages网站部署和使用说明

## 项目简介
这是一个自动化的电表余额查询系统，专门为天津市大学软件学院学生公寓设计。系统会自动访问学校的电表查询网页，获取电表余额，并在余额低于50度时通过Gmail发送邮件提醒。

## 功能特点
- 自动化查询电表余额
- 低于50度时自动发送Gmail邮件提醒
- 支持3次失败重试机制
- 无界面运行（Headless模式）
- 自动化错误处理和超时控制
- 详细的日志记录功能

## 环境要求
- Python 3.x
- Microsoft Edge 浏览器
- Edge WebDriver (msedgedriver)

### 必需的Python包
```bash
pip install selenium
```

## 配置说明
### 1. Gmail邮箱配置
在`send_alert_email`函数中配置以下参数：
```python
sender_email = "your_email@gmail.com"
sender_password = "your_app_password" # Gmail应用专用密码
receiver_email = "receiver@example.com"
```

### 2. 电表参数配置
在`get_meter_balance`函数中配置以下参数：
```python
params = {
    "wechatUserOpenid": "你的openid",
    "meterId": "电表ID",
    "elemeterTypeRemark": "电表类型备注"
}
```

## 使用方法
1. 克隆项目到本地
2. 安装依赖：
```bash
pip install selenium
```
3. 配置Gmail和电表参数
4. 运行脚本：
```bash
python "meter balance.py"
```

### 设置定时任务
1. 创建批处理文件 `run_meter_balance.bat`：
```batch
@echo off
cd /d "脚本所在目录路径"
python "meter balance.py"
```

2. 在Windows任务计划程序中设置定时任务：
- 打开任务计划程序（按Win+R，输入taskschd.msc）
- 创建基本任务
- 设置每天晚上21:00运行
- 选择启动程序，指向bat文件
- 配置"使用最高权限运行"

## 运行机制
1. 脚本启动后会以无界面模式打开Edge浏览器
2. 自动访问电表查询页面
3. 等待页面完全加载
4. 自动点击查询按钮
5. 获取电表余额
6. 如果余额低于50度，自动发送提醒邮件
7. 如果查询失败，最多重试3次
8. 所有操作都会记录到日志文件中

## 日志功能
- 日志文件位置：脚本所在目录下的 `meter_balance.log`
- 记录内容：
  - 程序启动时间
  - 查询过程的每个步骤
  - 查询结果
  - 错误信息（如果有）
- 每次查询都有清晰的分隔符
- 日志会持续追加，方便追踪历史记录

## 错误处理
- 网络超时：设置了60秒的页面加载超时
- 查询失败：自动等待10秒后重试，最多重试3次
- 浏览器崩溃：自动清理并重启浏览器进程
- 所有错误都会记录在日志文件中

## 安全提示
- 不要将Gmail密码直接写在代码中
- 建议使用环境变量或配置文件存储敏感信息
- 定期更新Gmail应用专用密码

## 注意事项
- 确保安装了Microsoft Edge浏览器
- 需要安装Edge WebDriver并添加到系统路径
- 需要稳定的网络连接
- Gmail账号需要开启"应用专用密码"功能
- 首次运行时需要确保所有参数配置正确

## 常见问题解决
1. 如果出现Edge WebDriver版本不匹配问题：
   - 更新Edge浏览器到最新版本
   - 下载对应版本的Edge WebDriver

2. 如果邮件发送失败：
   - 检查Gmail的应用专用密码是否正确
   - 确认Gmail账号的安全设置

3. 如果查询失败：
   - 检查网络连接
   - 验证电表参数是否正确
   - 查看日志文件了解具体错误原因

## Cloudflare Pages 可视化网站

本项目包含一个基于Cloudflare Pages的可视化网站，用于展示电表余额和用电量数据。

### 主要功能

- 实时显示当前电表余额
- 展示近7天的用电量图表
- 显示余额变化趋势
- 计算平均日用电量
- 预估剩余电量可用天数
- 详细的历史数据表格

### 部署方法

1. 在GitHub仓库中添加以下Secrets:
   - `CLOUDFLARE_API_TOKEN`: Cloudflare API令牌
   - `CLOUDFLARE_ACCOUNT_ID`: Cloudflare账号ID

2. 手动触发 `电表余额监控网站部署` 工作流进行初始部署

详细的部署和配置说明请参考 [CLOUDFLARE_README.md](CLOUDFLARE_README.md)。

### 工作原理

1. GitHub Actions每天运行电表余额查询
2. 查询完成后自动触发Cloudflare Pages部署工作流
3. 部署工作流从日志中提取电表余额数据并更新JSON文件
4. 将网站文件部署到Cloudflare Pages
5. 网站通过JavaScript从JSON文件中读取数据并生成图表和统计信息
