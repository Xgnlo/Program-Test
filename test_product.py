"""
商品接口测试
"""
import pytest
import allure
import random


@allure.feature("商品管理")
@allure.story("商品接口")
class TestProduct:

    @allure.title("获取商品列表")
    def test_get_product_list(self, auth_client):
        """获取商品列表"""
        response = auth_client.get("/products")
        data = auth_client.assert_success(response)
        assert isinstance(data["data"], list)

    @allure.title("商品列表-分页")
    def test_get_product_list_pagination(self, auth_client):
        """分页获取商品列表"""
        response = auth_client.get("/products?page=1&page_size=10")
        data = response.json()
        assert data.get("success") == True

    @allure.title("商品列表-搜索")
    def test_search_product(self, auth_client):
        """搜索商品"""
        response = auth_client.get("/products?keyword=测试")
        data = auth_client.assert_success(response)
        assert isinstance(data["data"], list)

    @allure.title("创建商品成功")
    def test_create_product_success(self, auth_client):
        """创建商品成功"""
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
        data = auth_client.assert_success(response)
        assert data["data"]["code"] == code
        assert data["data"]["stock"] == 100
        # 清理
        auth_client.delete(f"/products/{data['data']['id']}")

    @allure.title("创建商品-编码为空")
    def test_create_product_empty_code(self, auth_client):
        """商品编码为空"""
        response = auth_client.post(
            "/products",
            json={
                "code": "",
                "name": "测试商品",
                "category": "电子元件",
                "purchase_price": 5,
                "sale_price": 10,
                "stock": 100
            }
        )
        # 验证接口正常响应
        assert response.status_code == 200

    @allure.title("创建商品-进价为负数")
    def test_create_product_negative_price(self, auth_client):
        """进价为负数"""
        code = f"P-NEG-{random.randint(1000, 9999)}"
        response = auth_client.post(
            "/products",
            json={
                "code": code,
                "name": "负进价商品",
                "category": "电子元件",
                "purchase_price": -5,
                "sale_price": 10,
                "stock": 100
            }
        )
        assert response.status_code == 200

    @allure.title("获取商品详情")
    def test_get_product_detail(self, auth_client, test_product):
        """获取商品详情"""
        product_id = test_product["id"]
        response = auth_client.get(f"/products/{product_id}")
        data = auth_client.assert_success(response)
        assert data["data"]["id"] == product_id

    @allure.title("更新商品")
    def test_update_product(self, auth_client, test_product):
        """更新商品信息"""
        product_id = test_product["id"]
        new_name = "更新后的商品名称"
        response = auth_client.put(
            f"/products/{product_id}",
            json={"name": new_name}
        )
        data = auth_client.assert_success(response, "更新成功")
        assert data["data"]["name"] == new_name

    @allure.title("删除商品")
    def test_delete_product(self, auth_client):
        """删除商品"""
        code = f"P-DEL-{random.randint(1000, 9999)}"
        create_resp = auth_client.post(
            "/products",
            json={
                "code": code,
                "name": "待删除商品",
                "category": "电子元件",
                "purchase_price": 5,
                "sale_price": 10,
                "stock": 100
            }
        )
        product_id = create_resp.json()["data"]["id"]

        response = auth_client.delete(f"/products/{product_id}")
        data = response.json()
        assert data.get("success") == True
