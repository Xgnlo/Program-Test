"""
商品管理测试用例
"""
import pytest
from pages.product_page import ProductPage
from utils import generate_random_string


@pytest.mark.product
@pytest.mark.smoke
class TestProduct:
    """商品测试类"""
    
    def test_product_page_load(self, logged_in_page):
        """商品页面加载"""
        product_page = ProductPage(logged_in_page)
        product_page.load()
        product_page.verify_page_title()
    
    def test_create_product_success(self, logged_in_page, product_data):
        """创建商品成功"""
        product_page = ProductPage(logged_in_page)
        product_page.load()
        
        data = product_data.get("valid_product", {})
        data["code"] = f"{data.get('code', '')}_{generate_random_string()}"
        data["name"] = f"{data.get('name', '')}_{generate_random_string()}"
        
        product_page.create_product(data)