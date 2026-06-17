"""
基础页面类
封装所有页面通用的操作方法
"""
from playwright.sync_api import Page, expect
from config import config
from utils import logger, take_screenshot


class BasePage:
    """基础页面类"""
    
    def __init__(self, page: Page):
        self.page = page
        self.base_url = config.BASE_URL
        self.default_timeout = config.DEFAULT_TIMEOUT
    
    def navigate(self, url: str):
        """导航到指定 URL"""
        full_url = f"{self.base_url}{url}" if not url.startswith("http") else url
        logger.info(f"导航到: {full_url}")
        self.page.goto(full_url, timeout=self.default_timeout)
    
    def wait_for_page_load(self):
        """等待页面加载完成"""
        self.page.wait_for_load_state("networkidle", timeout=self.default_timeout)
    
    def click(self, selector: str, timeout: int = None):
        """点击元素"""
        timeout = timeout or self.default_timeout
        logger.info(f"点击元素: {selector}")
        self.page.click(selector, timeout=timeout)
    
    def fill(self, selector: str, value: str, timeout: int = None):
        """填充输入框"""
        timeout = timeout or self.default_timeout
        logger.info(f"填充元素 {selector}: {value}")
        self.page.fill(selector, value, timeout=timeout)
    
    def type(self, selector: str, value: str, timeout: int = None):
        """输入文本（逐字符输入）"""
        timeout = timeout or self.default_timeout
        logger.info(f"输入文本 {selector}: {value}")
        self.page.type(selector, value, timeout=timeout)
    
    def get_text(self, selector: str, timeout: int = None) -> str:
        """获取元素文本"""
        timeout = timeout or self.default_timeout
        return self.page.locator(selector).text_content(timeout=timeout)
    
    def get_value(self, selector: str, timeout: int = None) -> str:
        """获取输入框的值"""
        timeout = timeout or self.default_timeout
        return self.page.locator(selector).input_value(timeout=timeout)
    
    def select_option(self, selector: str, value: str, timeout: int = None):
        """选择下拉框选项"""
        timeout = timeout or self.default_timeout
        logger.info(f"选择下拉框 {selector}: {value}")
        self.page.select_option(selector, value, timeout=timeout)
    
    def check(self, selector: str, timeout: int = None):
        """勾选复选框"""
        timeout = timeout or self.default_timeout
        logger.info(f"勾选复选框: {selector}")
        self.page.check(selector, timeout=timeout)
    
    def uncheck(self, selector: str, timeout: int = None):
        """取消勾选复选框"""
        timeout = timeout or self.default_timeout
        logger.info(f"取消勾选复选框: {selector}")
        self.page.uncheck(selector, timeout=timeout)
    
    def wait_for_visible(self, selector: str, timeout: int = None):
        """等待元素可见"""
        timeout = timeout or self.default_timeout
        logger.info(f"等待元素可见: {selector}")
        expect(self.page.locator(selector)).to_be_visible(timeout=timeout)
    
    def wait_for_hidden(self, selector: str, timeout: int = None):
        """等待元素隐藏"""
        timeout = timeout or self.default_timeout
        expect(self.page.locator(selector)).to_be_hidden(timeout=timeout)
    
    def wait_for_enabled(self, selector: str, timeout: int = None):
        """等待元素可点击"""
        timeout = timeout or self.default_timeout
        expect(self.page.locator(selector)).to_be_enabled(timeout=timeout)
    
    def wait_for_text(self, selector: str, text: str, timeout: int = None):
        """等待元素包含指定文本"""
        timeout = timeout or self.default_timeout
        expect(self.page.locator(selector)).to_have_text(text, timeout=timeout)
    
    def wait_for_url_contains(self, text: str, timeout: int = None):
        """等待 URL 包含指定文本"""
        timeout = timeout or self.default_timeout
        expect(self.page).to_have_url(lambda url: text in url, timeout=timeout)
    
    def wait_for_url(self, url: str, timeout: int = None):
        """等待 URL 匹配"""
        timeout = timeout or self.default_timeout
        expect(self.page).to_have_url(url, timeout=timeout)
    
    def press_key(self, key: str):
        """按键操作"""
        logger.info(f"按键: {key}")
        self.page.keyboard.press(key)
    
    def get_title(self) -> str:
        """获取页面标题"""
        return self.page.title()
    
    def get_url(self) -> str:
        """获取当前 URL"""
        return self.page.url
    
    def scroll_to(self, selector: str, timeout: int = None):
        """滚动到指定元素"""
        timeout = timeout or self.default_timeout
        self.page.locator(selector).scroll_into_view_if_needed(timeout=timeout)
    
    def screenshot(self, name: str = "screenshot") -> str:
        """截图"""
        return take_screenshot(self.page, name)
    
    def execute_script(self, script: str, *args):
        """执行 JavaScript"""
        logger.info(f"执行脚本: {script[:50]}...")
        return self.page.evaluate(script, *args)
    
    def get_attribute(self, selector: str, attribute: str, timeout: int = None) -> str:
        """获取元素属性"""
        timeout = timeout or self.default_timeout
        return self.page.locator(selector).get_attribute(attribute, timeout=timeout)
    
    def is_visible(self, selector: str) -> bool:
        """检查元素是否可见"""
        try:
            self.page.locator(selector).wait_for(state="visible", timeout=3000)
            return True
        except Exception:
            return False
    
    def is_enabled(self, selector: str) -> bool:
        """检查元素是否可点击"""
        try:
            self.page.locator(selector).wait_for(state="enabled", timeout=3000)
            return True
        except Exception:
            return False
    
    def switch_to_frame(self, selector: str):
        """切换到 iframe"""
        self.page.frame_locator(selector)
    
    def accept_alert(self):
        """接受弹窗"""
        self.page.on("dialog", lambda dialog: dialog.accept())
    
    def dismiss_alert(self):
        """取消弹窗"""
        self.page.on("dialog", lambda dialog: dialog.dismiss())
    
    def wait(self, seconds: float):
        """等待指定秒数"""
        self.page.wait_for_timeout(seconds * 1000)
