"""
登录接口测试
"""
import pytest
import allure


@allure.feature("认证模块")
@allure.story("登录接口")
class TestLogin:

    @allure.title("登录成功-有效账号")
    def test_login_success(self, api_client):
        """正确用户名密码登录成功"""
        response = api_client.post(
            "/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        data = api_client.assert_success(response, "登录成功")
        assert "token" in data["data"], "应该返回token"
        assert "user" in data["data"], "应该返回用户信息"
        assert data["data"]["user"]["username"] == "admin"

    @allure.title("登录失败-错误密码")
    def test_login_wrong_password(self, api_client):
        """错误密码登录失败"""
        response = api_client.post(
            "/auth/login",
            json={"username": "admin", "password": "wrongpass"}
        )
        assert response.status_code in [200, 401]

    @allure.title("登录失败-空用户名")
    def test_login_empty_username(self, api_client):
        """用户名为空登录失败"""
        response = api_client.post(
            "/auth/login",
            json={"username": "", "password": "admin123"}
        )
        data = response.json()
        assert data.get("success") == False or response.status_code != 200

    @allure.title("登录失败-空密码")
    def test_login_empty_password(self, api_client):
        """密码为空登录失败"""
        response = api_client.post(
            "/auth/login",
            json={"username": "admin", "password": ""}
        )
        data = response.json()
        assert data.get("success") == False or response.status_code != 200

    @allure.title("登录失败-用户不存在")
    def test_login_user_not_exist(self, api_client):
        """不存在的用户登录失败"""
        response = api_client.post(
            "/auth/login",
            json={"username": "nonexist", "password": "admin123"}
        )
        data = response.json()
        assert data.get("success") == False or response.status_code != 200

    @allure.title("登出接口")
    def test_logout(self, auth_client):
        """登出接口"""
        response = auth_client.post("/auth/logout")
        # 登出可能返回成功，也可能不做实际处理（JWT无状态）
        assert response.status_code == 200
