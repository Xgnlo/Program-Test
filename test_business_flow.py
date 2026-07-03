"""
业务流程测试 - 端到端场景
"""
import pytest
import allure
import random


@allure.feature("业务流程")
@allure.story("采购入库-销售发货全流程")
class TestBusinessFlow:

    @allure.title("完整业务流程：采购入库→销售发货→库存一致")
    def test_full_business_flow(self, auth_client):
        """
        端到端测试：
        1. 创建供应商
        2. 创建商品（初始库存100）
        3. 创建采购订单（采购50个）
        4. 审批采购单
        5. 采购入库（库存变为150）
        6. 创建客户
        7. 创建销售订单（销售30个）
        8. 销售发货（库存变为120）
        9. 验证最终库存
        """
        # ========== 1. 创建供应商 ==========
        supplier_name = f"流程测试供应商_{random.randint(1000, 9999)}"
        supplier_resp = auth_client.post(
            "/suppliers",
            json={"name": supplier_name, "contact": "流程测试", "phone": "13800000000"}
        )
        supplier = supplier_resp.json()["data"]

        # ========== 2. 创建商品 ==========
        product_code = f"FLOW-{random.randint(1000, 9999)}"
        initial_stock = 100
        product_resp = auth_client.post(
            "/products",
            json={
                "code": product_code,
                "name": "流程测试商品",
                "category": "电子元件",
                "spec": "标准",
                "unit": "个",
                "purchase_price": 5.0,
                "sale_price": 10.0,
                "stock": initial_stock,
                "min_stock": 10
            }
        )
        product = product_resp.json()["data"]
        assert product["stock"] == initial_stock

        # ========== 3. 创建采购订单 ==========
        purchase_qty = 50
        purchase_resp = auth_client.post(
            "/purchase",
            json={
                "supplier_id": supplier["id"],
                "product_id": product["id"],
                "quantity": purchase_qty,
                "price": 5.0,
                "remark": "流程测试采购"
            }
        )
        purchase_order = purchase_resp.json()["data"]

        # ========== 4. 审批采购单 ==========
        approve_resp = auth_client.put(f"/purchase/{purchase_order['id']}/approve")
        assert approve_resp.json().get("success") == True

        # ========== 5. 采购入库 ==========
        stock_in_resp = auth_client.put(f"/purchase/{purchase_order['id']}/stock_in")
        assert stock_in_resp.json().get("success") == True

        # 验证库存增加
        product_resp = auth_client.get(f"/products/{product['id']}")
        stock_after_purchase = product_resp.json()["data"]["stock"]
        expected_stock = initial_stock + purchase_qty
        assert stock_after_purchase == expected_stock, f"采购入库后库存应为{expected_stock}，实际为{stock_after_purchase}"

        # ========== 6. 创建客户 ==========
        customer_name = f"流程测试客户_{random.randint(1000, 9999)}"
        customer_resp = auth_client.post(
            "/customers",
            json={"name": customer_name, "contact": "流程测试", "phone": "13900000000"}
        )
        customer = customer_resp.json()["data"]

        # ========== 7. 创建销售订单 ==========
        sales_qty = 30
        sales_resp = auth_client.post(
            "/sales",
            json={
                "customer_id": customer["id"],
                "product_id": product["id"],
                "quantity": sales_qty,
                "price": 10.0,
                "remark": "流程测试销售"
            }
        )
        sales_order = sales_resp.json()["data"]

        # ========== 8. 销售发货 ==========
        ship_resp = auth_client.put(f"/sales/{sales_order['id']}/ship")
        assert ship_resp.json().get("success") == True

        # ========== 9. 验证最终库存 ==========
        final_product_resp = auth_client.get(f"/products/{product['id']}")
        final_stock = final_product_resp.json()["data"]["stock"]
        expected_final_stock = expected_stock - sales_qty
        assert final_stock == expected_final_stock, f"销售发货后库存应为{expected_final_stock}，实际为{final_stock}"

        # ========== 清理数据 ==========
        auth_client.delete(f"/customers/{customer['id']}")
        auth_client.delete(f"/products/{product['id']}")
        auth_client.delete(f"/suppliers/{supplier['id']}")

    @allure.title("状态流转测试：采购单完整生命周期")
    def test_purchase_status_flow(self, auth_client, test_supplier, test_product):
        """
        测试采购单状态流转：
        待审批 → 已审批 → 已入库
        """
        # 创建
        create_resp = auth_client.post(
            "/purchase",
            json={
                "supplier_id": test_supplier["id"],
                "product_id": test_product["id"],
                "quantity": 10,
                "price": 5.0,
                "remark": "状态流转测试"
            }
        )
        order = create_resp.json()["data"]
        order_id = order["id"]

        # 初始状态：待审批
        assert order["status"] in ["pending", "待审批"], f"初始状态应该是待审批，实际为{order['status']}"

        # 审批
        auth_client.put(f"/purchase/{order_id}/approve")
        detail_resp = auth_client.get(f"/purchase/{order_id}")
        order_after_approve = detail_resp.json()["data"]
        assert order_after_approve["status"] in ["approved", "已审批"], f"审批后状态应该是已审批，实际为{order_after_approve['status']}"

        # 入库
        auth_client.put(f"/purchase/{order_id}/stock_in")
        final_resp = auth_client.get(f"/purchase/{order_id}")
        order_final = final_resp.json()["data"]
        assert order_final["status"] in ["stocked", "已入库"], f"入库后状态应该是已入库，实际为{order_final['status']}"
