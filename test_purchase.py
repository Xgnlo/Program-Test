"""
采购订单接口测试
"""
import pytest
import allure
import random


@allure.feature("采购管理")
@allure.story("采购订单接口")
class TestPurchase:

    @allure.title("获取采购订单列表")
    def test_get_purchase_list(self, auth_client):
        """获取采购订单列表"""
        response = auth_client.get("/purchase")
        data = auth_client.assert_success(response)
        assert isinstance(data["data"], list)

    @allure.title("创建采购订单成功")
    def test_create_purchase_success(self, auth_client, test_supplier, test_product):
        """创建采购订单成功"""
        response = auth_client.post(
            "/purchase",
            json={
                "supplier_id": test_supplier["id"],
                "product_id": test_product["id"],
                "quantity": 50,
                "price": 5.50,
                "remark": "接口测试采购订单"
            }
        )
        data = auth_client.assert_success(response)
        assert data["data"]["status"] == "pending" or data["data"]["status"] == "待审批"
        assert data["data"]["quantity"] == 50

    @allure.title("创建采购订单-数量为0")
    def test_create_purchase_zero_quantity(self, auth_client, test_supplier, test_product):
        """采购数量为0"""
        response = auth_client.post(
            "/purchase",
            json={
                "supplier_id": test_supplier["id"],
                "product_id": test_product["id"],
                "quantity": 0,
                "price": 5.50
            }
        )
        assert response.status_code == 200

    @allure.title("创建采购订单-数量为负数")
    def test_create_purchase_negative_quantity(self, auth_client, test_supplier, test_product):
        """采购数量为负数"""
        response = auth_client.post(
            "/purchase",
            json={
                "supplier_id": test_supplier["id"],
                "product_id": test_product["id"],
                "quantity": -10,
                "price": 5.50
            }
        )
        assert response.status_code == 200

    @allure.title("采购订单审批")
    def test_approve_purchase(self, auth_client, test_supplier, test_product):
        """审批采购订单"""
        # 先创建
        create_resp = auth_client.post(
            "/purchase",
            json={
                "supplier_id": test_supplier["id"],
                "product_id": test_product["id"],
                "quantity": 30,
                "price": 5.50,
                "remark": "测试审批"
            }
        )
        order_id = create_resp.json()["data"]["id"]

        # 审批
        response = auth_client.put(f"/purchase/{order_id}/approve")
        data = response.json()
        assert data.get("success") == True

    @allure.title("采购订单入库-库存增加")
    def test_purchase_stock_in(self, auth_client, test_supplier, test_product):
        """采购入库后库存增加"""
        initial_stock = test_product["stock"]

        # 创建采购单
        create_resp = auth_client.post(
            "/purchase",
            json={
                "supplier_id": test_supplier["id"],
                "product_id": test_product["id"],
                "quantity": 20,
                "price": 5.50,
                "remark": "测试入库"
            }
        )
        order_id = create_resp.json()["data"]["id"]

        # 审批
        auth_client.put(f"/purchase/{order_id}/approve")

        # 入库
        response = auth_client.put(f"/purchase/{order_id}/stock_in")
        data = response.json()
        assert data.get("success") == True

        # 验证库存增加
        product_resp = auth_client.get(f"/products/{test_product['id']}")
        new_stock = product_resp.json()["data"]["stock"]
        assert new_stock == initial_stock + 20, f"库存应该从{initial_stock}变为{initial_stock+20}，实际为{new_stock}"
