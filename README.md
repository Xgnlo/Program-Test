# ERP系统接口自动化测试

基于Python + Requests + Pytest的接口自动化测试框架。

## 环境要求

- Python >= 3.8
- pytest >= 7.4.4
- requests >= 2.31.0
- python-dotenv >= 1.0.0

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置环境变量

1. 复制 `.env.example` 为 `.env`
2. 修改 `.env` 文件中的配置：

```env
API_BASE_URL=http://127.0.0.1:5000
API_ADMIN_USERNAME=your_username
API_ADMIN_PASSWORD=your_password
API_TIMEOUT=10
```

## 运行测试

```bash
# 运行所有测试
pytest

# 运行指定模块
pytest test_login.py

# 生成HTML报告
pytest --html=report.html

# 生成Allure报告
pytest --alluredir=allure-results
```

## 项目结构

```
api_test/
├── .env.example          # 环境变量模板
├── .gitignore            # Git忽略配置
├── config.py             # 配置文件（读取环境变量）
├── conftest.py           # pytest fixtures
├── requirements.txt      # 依赖列表
├── test_login.py         # 登录接口测试
├── test_supplier.py      # 供应商接口测试
├── test_product.py       # 商品接口测试
├── test_inventory.py     # 库存接口测试
├── test_purchase.py      # 采购接口测试
├── test_sales.py         # 销售接口测试
├── test_business_flow.py # 业务流程测试
└── utils/
    ├── __init__.py
    └── api_client.py     # API客户端封装
```

## 注意事项

- **敏感信息**：用户名、密码等敏感信息存储在 `.env` 文件中，该文件已加入 `.gitignore`，不会被提交到代码仓库。
- **测试数据**：测试使用临时创建的供应商和商品，测试结束后自动清理。
- **前置条件**：运行测试前需要先启动ERP系统服务（默认地址 http://127.0.0.1:5000）。