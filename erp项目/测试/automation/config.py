"""
自动化测试配置模块
负责加载环境变量和配置参数
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 环境配置
    BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")
    ENV = os.getenv("ENV", "development")
    
    # 浏览器配置
    BROWSER = os.getenv("BROWSER", "chromium")
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
    VIEWPORT_WIDTH = int(os.getenv("VIEWPORT_WIDTH", 1920))
    VIEWPORT_HEIGHT = int(os.getenv("VIEWPORT_HEIGHT", 1080))
    DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", 30000))
    
    # 测试账号
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
    TEST_USERNAME = os.getenv("TEST_USERNAME", "test")
    TEST_PASSWORD = os.getenv("TEST_PASSWORD", "test123")
    
    # 报告配置
    REPORT_DIR = os.getenv("REPORT_DIR", "reports")
    SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "reports/screenshots")
    LOG_DIR = os.getenv("LOG_DIR", "logs")
    
    # API配置
    API_BASE_URL = f"{BASE_URL}/api"
    
    @classmethod
    def init_dirs(cls):
        """初始化必要的目录"""
        for dir_path in [cls.REPORT_DIR, cls.SCREENSHOT_DIR, cls.LOG_DIR]:
            os.makedirs(dir_path, exist_ok=True)

config = Config()
