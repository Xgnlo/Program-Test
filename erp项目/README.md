# 明远电子科技 ERP 管理系统 - 软件测试项目

## 🎯 项目概述

| 项目 | 内容 |
|------|------|
| **项目名称** | 明远电子科技 ERP 管理系统 |
| **项目类型** | 企业级管理信息系统（采购/销售/库存/客户/供应商管理） |
| **被测系统** | Flask (Python) + SQLite + RESTful API |
| **测试类型** | 功能测试、接口测试、UI自动化测试 |
| **测试框架** | Python unittest + requests + Playwright |
| **测试用例** | 接口测试 25条 + UI测试 14条 = 39条 |
| **测试通过率** | 100% |

---

## 📂 项目目录结构

```
erp项目/
│
├── 平台/                              # ERP被测系统
│   ├── app.py                        # Flask主程序 (核心)
│   ├── models.py                     # 数据库模型
│   ├── requirements.txt              # 依赖清单
│   ├── templates/                    # HTML页面模板
│   │   ├── index.html                # 登录页
│   │   ├── dashboard.html            # 仪表盘
│   │   ├── users.html                # 用户管理
│   │   ├── suppliers.html            # 供应商管理
│   │   ├── customers.html            # 客户管理
│   │   ├── products.html             # 商品管理
│   │   ├── purchase.html             # 采购订单
│   │   ├── sales.html                # 销售订单
│   │   └── inventory.html            # 库存管理
│   ├── static/css/style.css          # 前端样式
│   └── static/js/main.js             # 前端逻辑
│
├── 测试/                              # 测试工程
│   ├── api_test_cases.py             # 接口自动化测试 (25用例)
│   ├── ui_test_cases.py              # UI自动化测试 (14用例)
│   ├── 项目测试总结.md                # 完整测试报告
│   └── automation/                    # Playwright + POM高级自动化
│       ├── pages/                    # 页面对象
│       ├── tests/                    # 测试脚本
│       ├── data/test_data.yaml       # 测试数据
│       └── run_tests.bat             # 一键执行
│
└── README.md                         # 本文档
```

---

## 🚀 快速开始

### 1. 启动 ERP 服务器
```bash
cd 平台
pip install -r requirements.txt
python app.py
```
服务器启动后访问: http://127.0.0.1:5000

### 2. 登录系统
```
用户名: admin       密码: admin123
用户名: manager     密码: manager123
用户名: test        密码: test123
```

### 3. 运行接口自动化测试
```bash
cd 测试
python api_test_cases.py
# 预期输出: Ran 25 tests in 0.888s OK
```

### 4. 运行UI自动化测试
```bash
cd 测试
python ui_test_cases.py
# 预期输出: Ran 14 tests in 0.425s OK
```

### 5. 运行 Playwright 完整UI自动化
```bash
cd 测试/automation
pytest tests/ -v --html=reports/report.html
# 这会启动真实浏览器执行完整UI测试
```

---

## ✅ 测试结果摘要

### 接口自动化测试
```
测试工具:   Python unittest + requests
用例数量:   25条
执行时长:   0.888s
通过率:     100%
覆盖模块:   登录/用户/供应商/客户/商品/采购/销售/库存/仪表盘
测试结果:   PASSED 25, FAILED 0, ERROR 0
```

### UI自动化测试
```
测试工具:   Python unittest + requests (页面层)
用例数量:   14条
执行时长:   0.425s
通过率:     100%
覆盖模块:   登录页/仪表盘/所有业务模块页面
测试结果:   PASSED 14, FAILED 0, ERROR 0
```

### 模块覆盖率
| 模块 | 覆盖情况 | 核心功能 |
|------|---------|---------|
| 用户管理 | ✅ | 创建/查询/重复校验 |
| 供应商管理 | ✅ | 创建/查询/空值校验 |
| 客户管理 | ✅ | 创建/查询 |
| 商品管理 | ✅ | 创建/编码唯一性 |
| 采购订单 | ✅ | 创建/审批/入库流程 |
| 销售订单 | ✅ | 创建/发货流程 |
| 库存管理 | ✅ | 汇总/出入库记录 |
| 仪表盘 | ✅ | 统计数据验证 |

---

## 📊 核心业务流程说明

### 1. 采购流程
```
创建采购单 → 经理审批 → 供应商发货 → 仓库入库
   ↓           ↓           ↓           ↓
POST/orders → POST/approve → POST/receive → 库存自动+
```
### 2. 销售流程
```
创建销售单 → 确认订单 → 仓库发货 → 库存扣减
   ↓           ↓           ↓           ↓
POST/orders → (状态) → POST/ship → 库存自动-
```
### 3. 库存管理
```
实时库存查询:   GET /api/inventory/summary
出入库记录:     GET /api/inventory_records
库存预警:       低于安全库存自动预警
```

---

## 🔍 核心测试用例示例

### 接口测试示例（采购全流程）
```python
# 1. 创建采购单
resp = requests.post(API + "/purchase_orders", json={
    "supplier_id": 1, "product_id": 1,
    "quantity": 100, "price": 5.0
})
self.assertEqual(resp.json()["code"], 0)
order_id = resp.json()["data"]["id"]

# 2. 审批
resp = requests.post(API + f"/purchase_orders/{order_id}/approve", json={})
self.assertEqual(resp.json()["code"], 0)

# 3. 入库
resp = requests.post(API + f"/purchase_orders/{order_id}/receive", json={})
self.assertEqual(resp.json()["code"], 0)
# 预期: 商品库存数量增加
```

### UI测试示例（页面访问）
```python
# 验证仪表盘可访问
resp = requests.get(BASE_URL + "/dashboard")
self.assertEqual(resp.status_code, 200)
self.assertIn("仪表盘", resp.text)
# 预期: HTTP 200，页面包含"仪表盘"关键字
```

---

## 🎓 项目特点与亮点

### 1. 测试体系完整
✅ **三层测试覆盖**：功能测试 + 接口测试 + UI自动化测试  
✅ **业务流程覆盖**：采购/销售全链路，库存自动联动  
✅ **异常场景覆盖**：空值/重复值/边界值验证

### 2. 工程化实现
✅ **可维护代码结构**：按模块分 TestCase 类  
✅ **清晰命名规范**：test_xxx / 操作_xxx / 验证_yyy  
✅ **统一断言模式**：HTTP状态码 + 业务返回码 + 关键字段  
✅ **数据隔离策略**：使用随机数避免测试数据干扰

### 3. 业务价值突出
✅ **真实业务场景**：电子元器件经销企业的完整业务流程  
✅ **8大核心模块**：覆盖企业日常运营核心功能  
✅ **100%通过率**：接口测试25条、UI测试14条全部通过  
✅ **快速执行**：两套测试合计仅需约1.3秒

### 4. 技术栈规范
- **前端**: HTML5 + CSS3 + JavaScript + Bootstrap
- **后端**: Python Flask
- **数据库**: SQLite (SQLAlchemy ORM)
- **接口**: RESTful API + JSON
- **测试**: unittest + requests + Playwright

---

## 📝 主要API接口清单

| 接口 | 方法 | 功能 | 测试状态 |
|------|------|------|---------|
| /api/login | POST | 用户登录 | ✅ |
| /api/users | GET/POST | 用户管理 | ✅ |
| /api/suppliers | GET/POST | 供应商管理 | ✅ |
| /api/customers | GET/POST | 客户管理 | ✅ |
| /api/products | GET/POST | 商品管理 | ✅ |
| /api/purchase_orders | GET/POST | 采购订单 | ✅ |
| /api/purchase_orders/{id}/approve | POST | 审批 | ✅ |
| /api/purchase_orders/{id}/receive | POST | 入库 | ✅ |
| /api/sales_orders | GET/POST | 销售订单 | ✅ |
| /api/sales_orders/{id}/ship | POST | 发货 | ✅ |
| /api/inventory/summary | GET | 库存汇总 | ✅ |
| /api/dashboard | GET | 仪表盘统计 | ✅ |

---

## 📖 文档索引

| 文档 | 路径 | 说明 |
|------|------|------|
| 项目测试总结 | 测试/项目测试总结.md | 完整测试报告与细节 |
| 业务背景 | 平台/业务背景.md | ERP系统业务背景与设计 |
| 测试业务价值 | 测试/测试业务价值.md | 测试用例业务价值说明 |
| 自动化项目说明 | 测试/自动化项目总结.md | Playwright自动化工程说明 |
| 项目README | README.md | 项目整体说明（本文档） |

---

## 🎯 项目价值

### 作为测试项目的价值
1. **展示能力**：展现完整的软件测试设计与执行能力
2. **真实场景**：完整的企业级业务系统，非玩具项目
3. **代码质量**：规范的测试代码结构，可直接用于学习或复用
4. **面试素材**：完整的39条用例 + 详细业务流程
5. **可执行证明**：运行即出结果，便于现场演示

### 可扩展方向
- 添加性能测试 (Locust/压测脚本)
- 添加安全测试 (SQL注入/XSS扫描)
- 接入CI/CD (GitHub Actions)
- 添加测试数据管理 (Excel/CSV导入)
- 添加可视化测试报告 (HTML报告生成)

---

## ⚠️ 注意事项

1. **首次启动**：首次运行 app.py 会自动初始化数据库并创建测试账号
2. **依赖安装**：运行前请确保已执行 `pip install -r requirements.txt`
3. **端口占用**：默认使用 5000 端口，如被占用请修改 app.py 中的端口
4. **测试执行**：执行测试前需先启动 ERP 服务器，否则测试会因无法连接而失败

---

## 📞 联系方式

- **项目归属**: 软件测试项目作品集
- **技术栈**: Python + Flask + SQLite + unittest + requests
- **适用场景**: 软件测试工程师项目展示、测试自动化学习
- **运行环境**: Windows/Linux/Mac，Python 3.9+

---

**版本**: v1.0  
**更新**: 2024年6月
