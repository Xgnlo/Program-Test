"""
ERP 系统 - UI自动化测试用例
使用 requests 模拟表单提交（简化版UI测试，不依赖浏览器驱动）
适用于无 Playwright/Selenium 环境的快速验证
"""
import requests
import unittest
import random

BASE_URL = "http://127.0.0.1:5000"


class TestLoginPage(unittest.TestCase):
    """登录页面测试"""

    def test_01_login_page_status(self):
        """验证登录页面可访问"""
        resp = requests.get(BASE_URL + "/", timeout=10)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("ERP", resp.text)

    def test_02_login_success_flow(self):
        """模拟登录成功流程"""
        resp = requests.post(
            BASE_URL + "/api/login",
            json={"username": "admin", "password": "admin123"},
            timeout=10
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)

    def test_03_login_failure_flow(self):
        """模拟登录失败流程"""
        resp = requests.post(
            BASE_URL + "/api/login",
            json={"username": "wrong", "password": "wrong"},
            timeout=10
        )
        data = resp.json()
        self.assertNotEqual(data["code"], 0)


class TestDashboardPage(unittest.TestCase):
    """仪表盘页面测试"""

    def test_01_dashboard_status(self):
        """验证仪表盘页面可访问"""
        resp = requests.get(BASE_URL + "/dashboard", timeout=10)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("仪表盘", resp.text)

    def test_02_dashboard_api(self):
        """验证仪表盘数据API"""
        resp = requests.get(BASE_URL + "/api/dashboard", timeout=10)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertIn("total_suppliers", data["data"])


class TestModulePages(unittest.TestCase):
    """各模块页面测试"""

    def test_01_suppliers_page(self):
        """供应商管理页面"""
        resp = requests.get(BASE_URL + "/suppliers", timeout=10)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("供应商", resp.text)

    def test_02_customers_page(self):
        """客户管理页面"""
        resp = requests.get(BASE_URL + "/customers", timeout=10)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("客户", resp.text)

    def test_03_products_page(self):
        """商品管理页面"""
        resp = requests.get(BASE_URL + "/products", timeout=10)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("商品", resp.text)

    def test_04_purchase_page(self):
        """采购订单页面"""
        resp = requests.get(BASE_URL + "/purchase", timeout=10)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("采购", resp.text)

    def test_05_sales_page(self):
        """销售订单页面"""
        resp = requests.get(BASE_URL + "/sales", timeout=10)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("销售", resp.text)

    def test_06_inventory_page(self):
        """库存管理页面"""
        resp = requests.get(BASE_URL + "/inventory", timeout=10)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("库存", resp.text)


class TestBusinessFlow(unittest.TestCase):
    """业务流程测试"""

    def test_01_supplier_create_flow(self):
        """供应商创建流程测试"""
        # 1. 创建供应商
        resp = requests.post(
            BASE_URL + "/api/suppliers",
            json={"name": "UI测试供应商_" + str(random.randint(1000, 9999)),
                  "contact": "测试员",
                  "phone": "13800000000"},
            timeout=10
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)

        # 2. 验证供应商列表中可以查询到
        resp2 = requests.get(BASE_URL + "/api/suppliers", timeout=10)
        data2 = resp2.json()
        self.assertEqual(data2["code"], 0)
        self.assertGreaterEqual(len(data2["data"]), 1)

    def test_02_customer_create_flow(self):
        """客户创建流程测试"""
        resp = requests.post(
            BASE_URL + "/api/customers",
            json={"name": "UI测试客户_" + str(random.randint(1000, 9999)),
                  "contact": "测试员",
                  "phone": "13900000000"},
            timeout=10
        )
        data = resp.json()
        self.assertEqual(data["code"], 0)

    def test_03_purchase_workflow(self):
        """采购流程全测试：创建→审批→入库"""
        # 1. 创建采购单
        resp = requests.post(
            BASE_URL + "/api/purchase_orders",
            json={"supplier_id": 1, "product_id": 1, "quantity": 100, "price": 5.0},
            timeout=10
        )
        data = resp.json()
        self.assertEqual(data["code"], 0, "采购单创建失败: " + str(data))
        order_id = data["data"]["id"]

        # 2. 审批
        resp2 = requests.post(BASE_URL + f"/api/purchase_orders/{order_id}/approve", json={}, timeout=10)
        data2 = resp2.json()
        self.assertEqual(data2["code"], 0, "审批失败: " + str(data2))

        # 3. 入库
        resp3 = requests.post(BASE_URL + f"/api/purchase_orders/{order_id}/receive", json={}, timeout=10)
        data3 = resp3.json()
        self.assertEqual(data3["code"], 0, "入库失败: " + str(data3))


if __name__ == "__main__":
    print("=" * 60)
    print("ERP系统UI自动化测试")
    print("目标地址: " + BASE_URL)
    print("=" * 60)

    # 检查服务器
    try:
        requests.get(BASE_URL + "/", timeout=5)
        print("✓ 服务器状态: 正常")
    except:
        print("✗ 服务器不可达，请先启动 ERP 服务器")
        exit(1)

    print()
    print("-" * 60)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestLoginPage))
    suite.addTests(loader.loadTestsFromTestCase(TestDashboardPage))
    suite.addTests(loader.loadTestsFromTestCase(TestModulePages))
    suite.addTests(loader.loadTestsFromTestCase(TestBusinessFlow))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    print("=" * 60)
    print("UI测试完成")
    print(f"总数: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 60)
