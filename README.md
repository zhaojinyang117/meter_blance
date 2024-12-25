# meter_blance
天津市大学软件学院电表余额查询警报
# 天津市大学软件学院电表余额查询系统

## 项目简介
这是一个自动化的电表余额查询系统，专门为天津市大学软件学院院学生公寓设计。系统会自动访问学校的电表查询网页，获取电表余额，并在余额低于2度时通过Gmail发送邮件提醒。

## 功能特点
- 自动化查询电表余额
- 低于2度时自动发送Gmail邮件提醒
- 支持3次失败重试机制
- 无界面运行（Headless模式）
- 自动化错误处理和超时控制

## 环境要求
- Python 3.x
- Chrome浏览器
- ChromeDriver

### 必需的Python包
```
bash
pip install selenium
```

## 配置说明
### 1. Gmail邮箱配置
在`send_alert_email`函数中配置以下参数：
```
python
sender_email = "your_email@gmail.com"
sender_password = "your_app_password" # Gmail应用专用密码
receiver_email = "receiver@example.com"
```

### 2. 电表参数配置
在`get_meter_balance`函数中配置以下参数：
```
python
params = {
"wechatUserOpenid": "你的openid",
"meterId": "电表ID",
"elemeterTypeRemark": "电表类型备注"
}
```

## 使用方法
1. 克隆项目到本地
2. 安装依赖：
```
bash
pip install selenium
```

3. 配置Gmail和电表参数
4. 运行脚本：

```
python3 meter balance.py
```

## 运行机制
1. 脚本启动后会以无界面模式打开Chrome
2. 自动访问电表查询页面
3. 等待15秒让页面完全加载
4. 自动点击查询按钮
5. 获取电表余额
6. 如果余额低于2度，自动发送提醒邮件
7. 如果查询失败，最多重试3次

## 错误处理
- 网络超时：设置了300秒的页面加载超时
- 查询失败：自动等待10秒后重试，最多重试3次
- 浏览器崩溃：自动清理并重启浏览器进程

## 安全提示
- 不要将Gmail密码直接写在代码中
- 建议使用环境变量或配置文件存储敏感信息
- 定期更新Gmail应用专用密码

## 注意事项
- 确保Chrome浏览器版本与ChromeDriver版本匹配
- 需要稳定的网络连接
- Gmail账号需要开启"应用专用密码"功能
- 首次运行时需要确保所有参数配置正确

## 常见问题解决
1. 如果出现ChromeDriver版本不匹配问题：
   - 更新Chrome浏览器到最新版本
   - 下载对应版本的ChromeDriver

2. 如果邮件发送失败：
   - 检查Gmail的应用专用密码是否正确
   - 确认Gmail账号的安全设置

3. 如果查询失败：
   - 检查网络连接
   - 验证电表参数是否正确
