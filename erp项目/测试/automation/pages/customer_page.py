"""
客户管理页面对象
封装客户管理页面的所有元素和操作
"""
from playwright.sync_api import expect
from pages.base_page import BasePage
from utils import logger


class CustomerPage(BasePage):
    """客户管理页面"""
    
    PAGE_TITLE = ".page-title"
    ADD_BUTTON = "button.btn-primary"
    DATA_TABLE = "table"
    
    FORM_NAME = "#c_name, input[name='name']"
    FORM_CONTACT = "#c_contact, input[name='contact']"
    FORM_PHONE = "#c_phone, input[name='phone']"
    FORM_EMAIL = "#c_email, input[name='email']"
    FORM_ADDRESS = "#c_addr, input[name='address']"
    FORM_REMARK = "#c_remark, textarea[name='remark']"
    
    MODAL_SAVE = ".modal-footer .btn-primary"
    EDIT_BUTTON = ".btn-sm.btn-primary"
    DELETE_BUTTON = ".btn-sm.btn-danger"
    
    def __init__(self, page):
        super().__init__(page)
    
    def load(self):
        logger.info("加载客户管理页面")
        self.navigate("/dashboard")
        from pages.dashboard_page import DashboardPage
        DashboardPage(self.page).navigate_to_customers()
    
    def click_add_button(self):
        self.click(self.ADD_BUTTON)
    
    def create_customer(self, data: dict):
        logger.info(f"创建客户: {data.get('name')}")
        self.click_add_button()
        self.fill(self.FORM_NAME, data.get("name", ""))
        self.fill(self.FORM_CONTACT, data.get("contact", ""))
        self.fill(self.FORM_PHONE, data.get("phone", ""))
        self.fill(self.FORM_EMAIL, data.get("email", ""))
        self.fill(self.FORM_ADDRESS, data.get("address", ""))
        self.fill(self.FORM_REMARK, data.get("remark", ""))
        self.click(self.MODAL_SAVE)
        self.wait(1)
    
    def get_table_row_count(self) -> int:
        rows = self.page.locator(f"{self.DATA_TABLE} tbody tr")
        return rows.count()
    
    def verify_customer_created(self, name: str):
        assert self.get_table_row_count() > 0, "客户未创建成功"
        logger.info("客户创建成功")
    
    def verify_page_title(self):
        expect(self.page.locator(self.PAGE_TITLE)).to_have_text("客户管理")
