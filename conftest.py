"""
pytest 配置文件
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ADMIN_USERNAME, ADMIN_PASSWORD
from utils.api_client import APIClient


@pytest.fixture(scope="session")
def api_client():
    """未登录的API客户端"""
    client = APIClient()
    yield client


@pytest.fixture(scope="session")
def auth_client():
    """已登录的API客户端（管理员）"""
    client = APIClient()
    user_data = client.login(ADMIN_USERNAME, ADMIN_PASSWORD)
    assert user_data is not None, "登录失败，请检查服务是否启动"
    yield client


@pytest.fixture(scope="function")
def test_supplier(auth_client):
    """创建测试供应商，测试结束后删除"""
    import random
    name = f"接口测试供应商_{random.randint(1000, 9999)}"
    response = auth_client.post(
        "/suppliers",
        json={
            "name": name,
            "contact": "测试联系人",
            "phone": "13800000000",
            "email": "test@example.com",
            "address": "测试地址",
            "remark": "接口测试创建"
        }
    )
    data = response.json()
    supplier = data["data"]
    yield supplier
    # 清理
    try:
        auth_client.delete(f"/suppliers/{supplier['id']}")
    except:
        pass


@pytest.fixture(scope="function")
def test_product(auth_client):
    """创建测试商品，测试结束后删除"""
    import random
    code = f"P-API-{random.randint(1000, 9999)}"
    response = auth_client.post(
        "/products",
        json={
            "code": code,
            "name": "接口测试商品",
            "category": "电子元件",
            "spec": "标准规格",
            "unit": "个",
            "purchase_price": 5.50,
            "sale_price": 9.90,
            "stock": 100,
            "min_stock": 10,
            "remark": "接口测试创建"
        }
    )
    data = response.json()
    product = data["data"]
    yield product
    # 清理
    try:
        auth_client.delete(f"/products/{product['id']}")
    except:
        pass
