"""
库存管理接口测试
"""
import pytest
import allure


@allure.feature("库存管理")
@allure.story("库存接口")
class TestInventory:

    @allure.title("获取库存列表")
    def test_get_inventory_list(self, auth_client):
        """获取库存列表"""
        response = auth_client.get("/inventory")
        data = auth_client.assert_success(response)
        assert isinstance(data["data"], list)

    @allure.title("获取库存预警列表")
    def test_get_inventory_warning(self, auth_client):
        """获取库存预警列表"""
        response = auth_client.get("/inventory/warning")
        data = auth_client.assert_success(response)
        assert isinstance(data["data"], list)

    @allure.title("库存调整")
    def test_inventory_adjust(self, auth_client, test_product):
        """调整库存"""
        new_stock = 200
        response = auth_client.put(
            f"/inventory/{test_product['id']}/adjust",
            json={"stock": new_stock, "reason": "接口测试调整"}
        )
        data = response.json()
        assert data.get("success") == True

        # 验证库存
        product_resp = auth_client.get(f"/products/{test_product['id']}")
        assert product_resp.json()["data"]["stock"] == new_stock


@allure.feature("仪表盘")
@allure.story("统计数据")
class TestDashboard:

    @allure.title("获取仪表盘统计")
    def test_get_dashboard_stats(self, auth_client):
        """获取仪表盘统计数据"""
        response = auth_client.get("/dashboard/stats")
        data = auth_client.assert_success(response)
        # 验证返回的统计数据
        assert isinstance(data["data"], dict)
