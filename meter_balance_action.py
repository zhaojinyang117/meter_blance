from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
    NoSuchElementException,
    SessionNotCreatedException,
)
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from datetime import datetime, timezone, timedelta
import os
import sys
import traceback


def setup_logging():
    """设置日志记录"""
    try:
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"当前目录: {current_dir}")

        log_filename = os.path.join(current_dir, "meter_balance.log")
        print(f"尝试创建/访问日志文件: {log_filename}")

        # 设置基本日志配置
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler()  # GitHub Actions环境下主要使用控制台输出
            ],
        )

        # 尝试添加文件处理程序（如果可写入）
        try:
            file_handler = logging.FileHandler(log_filename, encoding="utf-8")
            logging.getLogger().addHandler(file_handler)
            print(f"成功添加日志文件处理程序: {log_filename}")
        except PermissionError:
            print(f"警告: 无法写入日志文件 {log_filename}，将只使用控制台输出")

        return logging.getLogger(__name__)

    except Exception as e:
        print(f"设置日志时出错: {str(e)}")
        print(f"错误类型: {type(e)}")
        return logging.getLogger(__name__)  # 返回一个默认的logger


def send_alert_email(balance):
    """发送电表余额不足警告邮件"""
    # 从环境变量获取邮箱配置
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")
    receiver_email = os.environ.get("RECEIVER_EMAIL")

    # 检查配置是否完整
    if not sender_email or not sender_password or not receiver_email:
        logging.warning("邮箱配置不完整，无法发送警告邮件")
        return False

    # 获取北京时间
    beijing_time = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8)))

    # 创建邮件内容
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = f"电表余额不足警告 - {beijing_time.strftime('%Y-%m-%d')}"

    body = f"""
    警告：当前电表余额为 {balance} 度，已低于50度，请及时充值！
    
    此邮件由GitHub Actions自动发送于 {beijing_time.strftime("%Y-%m-%d %H:%M:%S")} (北京时间)
    """
    message.attach(MIMEText(body, "plain"))

    try:
        # 连接Gmail服务器并发送邮件
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()
        logging.info("警告邮件发送成功！")
        return True
    except Exception as e:
        logging.error(f"发送邮件时出错: {str(e)}")
        return False


def safely_quit_driver(driver, logger):
    """安全关闭WebDriver"""
    if driver:
        try:
            logger.info("正在安全关闭浏览器...")
            driver.quit()
            logger.info("浏览器已安全关闭")
        except Exception as e:
            logger.error(f"关闭浏览器时出错: {str(e)}")
        finally:
            return None
    return None


def get_meter_balance():
    """查询电表余额"""
    driver = None
    retry_count = 3  # 设置重试次数
    logger = logging.getLogger(__name__)

    # 检查必要的环境变量
    required_vars = ["METER_OPENID", "METER_ID", "METER_TYPE_REMARK"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        logger.error(f"缺少必要的环境变量: {', '.join(missing_vars)}")
        return None

    # 配置Edge浏览器选项
    options = EdgeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-logging")
    options.add_argument("--disable-logging-redirect")
    options.add_argument("--single-process")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-infobars")
    options.add_argument("--window-size=1920,1080")  # 设置窗口大小
    options.add_argument("--start-maximized")  # 最大化窗口
    options.add_argument(
        "--disable-blink-features=AutomationControlled"
    )  # 禁用自动化标志

    # 增加稳定性参数
    options.add_argument("--disable-features=NetworkService")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-web-security")
    options.add_argument("--dns-prefetch-disable")
    options.add_argument("--disable-hang-monitor")

    # 从环境变量获取电表查询参数
    wechat_user_openid = os.environ.get("METER_OPENID")
    meter_id = os.environ.get("METER_ID")
    elemeter_type_remark = os.environ.get("METER_TYPE_REMARK")

    for attempt in range(retry_count):
        try:
            # 安全关闭之前可能存在的实例
            driver = safely_quit_driver(driver, logger)
            time.sleep(3)  # 等待之前的浏览器实例完全关闭

            logger.info(f"尝试第 {attempt + 1} 次连接...")
            service = EdgeService()
            driver = webdriver.Edge(service=service, options=options)
            driver.set_page_load_timeout(60)  # 减少超时时间，防止长时间卡住
            driver.set_script_timeout(60)

            logger.info("开始访问页面...")
            url = "https://zndk-443.webvpn.tjise.edu.cn/electricmeter/index.html#/pages/meterlist/meterquery"
            params = {
                "wechatUserOpenid": wechat_user_openid,
                "meterId": meter_id,
                "elemeterTypeRemark": elemeter_type_remark,
            }

            full_url = f"{url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"

            # 尝试多次加载页面
            page_load_attempts = 3
            page_loaded = False

            for page_attempt in range(page_load_attempts):
                try:
                    logger.info(f"第 {page_attempt + 1} 次尝试加载页面...")
                    driver.get(full_url)
                    # 检查页面是否成功加载
                    if "electricmeter" in driver.current_url:
                        page_loaded = True
                        logger.info("页面成功加载")
                        break
                except WebDriverException as e:
                    if page_attempt == page_load_attempts - 1:
                        logger.error(f"所有页面加载尝试均失败: {str(e)}")
                        raise
                    logger.warning(
                        f"页面加载失败 ({page_attempt + 1}/{page_load_attempts}): {str(e)}"
                    )
                    time.sleep(5)

            if not page_loaded:
                raise Exception("页面加载失败，URL加载不完整")

            logger.info("等待页面初始加载...")
            time.sleep(10)  # 减少等待时间，避免浏览器闲置太久自动关闭

            logger.info("等待查询按钮出现...")
            wait = WebDriverWait(driver, 20)  # 减少等待时间

            try:
                query_button = wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "/html/body/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[1]/uni-button",
                        )
                    )
                )

                logger.info("找到查询按钮，准备点击...")
                try:
                    # 使用JavaScript点击按钮
                    driver.execute_script("arguments[0].click();", query_button)
                    logger.info("使用JavaScript成功点击查询按钮")
                except Exception as js_error:
                    logger.warning(f"JavaScript点击失败: {str(js_error)}，尝试直接点击")
                    # 如果JavaScript点击失败，尝试直接点击
                    query_button.click()
                    logger.info("使用直接点击成功点击查询按钮")

                logger.info("已点击查询按钮，等待数据加载...")
                time.sleep(5)  # 减少等待时间

                logger.info("尝试获取电表剩余值...")
                input_element = wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "uni-input input.uni-input-input")
                    )
                )

                balance = input_element.get_attribute("value")

                if balance:
                    logger.info(f"获取到电表剩余值: {balance}")
                    # 转换余额为浮点数并检查
                    balance_float = float(balance)
                    if balance_float < 50:  # 设置为50度阈值
                        logger.warning(f"电量低于50度 ({balance})，发送警告邮件...")
                        send_alert_email(balance)
                    return balance
                else:
                    logger.warning("输入元素存在但未能获取到电表余额值")
                    raise Exception("电表余额获取失败：输入框值为空")

            except (TimeoutException, NoSuchElementException) as e:
                logger.error(f"查找元素超时或元素不存在: {str(e)}")
                # 尝试截图保存错误状态
                try:
                    screenshot_path = os.path.join(
                        os.path.dirname(os.path.abspath(__file__)),
                        f"error_screenshot_{attempt}.png",
                    )
                    driver.save_screenshot(screenshot_path)
                    logger.info(f"已保存错误截图: {screenshot_path}")
                except Exception as ss_error:
                    logger.warning(f"保存截图失败: {str(ss_error)}")
                raise Exception(f"查找元素失败: {str(e)}")

        except Exception as e:
            logger.error(f"第 {attempt + 1} 次尝试失败: {str(e)}")
            logger.error(f"错误详情: {traceback.format_exc()}")

            # 安全关闭当前driver实例
            driver = safely_quit_driver(driver, logger)

            if attempt < retry_count - 1:
                logger.info("等待10秒后重试...")
                time.sleep(10)
            else:
                logger.error("已达到最大重试次数，退出...")
                return None

    return None


def main():
    """主函数"""
    try:
        # 设置日志
        logger = setup_logging()
        logger.info("=== GitHub Actions 电表余额查询脚本开始执行 ===")

        # 获取北京时间（UTC+8）
        beijing_time = datetime.now(timezone.utc).astimezone(
            timezone(timedelta(hours=8))
        )
        logger.info(f"执行时间(北京): {beijing_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # 检查必要的环境变量
        required_env_vars = [
            "METER_OPENID",
            "METER_ID",
            "METER_TYPE_REMARK",
            "SENDER_EMAIL",
            "SENDER_PASSWORD",
            "RECEIVER_EMAIL",
        ]

        missing_vars = []
        for var in required_env_vars:
            if not os.environ.get(var):
                missing_vars.append(var)

        if missing_vars:
            logger.error(f"缺少必要的环境变量: {', '.join(missing_vars)}")
            logger.error("请确保在GitHub Secrets中设置了上述环境变量")
            return 1

        # 查询电表余额
        logger.info("开始执行电表余额查询...")
        result = get_meter_balance()

        if result:
            logger.info(f"查询完成，电表余额: {result}度")
            # 将结果写入GitHub Actions输出
            print(f"::set-output name=balance::{result}")
            # 添加一个特殊格式的日志，方便后续提取
            logger.info(f"===METER_BALANCE_RESULT===电表余额: {result}度===")
            
            # 更新data.json文件
            try:
                logger.info("开始更新电表数据文件...")
                import subprocess
                
                # 调用update_meter_data.py脚本更新数据
                update_cmd = [sys.executable, "update_meter_data.py", result]
                logger.info(f"执行命令: {' '.join(update_cmd)}")
                
                # 运行更新脚本
                process = subprocess.run(
                    update_cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # 记录脚本输出
                if process.stdout:
                    logger.info(f"更新脚本输出: {process.stdout}")
                
                logger.info("电表数据文件更新成功")
            except subprocess.CalledProcessError as e:
                logger.error(f"更新电表数据文件失败: {str(e)}")
                logger.error(f"脚本错误输出: {e.stderr}")
                # 即使更新失败，也不影响整体流程
            except Exception as e:
                logger.error(f"更新电表数据文件时发生错误: {str(e)}")
                # 即使更新失败，也不影响整体流程
            
            return 0
        else:
            logger.error("查询失败，未能获取电表余额")
            return 1

    except Exception as e:
        print(f"程序执行出错: {str(e)}")
        print(f"错误详情: {traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
