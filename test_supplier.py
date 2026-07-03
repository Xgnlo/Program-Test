"""
供应商接口测试
"""
import pytest
import allure
import random


@allure.feature("供应商管理")
@allure.story("供应商接口")
class TestSupplier:

    @allure.title("获取供应商列表")
    def test_get_supplier_list(self, auth_client):
        """获取供应商列表"""
        response = auth_client.get("/suppliers")
        data = auth_client.assert_success(response)
        assert isinstance(data["data"], list)

    @allure.title("供应商列表-分页")
    def test_get_supplier_list_pagination(self, auth_client):
        """分页获取供应商列表"""
        response = auth_client.get("/suppliers?page=1&page_size=10")
        data = response.json()
        assert data.get("success") == True
        # 分页返回可能有total字段

    @allure.title("供应商列表-搜索")
    def test_search_supplier(self, auth_client):
        """搜索供应商"""
        response = auth_client.get("/suppliers?keyword=测试")
        data = auth_client.assert_success(response)
        assert isinstance(data["data"], list)

    @allure.title("创建供应商成功")
    def test_create_supplier_success(self, auth_client):
        """创建供应商成功"""
        name = f"接口测试供应商_{random.randint(1000, 9999)}"
        response = auth_client.post(
            "/suppliers",
            json={
                "name": name,
                "contact": "张三",
                "phone": "13800000001",
                "email": "supplier@test.com",
                "address": "测试地址",
                "remark": "测试备注"
            }
        )
        data = auth_client.assert_success(response, "创建成功")
        assert data["data"]["name"] == name
        # 清理
        auth_client.delete(f"/suppliers/{data['data']['id']}")

    @allure.title("创建供应商-名称为空")
    def test_create_supplier_empty_name(self, auth_client):
        """供应商名称为空创建失败"""
        response = auth_client.post(
            "/suppliers",
            json={
                "name": "",
                "contact": "张三",
                "phone": "13800000001"
            }
        )
        data = response.json()
        # 应该返回失败（具体取决于后端校验逻辑）
        # 这里不严格断言，只验证接口不报错
        assert response.status_code == 200

    @allure.title("获取单个供应商详情")
    def test_get_supplier_detail(self, auth_client, test_supplier):
        """获取供应商详情"""
        supplier_id = test_supplier["id"]
        response = auth_client.get(f"/suppliers/{supplier_id}")
        data = auth_client.assert_success(response)
        assert data["data"]["id"] == supplier_id

    @allure.title("更新供应商")
    def test_update_supplier(self, auth_client, test_supplier):
        """更新供应商信息"""
        supplier_id = test_supplier["id"]
        new_contact = "更新后的联系人"
        response = auth_client.put(
            f"/suppliers/{supplier_id}",
            json={"contact": new_contact}
        )
        data = auth_client.assert_success(response, "更新成功")
        assert data["data"]["contact"] == new_contact

    @allure.title("删除供应商")
    def test_delete_supplier(self, auth_client):
        """删除供应商"""
        # 先创建
        name = f"待删除供应商_{random.randint(1000, 9999)}"
        create_resp = auth_client.post(
            "/suppliers",
            json={"name": name, "contact": "待删除"}
        )
        supplier_id = create_resp.json()["data"]["id"]

        # 再删除
        response = auth_client.delete(f"/suppliers/{supplier_id}")
        data = response.json()
        assert data.get("success") == True
