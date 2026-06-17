"""
客户管理测试用例
"""
import pytest
from pages.customer_page import CustomerPage
from utils import generate_random_string


@pytest.mark.customer
@pytest.mark.smoke
class TestCustomer:
    """客户测试类"""
    
    def test_customer_page_load(self, logged_in_page):
        """客户页面加载"""
        customer_page = CustomerPage(logged_in_page)
        customer_page.load()
        customer_page.verify_page_title()
    
    def test_create_customer_success(self, logged_in_page, customer_data):
        """创建客户成功"""
        customer_page = CustomerPage(logged_in_page)
        customer_page.load()
        
        data = customer_data.get("valid_customer", {})
        data["name"] = f"{data.get('name', '')}_{generate_random_string()}"
        
        customer_page.create_customer(data)
        customer_page.verify_customer_created(data["name"])