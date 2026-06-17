"""
ERP 系统 - 接口自动化测试用例
测试范围：登录、用户、供应商、客户、商品、采购、销售、库存
"""
import requests
import json
import time
import random
import unittest

BASE_URL = "http://127.0.0.1:5000"
API_BASE_URL = BASE_URL + "/api"

TEST_DATA = {
    "login": {"username": "admin", "password": "admin123"},
    "supplier": {"name": "", "contact": "测试员", "phone": "13800138000", "email": "test@test.com"},
    "customer": {"name": "", "contact": "客户联系人", "phone": "13900139000", "email": "customer@test.com", "level": "一般", "credit_limit": 5000},
    "product": {"code": "", "name": "", "spec": "标准规格", "category": "测试分类", "unit": "个", "purchase_price": 5.5, "sale_price": 9.9, "stock": 100, "min_stock": 10, "max_stock": 10000},
    "purchase": {"supplier_id": 1, "product_id": 1, "quantity": 50, "price": 5.5},
    "sales": {"customer_id": 1, "product_id": 1, "quantity": 5, "price": 9.9},
}


def api_get(path):
    return requests.get(API_BASE_URL + path, timeout=30)


def api_post(path, data):
    return requests.post(API_BASE_URL + path, json=data, timeout=30)


def api_put(path, data):
    return requests.put(API_BASE_URL + path, json=data, timeout=30)


def api_delete(path):
    return requests.delete(API_BASE_URL + path, timeout=30)


class TestLogin(unittest.TestCase):
    """登录接口测试"""

    def test_login_success(self):
        resp = api_post("/login", TEST_DATA["login"])
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertIsNotNone(data["data"])

    def test_login_wrong_password(self):
        resp = api_post("/login", {"username": "admin", "password": "wrong"})
        data = resp.json()
        self.assertNotEqual(data["code"], 0)

    def test_login_empty_username(self):
        resp = api_post("/login", {"username": "", "password": "admin123"})
        data = resp.json()
        self.assertNotEqual(data["code"], 0)

    def test_login_empty_password(self):
        resp = api_post("/login", {"username": "admin", "password": ""})
        data = resp.json()
        self.assertNotEqual(data["code"], 0)


class TestUser(unittest.TestCase):
    """用户管理接口测试"""

    @classmethod
    def setUpClass(cls):
        cls.test_user_code = str(random.randint(1000, 9999))

    def test_01_get_users(self):
        resp = api_get("/users")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertIsInstance(data["data"], list)

    def test_02_create_user(self):
        payload = {
            "username": "testuser_" + self.test_user_code,
            "password": "123456",
            "real_name": "测试用户",
            "role": "user",
            "department": "测试部"
        }
        resp = api_post("/users", payload)
        data = resp.json()
        self.assertEqual(data["code"], 0, msg="创建用户失败: " + str(data))

    def test_03_create_duplicate_user(self):
        payload = {
            "username": "admin",
            "password": "123456",
            "real_name": "重复用户"
        }
        resp = api_post("/users", payload)
        data = resp.json()
        self.assertNotEqual(data["code"], 0, msg="重复用户名应返回错误")


class TestSupplier(unittest.TestCase):
    """供应商管理接口测试"""

    def test_01_get_suppliers(self):
        resp = api_get("/suppliers")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertIsInstance(data["data"], list)

    def test_02_create_supplier(self):
        payload = {
            "name": "测试供应商_" + str(random.randint(1000, 9999)),
            "contact": "张三",
            "phone": "13800138000",
            "email": "supplier@test.com",
            "address": "深圳测试路1号",
            "level": "A",
            "remark": "测试创建"
        }
        resp = api_post("/suppliers", payload)
        data = resp.json()
        self.assertEqual(data["code"], 0, msg="创建供应商失败: " + str(data))
        self.__class__.new_supplier_id = data["data"]["id"]

    def test_03_create_supplier_empty_name(self):
        resp = api_post("/suppliers", {"name": "", "contact": "测试"})
        data = resp.json()
        self.assertNotEqual(data["code"], 0, msg="空名称应返回错误")


class TestCustomer(unittest.TestCase):
    """客户管理接口测试"""

    def test_01_get_customers(self):
        resp = api_get("/customers")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertIsInstance(data["data"], list)

    def test_02_create_customer(self):
        payload = {
            "name": "测试客户_" + str(random.randint(1000, 9999)),
            "contact": "李四",
            "phone": "13900139000",
            "email": "customer@test.com",
            "address": "北京测试路1号",
            "level": "一般",
            "credit_limit": 10000
        }
        resp = api_post("/customers", payload)
        data = resp.json()
        self.assertEqual(data["code"], 0, msg="创建客户失败: " + str(data))


class TestProduct(unittest.TestCase):
    """商品管理接口测试"""

    def test_01_get_products(self):
        resp = api_get("/products")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)

    def test_02_create_product(self):
        payload = {
            "code": "SKU-T" + str(random.randint(10000, 99999)),
            "name": "测试商品_" + str(random.randint(1000, 9999)),
            "spec": "标准规格",
            "category": "测试分类",
            "unit": "个",
            "purchase_price": 5.5,
            "sale_price": 9.9,
            "stock": 500,
            "min_stock": 50,
            "max_stock": 5000
        }
        resp = api_post("/products", payload)
        data = resp.json()
        self.assertEqual(data["code"], 0, msg="创建商品失败: " + str(data))

    def test_03_create_product_empty(self):
        resp = api_post("/products", {"name": "", "code": ""})
        data = resp.json()
        self.assertNotEqual(data["code"], 0)


class TestPurchaseOrder(unittest.TestCase):
    """采购订单接口测试"""

    def test_01_get_purchase_orders(self):
        resp = api_get("/purchase_orders")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)

    def test_02_create_purchase_order(self):
        resp = api_post("/purchase_orders", {
            "supplier_id": 1,
            "product_id": 1,
            "quantity": 100,
            "price": 5.5,
            "remark": "测试采购单"
        })
        data = resp.json()
        self.assertEqual(data["code"], 0, msg="创建采购单失败: " + str(data))
        self.__class__.new_order_id = data["data"]["id"]

    def test_03_approve_purchase_order(self):
        if not hasattr(self, 'new_order_id'):
            self.skipTest("需先成功创建采购单")
        resp = api_post("/purchase_orders/" + str(self.new_order_id) + "/approve", {})
        data = resp.json()
        self.assertEqual(data["code"], 0, msg="审批失败: " + str(data))

    def test_04_receive_purchase_order(self):
        if not hasattr(self, 'new_order_id'):
            self.skipTest("需先成功创建采购单")
        resp = api_post("/purchase_orders/" + str(self.new_order_id) + "/receive", {})
        data = resp.json()
        self.assertEqual(data["code"], 0, msg="入库失败: " + str(data))


class TestSalesOrder(unittest.TestCase):
    """销售订单接口测试"""

    def test_01_get_sales_orders(self):
        resp = api_get("/sales_orders")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)

    def test_02_create_sales_order(self):
        resp = api_post("/sales_orders", {
            "customer_id": 1,
            "product_id": 1,
            "quantity": 10,
            "price": 9.9,
            "remark": "测试销售单"
        })
        data = resp.json()
        self.assertEqual(data["code"], 0, msg="创建销售单失败: " + str(data))
        self.__class__.new_sales_id = data["data"]["id"]

    def test_03_ship_sales_order(self):
        if not hasattr(self, 'new_sales_id'):
            self.skipTest("需先成功创建销售单")
        resp = api_post("/sales_orders/" + str(self.new_sales_id) + "/ship", {})
        data = resp.json()
        self.assertEqual(data["code"], 0, msg="发货失败: " + str(data))


class TestInventory(unittest.TestCase):
    """库存管理接口测试"""

    def test_01_inventory_summary(self):
        resp = api_get("/inventory/summary")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertIsInstance(data["data"], list)

    def test_02_inventory_records(self):
        resp = api_get("/inventory_records")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)


class TestDashboard(unittest.TestCase):
    """仪表盘接口测试"""

    def test_01_dashboard(self):
        resp = api_get("/dashboard")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertIn("total_suppliers", data["data"])
        self.assertIn("total_customers", data["data"])
        self.assertIn("total_products", data["data"])


if __name__ == "__main__":
    print("=" * 60)
    print("ERP系统接口自动化测试")
    print("目标地址: " + BASE_URL)
    print("=" * 60)
    print("")

    # 检查服务器是否可用
    try:
        resp = requests.get(BASE_URL + "/", timeout=5)
        print("✓ 服务器状态: 正常")
    except:
        print("✗ 服务器不可达，请先启动 ERP 服务器")
        print("  启动方式: cd 平台 && python app.py")
        exit(1)

    print("")
    print("-" * 60)
    # 使用 unittest 运行测试
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestLogin))
    suite.addTests(loader.loadTestsFromTestCase(TestUser))
    suite.addTests(loader.loadTestsFromTestCase(TestSupplier))
    suite.addTests(loader.loadTestsFromTestCase(TestCustomer))
    suite.addTests(loader.loadTestsFromTestCase(TestProduct))
    suite.addTests(loader.loadTestsFromTestCase(TestPurchaseOrder))
    suite.addTests(loader.loadTestsFromTestCase(TestSalesOrder))
    suite.addTests(loader.loadTestsFromTestCase(TestInventory))
    suite.addTests(loader.loadTestsFromTestCase(TestDashboard))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("")
    print("=" * 60)
    print("测试完成")
    print(f"总数: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 60)
