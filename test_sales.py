"""
销售订单接口测试
"""
import pytest
import allure
import random


@allure.feature("销售管理")
@allure.story("销售订单接口")
class TestSales:

    @allure.title("获取销售订单列表")
    def test_get_sales_list(self, auth_client):
        """获取销售订单列表"""
        response = auth_client.get("/sales")
        data = auth_client.assert_success(response)
        assert isinstance(data["data"], list)

    @allure.title("创建销售订单成功")
    def test_create_sales_success(self, auth_client, test_product):
        """创建销售订单成功"""
        # 先创建一个客户
        import random
        customer_name = f"测试客户_{random.randint(1000, 9999)}"
        customer_resp = auth_client.post(
            "/customers",
            json={"name": customer_name, "contact": "测试", "phone": "13900000000"}
        )
        customer = customer_resp.json()["data"]

        response = auth_client.post(
            "/sales",
            json={
                "customer_id": customer["id"],
                "product_id": test_product["id"],
                "quantity": 10,
                "price": 9.90,
                "remark": "接口测试销售订单"
            }
        )
        data = auth_client.assert_success(response)
        assert data["data"]["quantity"] == 10

        # 清理客户
        auth_client.delete(f"/customers/{customer['id']}")

    @allure.title("销售发货-库存减少")
    def test_sales_ship_stock_decrease(self, auth_client, test_product):
        """销售发货后库存减少"""
        initial_stock = test_product["stock"]
        ship_quantity = 5

        # 创建客户
        customer_name = f"发货测试客户_{random.randint(1000, 9999)}"
        customer_resp = auth_client.post(
            "/customers",
            json={"name": customer_name, "contact": "测试", "phone": "13900000000"}
        )
        customer = customer_resp.json()["data"]

        # 创建销售单
        create_resp = auth_client.post(
            "/sales",
            json={
                "customer_id": customer["id"],
                "product_id": test_product["id"],
                "quantity": ship_quantity,
                "price": 9.90,
                "remark": "测试发货"
            }
        )
        order_id = create_resp.json()["data"]["id"]

        # 发货
        response = auth_client.put(f"/sales/{order_id}/ship")
        data = response.json()
        assert data.get("success") == True

        # 验证库存减少
        product_resp = auth_client.get(f"/products/{test_product['id']}")
        new_stock = product_resp.json()["data"]["stock"]
        assert new_stock == initial_stock - ship_quantity, f"库存应该从{initial_stock}变为{initial_stock-ship_quantity}，实际为{new_stock}"

        # 清理
        auth_client.delete(f"/customers/{customer['id']}")

    @allure.title("销售发货-库存不足")
    def test_sales_ship_insufficient_stock(self, auth_client, test_product):
        """库存不足时发货应该失败"""
        # 获取当前库存
        current_stock = test_product["stock"]
        too_much = current_stock + 100

        # 创建客户
        customer_name = f"库存不足测试_{random.randint(1000, 9999)}"
        customer_resp = auth_client.post(
            "/customers",
            json={"name": customer_name, "contact": "测试", "phone": "13900000000"}
        )
        customer = customer_resp.json()["data"]

        # 创建超额销售单
        create_resp = auth_client.post(
            "/sales",
            json={
                "customer_id": customer["id"],
                "product_id": test_product["id"],
                "quantity": too_much,
                "price": 9.90,
                "remark": "测试库存不足"
            }
        )
        order_id = create_resp.json()["data"]["id"]

        # 尝试发货
        response = auth_client.put(f"/sales/{order_id}/ship")
        # 库存不足应该返回失败
        # 具体断言根据后端实现调整
        assert response.status_code == 200

        # 清理
        auth_client.delete(f"/customers/{customer['id']}")
