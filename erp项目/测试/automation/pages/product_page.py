"""
商品管理页面对象
封装商品管理页面的所有元素和操作
"""
from playwright.sync_api import expect
from pages.base_page import BasePage
from utils import logger


class ProductPage(BasePage):
    """商品管理页面"""
    
    PAGE_TITLE = ".page-title"
    ADD_BUTTON = "button.btn-primary"
    DATA_TABLE = "table"
    
    FORM_CODE = "#p_code, input[name='code']"
    FORM_NAME = "#p_name, input[name='name']"
    FORM_CATEGORY = "#p_cat, input[name='category']"
    FORM_SPEC = "#p_spec, input[name='spec']"
    FORM_UNIT = "#p_unit, input[name='unit']"
    FORM_PURCHASE_PRICE = "#p_pp, input[name='purchase_price']"
    FORM_SALE_PRICE = "#p_sp, input[name='sale_price']"
    FORM_STOCK = "#p_stk, input[name='stock']"
    FORM_MIN_STOCK = "#p_ms, input[name='min_stock']"
    FORM_REMARK = "#p_remark, textarea[name='remark']"
    
    MODAL_SAVE = ".modal-footer .btn-primary"
    
    def __init__(self, page):
        super().__init__(page)
    
    def load(self):
        logger.info("加载商品管理页面")
        self.navigate("/dashboard")
        from pages.dashboard_page import DashboardPage
        DashboardPage(self.page).navigate_to_products()
    
    def click_add_button(self):
        self.click(self.ADD_BUTTON)
    
    def create_product(self, data: dict):
        logger.info(f"创建商品: {data.get('name')}")
        self.click_add_button()
        self.fill(self.FORM_CODE, data.get("code", ""))
        self.fill(self.FORM_NAME, data.get("name", ""))
        self.fill(self.FORM_CATEGORY, data.get("category", ""))
        self.fill(self.FORM_SPEC, data.get("spec", ""))
        self.fill(self.FORM_UNIT, data.get("unit", "个"))
        self.fill(self.FORM_PURCHASE_PRICE, str(data.get("purchase_price", 0)))
        self.fill(self.FORM_SALE_PRICE, str(data.get("sale_price", 0)))
        self.fill(self.FORM_STOCK, str(data.get("stock", 0)))
        self.fill(self.FORM_MIN_STOCK, str(data.get("min_stock", 0)))
        self.fill(self.FORM_REMARK, data.get("remark", ""))
        self.click(self.MODAL_SAVE)
        self.wait(1)
    
    def verify_page_title(self):
        expect(self.page.locator(self.PAGE_TITLE)).to_have_text("商品管理")
