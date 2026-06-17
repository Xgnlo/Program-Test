"""
供应商管理页面对象
封装供应商管理页面的所有元素和操作
"""
from playwright.sync_api import expect
from pages.base_page import BasePage
from utils import logger


class SupplierPage(BasePage):
    """供应商管理页面"""
    
    # 元素定位器
    PAGE_TITLE = ".page-title"
    ADD_BUTTON = "button.btn-primary"
    DATA_TABLE = "table"
    SEARCH_INPUT = "#searchInput, input[name='keyword']"
    SEARCH_BUTTON = "#btnSearch, button.btn-search"
    
    # 弹窗相关
    MODAL = ".modal"
    MODAL_TITLE = ".modal-title"
    MODAL_CLOSE = ".btn-close"
    MODAL_SAVE = ".modal-footer .btn-primary"
    MODAL_CANCEL = ".modal-footer .btn-secondary"
    
    # 表单字段
    FORM_NAME = "#s_name, input[name='name']"
    FORM_CONTACT = "#s_contact, input[name='contact']"
    FORM_PHONE = "#s_phone, input[name='phone']"
    FORM_EMAIL = "#s_email, input[name='email']"
    FORM_ADDRESS = "#s_addr, input[name='address']"
    FORM_REMARK = "#s_remark, textarea[name='remark']"
    
    # 操作按钮
    EDIT_BUTTON = ".btn-sm.btn-primary"
    DELETE_BUTTON = ".btn-sm.btn-danger"
    
    def __init__(self, page):
        super().__init__(page)
    
    def load(self):
        """加载供应商管理页面"""
        logger.info("加载供应商管理页面")
        self.navigate("/dashboard")
        from pages.dashboard_page import DashboardPage
        DashboardPage(self.page).navigate_to_suppliers()
    
    def click_add_button(self):
        """点击新增按钮"""
        self.click(self.ADD_BUTTON)
    
    def fill_name(self, name: str):
        """填充名称"""
        self.fill(self.FORM_NAME, name)
    
    def fill_contact(self, contact: str):
        """填充联系人"""
        self.fill(self.FORM_CONTACT, contact)
    
    def fill_phone(self, phone: str):
        """填充电话"""
        self.fill(self.FORM_PHONE, phone)
    
    def fill_email(self, email: str):
        """填充邮箱"""
        self.fill(self.FORM_EMAIL, email)
    
    def fill_address(self, address: str):
        """填充地址"""
        self.fill(self.FORM_ADDRESS, address)
    
    def fill_remark(self, remark: str):
        """填充备注"""
        self.fill(self.FORM_REMARK, remark)
    
    def click_save(self):
        """点击保存按钮"""
        self.click(self.MODAL_SAVE)
    
    def click_cancel(self):
        """点击取消按钮"""
        self.click(self.MODAL_CANCEL)
    
    def click_close_modal(self):
        """关闭弹窗"""
        self.click(self.MODAL_CLOSE)
    
    def create_supplier(self, data: dict):
        """创建供应商"""
        logger.info(f"创建供应商: {data.get('name')}")
        self.click_add_button()
        self.fill_name(data.get("name", ""))
        self.fill_contact(data.get("contact", ""))
        self.fill_phone(data.get("phone", ""))
        self.fill_email(data.get("email", ""))
        self.fill_address(data.get("address", ""))
        self.fill_remark(data.get("remark", ""))
        self.click_save()
        self.wait(1)
    
    def search_supplier(self, keyword: str):
        """搜索供应商"""
        logger.info(f"搜索供应商: {keyword}")
        if self.is_visible(self.SEARCH_INPUT):
            self.fill(self.SEARCH_INPUT, keyword)
            if self.is_visible(self.SEARCH_BUTTON):
                self.click(self.SEARCH_BUTTON)
            else:
                self.press_key("Enter")
            self.wait(1)
    
    def get_table_row_count(self) -> int:
        """获取表格行数"""
        rows = self.page.locator(f"{self.DATA_TABLE} tbody tr")
        return rows.count()
    
    def click_first_edit_button(self):
        """点击第一条记录的编辑按钮"""
        buttons = self.page.locator(self.EDIT_BUTTON)
        if buttons.count() > 0:
            buttons.first.click()
            self.wait(0.5)
    
    def click_first_delete_button(self):
        """点击第一条记录的删除按钮"""
        buttons = self.page.locator(self.DELETE_BUTTON)
        if buttons.count() > 0:
            buttons.first.click()
            self.wait(0.5)
    
    def confirm_delete(self):
        """确认删除（处理弹窗）"""
        self.page.on("dialog", lambda dialog: dialog.accept())
    
    def verify_supplier_created(self, name: str):
        """验证供应商创建成功"""
        self.search_supplier(name)
        row_count = self.get_table_row_count()
        assert row_count > 0, "供应商未创建成功"
        logger.info(f"供应商创建成功，当前记录数: {row_count}")
    
    def verify_page_title(self):
        """验证页面标题"""
        expect(self.page.locator(self.PAGE_TITLE)).to_have_text("供应商管理")
