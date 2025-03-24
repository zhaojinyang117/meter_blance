from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from datetime import datetime
import os

def setup_logging():
    try:
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"当前目录: {current_dir}")  # 调试信息
        
        log_filename = os.path.join(current_dir, "meter_balance.log")
        print(f"尝试创建/访问日志文件: {log_filename}")  # 调试信息
        
        # 创建分隔符
        separator = "\n" + "="*50 + "\n" + \
                    f"开始新的查询 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" + \
                    "="*50 + "\n"
        
        # 如果日志文件不存在，创建一个新文件
        if not os.path.exists(log_filename):
            print("日志文件不存在，尝试创建新文件...")  # 调试信息
            with open(log_filename, 'w', encoding='utf-8') as f:
                f.write(f"电表查询日志文件 - 创建于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(separator)
                print("成功创建日志文件")  # 调试信息
        else:
            print("日志文件已存在，追加内容...")  # 调试信息
            with open(log_filename, 'a', encoding='utf-8') as f:
                f.write(separator)
                print("成功追加分隔符")  # 调试信息

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
        
    except Exception as e:
        print(f"设置日志时出错: {str(e)}")
        print(f"错误类型: {type(e)}")
        print(f"错误详情: {e.__dict__}")
        raise  # 重新抛出异常以便查看完整的错误堆栈

def send_alert_email(balance):
    # Gmail 邮箱配置
    sender_email = ""
    sender_password = ""  # 需要在Gmail设置中生成应用专用密码
    receiver_email = ""
    
    # 创建邮件内容
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "电表余额不足警告"
    
    body = f"警告：当前电表余额为 {balance} 度，已低于50度，请及时充值！"
    message.attach(MIMEText(body, "plain"))
    
    try:
        # 连接Gmail服务器并发送邮件
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()
        print("警告邮件发送成功！")
    except Exception as e:
        print(f"发送邮件时出错: {str(e)}")

def get_meter_balance():
    driver = None
    retry_count = 3  # 设置重试次数
    
    options = EdgeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-logging')
    options.add_argument('--disable-logging-redirect')
    options.add_argument('--single-process')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-infobars')
    
    service = EdgeService()
    
    for attempt in range(retry_count):
        try:
            print(f"尝试第 {attempt + 1} 次连接...")
            driver = webdriver.Edge(service=service, options=options)
            driver.set_page_load_timeout(300)
            driver.set_script_timeout(300)
            
            print("开始访问页面...")
            url = "https://zndk-443.webvpn.tjise.edu.cn/electricmeter/index.html#/pages/meterlist/meterquery"
            params = {
                "wechatUserOpenid": "",
                "meterId": "",
                "elemeterTypeRemark": ""
            }
            
            full_url = f"{url}?{'&'.join([f'{k}={v}' for k,v in params.items()])}"
            driver.get(full_url)
            
            print("等待页面初始加载...")
            time.sleep(15)
            
            print("等待查询按钮出现...")
            wait = WebDriverWait(driver, 30)
            query_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[1]/uni-button"))
            )
            
            print("找到查询按钮，准备点击...")
            driver.execute_script("arguments[0].click();", query_button)
            print("已点击查询按钮")
            time.sleep(8)
            
            print("尝试获取电表剩余值...")
            input_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "uni-input input.uni-input-input"))
            )
            balance = input_element.get_attribute('value')
            
            if balance:
                print(f"获取到电表剩余值: {balance}")
                # 转换余额为浮点数并检查
                balance_float = float(balance)
                if balance_float < 50:
                    print("电量低于50度，发送警告邮件...")
                    send_alert_email(balance)
                return balance
            else:
                print("未能获取到电表剩余值")
                return None
            
        except Exception as e:
            print(f"第 {attempt + 1} 次尝试失败: {str(e)}")
            if driver:
                driver.quit()
                driver = None
            if attempt < retry_count - 1:
                print("等待10秒后重试...")
                time.sleep(10)
            else:
                print("已达到最大重试次数，退出...")
                return None
            
        finally:
            if driver:
                print("关闭浏览器...")
                driver.quit()
                driver = None  # 保留这行以确保引用被清除

    return None  # 添加一个默认返回值

if __name__ == "__main__":
    try:
        logger = setup_logging()  # 首先设置日志
        logger.info("开始执行电表余额查询...")
        result = get_meter_balance()
        logger.info(f"查询完成，最终结果: {result}")
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
