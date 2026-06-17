"""
仪表盘页面对象
封装仪表盘页面的所有元素和操作
"""
from playwright.sync_api import expect
from pages.base_page import BasePage
from utils import logger


class DashboardPage(BasePage):
    """仪表盘页面"""
    
    # 元素定位器
    SIDEBAR_LINKS = ".sidebar a"
    USER_INFO = "#userInfo"
    LOGOUT_BUTTON = ".btn-outline-secondary"
    STAT_CARDS = ".stat-card"
    MAIN_CONTENT = "#mainContent"
    
    # 侧边栏菜单项
    MENU_DASHBOARD = "a[data-page='dashboard']"
    MENU_USERS = "a[data-page='users']"
    MENU_SUPPLIERS = "a[data-page='suppliers']"
    MENU_CUSTOMERS = "a[data-page='customers']"
    MENU_PRODUCTS = "a[data-page='products']"
    MENU_PURCHASE = "a[data-page='purchase']"
    MENU_SALES = "a[data-page='sales']"
    MENU_INVENTORY = "a[data-page='inventory']"
    
    def __init__(self, page):
        super().__init__(page)
    
    def load(self):
        """加载仪表盘页面"""
        logger.info("加载仪表盘页面")
        self.navigate("/dashboard")
    
    def get_user_info(self) -> str:
        """获取用户信息"""
        return self.get_text(self.USER_INFO)
    
    def click_logout(self):
        """点击退出按钮"""
        self.click(self.LOGOUT_BUTTON)
    
    def verify_logout(self):
        """验证退出成功（跳转到登录页）"""
        self.wait_for_url_contains("login")
        logger.info("退出成功")
    
    def click_menu_item(self, item_selector: str):
        """点击侧边栏菜单项"""
        logger.info(f"点击菜单项: {item_selector}")
        self.click(item_selector)
    
    def navigate_to_users(self):
        """导航到用户管理"""
        self.click_menu_item(self.MENU_USERS)
    
    def navigate_to_suppliers(self):
        """导航到供应商管理"""
        self.click_menu_item(self.MENU_SUPPLIERS)
    
    def navigate_to_customers(self):
        """导航到客户管理"""
        self.click_menu_item(self.MENU_CUSTOMERS)
    
    def navigate_to_products(self):
        """导航到商品管理"""
        self.click_menu_item(self.MENU_PRODUCTS)
    
    def navigate_to_purchase(self):
        """导航到采购订单"""
        self.click_menu_item(self.MENU_PURCHASE)
    
    def navigate_to_sales(self):
        """导航到销售订单"""
        self.click_menu_item(self.MENU_SALES)
    
    def navigate_to_inventory(self):
        """导航到库存管理"""
        self.click_menu_item(self.MENU_INVENTORY)
    
    def verify_stat_cards(self):
        """验证统计卡片存在"""
        expect(self.page.locator(self.STAT_CARDS)).to_have_count(8)
        logger.info("统计卡片验证通过")
    
    def get_stat_value(self, index: int) -> str:
        """获取第N个统计卡片的值"""
        return self.get_text(f"{self.STAT_CARDS}:nth-child({index}) .num")
    
    def verify_page_title(self):
        """验证页面标题"""
        expect(self.page).to_have_title("明远电子科技 ERP 管理系统")
