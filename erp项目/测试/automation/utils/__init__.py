"""
工具函数模块
提供通用的辅助函数
"""
import os
import json
import yaml
import logging
from datetime import datetime
from config import config

# 日志配置
logger = logging.getLogger("erp_auto_test")
logger.setLevel(logging.INFO)

# 创建日志目录
os.makedirs(config.LOG_DIR, exist_ok=True)

# 文件处理器
file_handler = logging.FileHandler(
    os.path.join(config.LOG_DIR, f"test_{datetime.now().strftime('%Y%m%d')}.log"),
    encoding="utf-8"
)
file_handler.setLevel(logging.INFO)

# 控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 格式化器
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


def load_yaml(file_path: str) -> dict:
    """加载 YAML 文件"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"加载 YAML 文件失败: {file_path}, 错误: {e}")
        return {}


def save_json(data: dict, file_path: str):
    """保存数据到 JSON 文件"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"数据已保存到: {file_path}")
    except Exception as e:
        logger.error(f"保存 JSON 文件失败: {file_path}, 错误: {e}")


def generate_timestamp() -> str:
    """生成时间戳字符串"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def generate_random_string(length: int = 6) -> str:
    """生成随机字符串"""
    import random
    import string
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_number(length: int = 8) -> str:
    """生成随机数字字符串"""
    import random
    return "".join(random.choices(string.digits, k=length))


def take_screenshot(page, name: str = "screenshot") -> str:
    """
    截图并保存
    :param page: Playwright Page 对象
    :param name: 截图名称（不含扩展名）
    :return: 截图文件路径
    """
    os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)
    timestamp = generate_timestamp()
    file_path = os.path.join(config.SCREENSHOT_DIR, f"{name}_{timestamp}.png")
    try:
        page.screenshot(path=file_path, full_page=True)
        logger.info(f"截图已保存: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"截图失败: {e}")
        return ""
