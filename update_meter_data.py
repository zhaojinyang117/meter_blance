import os
import json
import sys
from datetime import datetime, timezone, timedelta
import logging

def setup_logging():
    """设置日志记录"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def get_data_file_path():
    """获取数据文件路径"""
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "data.json")

def load_existing_data(file_path):
    """加载现有数据，如果文件不存在则创建新的数据结构"""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logging.warning(f"数据文件 {file_path} 格式错误，将创建新文件")
    
    # 如果文件不存在或格式错误，返回初始数据结构
    return {
        "daily_data": []
    }

def update_data(data, balance):
    """更新数据，添加今天的余额记录"""
    # 获取北京时间
    beijing_time = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8)))
    today_date = beijing_time.strftime("%Y-%m-%d")
    
    # 检查今天是否已有记录
    for entry in data["daily_data"]:
        if entry["date"] == today_date:
            # 更新今天的记录
            entry["balance"] = float(balance)
            logging.info(f"更新今天 ({today_date}) 的记录: {balance} 度")
            return data
    
    # 如果今天没有记录，添加新记录
    new_entry = {
        "date": today_date,
        "balance": float(balance)
    }
    data["daily_data"].append(new_entry)
    logging.info(f"添加今天 ({today_date}) 的新记录: {balance} 度")
    
    return data

def save_data(data, file_path):
    """保存数据到文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"数据已保存到 {file_path}")
        return True
    except Exception as e:
        logging.error(f"保存数据时出错: {str(e)}")
        return False

def main():
    """主函数"""
    logger = setup_logging()
    logger.info("开始更新电表数据...")
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        logger.error("缺少电表余额参数")
        logger.info("用法: python update_meter_data.py <电表余额>")
        return 1
    
    # 获取电表余额
    try:
        balance = float(sys.argv[1])
        logger.info(f"获取到电表余额: {balance} 度")
    except ValueError:
        logger.error(f"无效的电表余额: {sys.argv[1]}")
        return 1
    
    # 获取数据文件路径
    data_file = get_data_file_path()
    
    # 加载现有数据
    data = load_existing_data(data_file)
    
    # 更新数据
    updated_data = update_data(data, balance)
    
    # 保存数据
    if save_data(updated_data, data_file):
        logger.info("数据更新成功")
        return 0
    else:
        logger.error("数据更新失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())