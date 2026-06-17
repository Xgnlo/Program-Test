"""
供应商管理测试用例
"""
import pytest
from pages.supplier_page import SupplierPage
from utils import generate_random_string


@pytest.mark.supplier
@pytest.mark.smoke
class TestSupplier:
    """供应商测试类"""
    
    def test_supplier_page_load(self, logged_in_page):
        """供应商页面加载"""
        supplier_page = SupplierPage(logged_in_page)
        supplier_page.load()
        supplier_page.verify_page_title()
    
    def test_create_supplier_success(self, logged_in_page, supplier_data):
        """创建供应商成功"""
        supplier_page = SupplierPage(logged_in_page)
        supplier_page.load()
        
        # 使用测试数据 + 随机后缀避免重复
        data = supplier_data.get("valid_supplier", {})
        data["name"] = f"{data.get('name', '')}_{generate_random_string()}"
        
        supplier_page.create_supplier(data)
        supplier_page.verify_supplier_created(data["name"])
    
    def test_create_supplier_minimal(self, logged_in_page, supplier_data):
        """创建供应商-仅必填字段"""
        supplier_page = SupplierPage(logged_in_page)
        supplier_page.load()
        
        data = supplier_data.get("minimal_supplier", {})
        data["name"] = f"{data.get('name', '')}_{generate_random_string()}"
        
        supplier_page.create_supplier(data)
        supplier_page.verify_supplier_created(data["name"])
    
    def test_supplier_search(self, logged_in_page):
        """供应商搜索功能"""
        supplier_page = SupplierPage(logged_in_page)
        supplier_page.load()
        supplier_page.search_supplier("测试")