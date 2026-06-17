"""
登录功能测试用例
"""
import pytest
from pages.login_page import LoginPage
from config import config


@pytest.mark.login
@pytest.mark.smoke
class TestLogin:
    """登录测试类"""
    
    def test_login_success(self, page):
        """登录成功-有效管理员账号"""
        login_page = LoginPage(page)
        login_page.login(config.ADMIN_USERNAME, config.ADMIN_PASSWORD)
        login_page.verify_login_success()
    
    def test_login_failure_invalid_user(self, page):
        """登录失败-无效账号"""
        login_page = LoginPage(page)
        login_page.login("wrong_user", "wrong_password")
        login_page.verify_login_failure()
    
    def test_login_failure_empty_username(self, page):
        """登录失败-空用户名"""
        login_page = LoginPage(page)
        login_page.login("", "admin123")
        login_page.verify_login_failure()
    
    def test_login_failure_empty_password(self, page):
        """登录失败-空密码"""
        login_page = LoginPage(page)
        login_page.login("admin", "")
        login_page.verify_login_failure()
    
    def test_login_page_elements(self, page):
        """验证登录页面元素"""
        login_page = LoginPage(page)
        login_page.load()
        login_page.verify_page_title()
        assert login_page.is_visible("#username")
        assert login_page.is_visible("#password")
        assert login_page.is_visible("button[type='submit']")