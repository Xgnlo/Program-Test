"""
登录页面对象
封装登录页面的所有元素和操作
"""
from playwright.sync_api import expect
from pages.base_page import BasePage
from utils import logger


class LoginPage(BasePage):
    """登录页面"""
    
    # 元素定位器
    USERNAME_INPUT = "#username"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "button[type='submit']"
    ERROR_MESSAGE = ".alert-danger, .error"
    SUCCESS_MESSAGE = ".alert-success"
    
    def __init__(self, page):
        super().__init__(page)
    
    def load(self):
        """加载登录页面"""
        logger.info("加载登录页面")
        self.navigate("/")
    
    def enter_username(self, username: str):
        """输入用户名"""
        self.fill(self.USERNAME_INPUT, username)
    
    def enter_password(self, password: str):
        """输入密码"""
        self.fill(self.PASSWORD_INPUT, password)
    
    def click_login(self):
        """点击登录按钮"""
        self.click(self.LOGIN_BUTTON)
    
    def login(self, username: str, password: str):
        """执行完整登录流程"""
        logger.info(f"执行登录: {username}")
        self.load()
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()
    
    def verify_login_success(self):
        """验证登录成功（URL 包含 dashboard）"""
        self.wait_for_url_contains("dashboard")
        logger.info("登录成功")
    
    def verify_login_failure(self):
        """验证登录失败（停留在登录页或出现错误提示）"""
        try:
            self.wait_for_visible(self.ERROR_MESSAGE)
            logger.info("登录失败 - 出现错误提示")
        except Exception:
            # 检查是否仍在登录页
            current_url = self.get_url()
            assert "login" in current_url.lower(), f"预期停留在登录页，实际 URL: {current_url}"
            logger.info("登录失败 - 停留在登录页")
    
    def get_error_message(self) -> str:
        """获取错误提示信息"""
        if self.is_visible(self.ERROR_MESSAGE):
            return self.get_text(self.ERROR_MESSAGE)
        return ""
    
    def verify_page_title(self):
        """验证页面标题"""
        expect(self.page).to_have_title("明远电子科技 ERP 管理系统")
    
    def clear_fields(self):
        """清空输入框"""
        self.fill(self.USERNAME_INPUT, "")
        self.fill(self.PASSWORD_INPUT, "")
