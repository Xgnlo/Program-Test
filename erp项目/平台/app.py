"""
明远电子科技 ERP 管理系统 - 主入口
Flask Web 应用 + RESTful API
"""
import os
import random
from datetime import datetime, date
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, User, Supplier, Customer, Product, PurchaseOrder, SalesOrder, InventoryRecord

# 初始化 Flask 应用
app = Flask(__name__)

# 配置数据库 - 使用 SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'erp.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mingyuan-erp-secret-key-2024'
app.config['JWT_SECRET_KEY'] = 'mingyuan-jwt-secret-2024'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # 24小时过期

# 初始化扩展
db.init_app(app)
CORS(app)
jwt = JWTManager(app)


def generate_order_no(prefix):
    """生成订单号：前缀 + 日期 + 4位随机数"""
    today = datetime.now().strftime('%Y%m%d')
    rand = str(random.randint(1000, 9999))
    return f"{prefix}-{today}-{rand}"


def success_response(data=None, msg='操作成功'):
    """统一成功响应格式"""
    return jsonify({'code': 0, 'msg': msg, 'data': data})


def error_response(msg='操作失败', code=1):
    """统一错误响应格式"""
    return jsonify({'code': code, 'msg': msg, 'data': None})


def get_form_value(key, default=''):
    """获取请求参数，优先从JSON读取，其次从表单"""
    data = request.get_json(silent=True)
    if data and key in data:
        return data[key]
    return request.form.get(key, default)


# ============================================================
# 页面路由
# ============================================================
@app.route('/')
def index():
    """登录页"""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """主页面"""
    return render_template('dashboard.html')


@app.route('/users')
def users_page():
    """用户管理页"""
    return render_template('users.html')


@app.route('/suppliers')
def suppliers_page():
    """供应商管理页"""
    return render_template('suppliers.html')


@app.route('/customers')
def customers_page():
    """客户管理页"""
    return render_template('customers.html')


@app.route('/products')
def products_page():
    """商品管理页"""
    return render_template('products.html')


@app.route('/purchase')
def purchase_page():
    """采购订单页"""
    return render_template('purchase.html')


@app.route('/sales')
def sales_page():
    """销售订单页"""
    return render_template('sales.html')


@app.route('/inventory')
def inventory_page():
    """库存管理页"""
    return render_template('inventory.html')


# ============================================================
# 认证接口
# ============================================================
@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json(silent=True)
    username = data.get('username') if data else request.form.get('username')
    password = data.get('password') if data else request.form.get('password')

    # 基础校验
    if not username or not password:
        return error_response('用户名和密码不能为空')

    # 查询用户
    user = User.query.filter_by(username=username).first()
    if not user:
        return error_response('用户不存在')

    if user.status != 1:
        return error_response('账号已禁用')

    if not user.check_password(password):
        return error_response('密码错误')

    # 生成 token
    token = create_access_token(identity=str(user.id))
    return success_response({
        'token': token,
        'user': user.to_dict()
    }, '登录成功')


@app.route('/api/logout', methods=['POST'])
def logout():
    """用户退出"""
    session.clear()
    return success_response(msg='退出成功')


# ============================================================
# 用户管理 API
# ============================================================
@app.route('/api/users', methods=['GET'])
def get_users():
    """获取用户列表"""
    users = User.query.order_by(User.id.asc()).all()
    return success_response([u.to_dict() for u in users])


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取单个用户"""
    user = User.query.get(user_id)
    if not user:
        return error_response('用户不存在')
    return success_response(user.to_dict())


@app.route('/api/users', methods=['POST'])
def create_user():
    """创建用户"""
    data = request.get_json(silent=True) or request.form
    username = data.get('username', '').strip()
    password = data.get('password', '123456')

    if not username:
        return error_response('用户名不能为空')

    # 检查是否已存在
    if User.query.filter_by(username=username).first():
        return error_response('用户名已存在')

    user = User(
        username=username,
        real_name=data.get('real_name', username),
        role=data.get('role', 'user'),
        department=data.get('department', ''),
        phone=data.get('phone', ''),
        email=data.get('email', ''),
        status=int(data.get('status', 1))
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return success_response(user.to_dict(), '用户创建成功')


@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """更新用户"""
    user = User.query.get(user_id)
    if not user:
        return error_response('用户不存在')

    data = request.get_json(silent=True) or request.form
    user.real_name = data.get('real_name', user.real_name)
    user.role = data.get('role', user.role)
    user.department = data.get('department', user.department)
    user.phone = data.get('phone', user.phone)
    user.email = data.get('email', user.email)
    user.status = int(data.get('status', user.status))

    # 可选更新密码
    new_password = data.get('password')
    if new_password:
        user.set_password(new_password)

    db.session.commit()
    return success_response(user.to_dict(), '用户更新成功')


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户"""
    user = User.query.get(user_id)
    if not user:
        return error_response('用户不存在')
    db.session.delete(user)
    db.session.commit()
    return success_response(msg='删除成功')


# ============================================================
# 供应商管理 API
# ============================================================
@app.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    """获取供应商列表"""
    keyword = request.args.get('keyword', '').strip()
    query = Supplier.query
    if keyword:
        query = query.filter(Supplier.name.contains(keyword))
    suppliers = query.order_by(Supplier.id.asc()).all()
    return success_response([s.to_dict() for s in suppliers])


@app.route('/api/suppliers/<int:supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    """获取单个供应商"""
    s = Supplier.query.get(supplier_id)
    if not s:
        return error_response('供应商不存在')
    return success_response(s.to_dict())


@app.route('/api/suppliers', methods=['POST'])
def create_supplier():
    """创建供应商"""
    data = request.get_json(silent=True) or request.form
    name = data.get('name', '').strip()
    if not name:
        return error_response('供应商名称不能为空')

    supplier = Supplier(
        name=name,
        contact=data.get('contact', ''),
        phone=data.get('phone', ''),
        email=data.get('email', ''),
        address=data.get('address', ''),
        level=data.get('level', 'C'),
        remark=data.get('remark', '')
    )
    db.session.add(supplier)
    db.session.commit()
    return success_response(supplier.to_dict(), '供应商创建成功')


@app.route('/api/suppliers/<int:supplier_id>', methods=['PUT'])
def update_supplier(supplier_id):
    """更新供应商"""
    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        return error_response('供应商不存在')

    data = request.get_json(silent=True) or request.form
    supplier.name = data.get('name', supplier.name)
    supplier.contact = data.get('contact', supplier.contact)
    supplier.phone = data.get('phone', supplier.phone)
    supplier.email = data.get('email', supplier.email)
    supplier.address = data.get('address', supplier.address)
    supplier.level = data.get('level', supplier.level)
    supplier.remark = data.get('remark', supplier.remark)

    db.session.commit()
    return success_response(supplier.to_dict(), '供应商更新成功')


@app.route('/api/suppliers/<int:supplier_id>', methods=['DELETE'])
def delete_supplier(supplier_id):
    """删除供应商"""
    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        return error_response('供应商不存在')
    db.session.delete(supplier)
    db.session.commit()
    return success_response(msg='供应商删除成功')


# ============================================================
# 客户管理 API
# ============================================================
@app.route('/api/customers', methods=['GET'])
def get_customers():
    """获取客户列表"""
    keyword = request.args.get('keyword', '').strip()
    query = Customer.query
    if keyword:
        query = query.filter(Customer.name.contains(keyword))
    customers = query.order_by(Customer.id.asc()).all()
    return success_response([c.to_dict() for c in customers])


@app.route('/api/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """获取单个客户"""
    c = Customer.query.get(customer_id)
    if not c:
        return error_response('客户不存在')
    return success_response(c.to_dict())


@app.route('/api/customers', methods=['POST'])
def create_customer():
    """创建客户"""
    data = request.get_json(silent=True) or request.form
    name = data.get('name', '').strip()
    if not name:
        return error_response('客户名称不能为空')

    customer = Customer(
        name=name,
        contact=data.get('contact', ''),
        phone=data.get('phone', ''),
        email=data.get('email', ''),
        address=data.get('address', ''),
        level=data.get('level', '一般'),
        credit_limit=float(data.get('credit_limit', 10000)),
        remark=data.get('remark', '')
    )
    db.session.add(customer)
    db.session.commit()
    return success_response(customer.to_dict(), '客户创建成功')


@app.route('/api/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """更新客户"""
    customer = Customer.query.get(customer_id)
    if not customer:
        return error_response('客户不存在')

    data = request.get_json(silent=True) or request.form
    customer.name = data.get('name', customer.name)
    customer.contact = data.get('contact', customer.contact)
    customer.phone = data.get('phone', customer.phone)
    customer.email = data.get('email', customer.email)
    customer.address = data.get('address', customer.address)
    customer.level = data.get('level', customer.level)
    customer.credit_limit = float(data.get('credit_limit', customer.credit_limit))
    customer.remark = data.get('remark', customer.remark)

    db.session.commit()
    return success_response(customer.to_dict(), '客户更新成功')


@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """删除客户"""
    customer = Customer.query.get(customer_id)
    if not customer:
        return error_response('客户不存在')
    db.session.delete(customer)
    db.session.commit()
    return success_response(msg='客户删除成功')


# ============================================================
# 商品管理 API
# ============================================================
@app.route('/api/products', methods=['GET'])
def get_products():
    """获取商品列表"""
    keyword = request.args.get('keyword', '').strip()
    query = Product.query
    if keyword:
        query = query.filter((Product.name.contains(keyword)) | (Product.code.contains(keyword)))
    products = query.order_by(Product.id.asc()).all()
    return success_response([p.to_dict() for p in products])


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """获取单个商品"""
    p = Product.query.get(product_id)
    if not p:
        return error_response('商品不存在')
    return success_response(p.to_dict())


@app.route('/api/products', methods=['POST'])
def create_product():
    """创建商品"""
    data = request.get_json(silent=True) or request.form
    name = data.get('name', '').strip()
    code = data.get('code', '').strip()

    if not name or not code:
        return error_response('商品名称和编码不能为空')

    # 检查编码是否重复
    if Product.query.filter_by(code=code).first():
        return error_response('商品编码已存在')

    product = Product(
        code=code,
        name=name,
        spec=data.get('spec', ''),
        category=data.get('category', ''),
        unit=data.get('unit', '个'),
        purchase_price=float(data.get('purchase_price', 0)),
        sale_price=float(data.get('sale_price', 0)),
        stock=float(data.get('stock', 0)),
        min_stock=float(data.get('min_stock', 0)),
        max_stock=float(data.get('max_stock', 10000)),
        remark=data.get('remark', '')
    )
    db.session.add(product)
    db.session.commit()
    return success_response(product.to_dict(), '商品创建成功')


@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """更新商品"""
    product = Product.query.get(product_id)
    if not product:
        return error_response('商品不存在')

    data = request.get_json(silent=True) or request.form
    product.name = data.get('name', product.name)
    product.code = data.get('code', product.code)
    product.spec = data.get('spec', product.spec)
    product.category = data.get('category', product.category)
    product.unit = data.get('unit', product.unit)
    product.purchase_price = float(data.get('purchase_price', product.purchase_price))
    product.sale_price = float(data.get('sale_price', product.sale_price))
    product.stock = float(data.get('stock', product.stock))
    product.min_stock = float(data.get('min_stock', product.min_stock))
    product.max_stock = float(data.get('max_stock', product.max_stock))
    product.remark = data.get('remark', product.remark)

    db.session.commit()
    return success_response(product.to_dict(), '商品更新成功')


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """删除商品"""
    product = Product.query.get(product_id)
    if not product:
        return error_response('商品不存在')
    db.session.delete(product)
    db.session.commit()
    return success_response(msg='商品删除成功')


# ============================================================
# 采购订单 API
# ============================================================
@app.route('/api/purchase_orders', methods=['GET'])
def get_purchase_orders():
    """获取采购订单列表"""
    orders = PurchaseOrder.query.order_by(PurchaseOrder.id.desc()).all()
    return success_response([o.to_dict() for o in orders])


@app.route('/api/purchase_orders/<int:order_id>', methods=['GET'])
def get_purchase_order(order_id):
    """获取单个采购订单"""
    order = PurchaseOrder.query.get(order_id)
    if not order:
        return error_response('采购订单不存在')
    return success_response(order.to_dict())


@app.route('/api/purchase_orders', methods=['POST'])
def create_purchase_order():
    """创建采购订单"""
    data = request.get_json(silent=True) or request.form
    supplier_id = data.get('supplier_id')
    product_id = data.get('product_id')

    if not supplier_id:
        return error_response('请选择供应商')

    try:
        supplier_id = int(supplier_id)
    except (ValueError, TypeError):
        return error_response('供应商ID无效')

    # 验证供应商存在
    if not Supplier.query.get(supplier_id):
        return error_response('供应商不存在')

    # 验证商品（可选）
    if product_id:
        try:
            product_id = int(product_id)
            if not Product.query.get(product_id):
                return error_response('商品不存在')
        except (ValueError, TypeError):
            product_id = None

    quantity = float(data.get('quantity', 0))
    price = float(data.get('price', 0))
    total_amount = quantity * price

    order = PurchaseOrder(
        order_no=generate_order_no('PO'),
        supplier_id=supplier_id,
        product_id=product_id,
        quantity=quantity,
        price=price,
        total_amount=total_amount,
        status='pending',
        remark=data.get('remark', '')
    )
    db.session.add(order)
    db.session.commit()
    return success_response(order.to_dict(), '采购订单创建成功')


@app.route('/api/purchase_orders/<int:order_id>/approve', methods=['POST'])
def approve_purchase_order(order_id):
    """审批采购订单"""
    order = PurchaseOrder.query.get(order_id)
    if not order:
        return error_response('采购订单不存在')
    if order.status != 'pending':
        return error_response('订单状态不允许审批')

    order.status = 'approved'
    order.approved_at = datetime.now()
    db.session.commit()
    return success_response(order.to_dict(), '审批成功')


@app.route('/api/purchase_orders/<int:order_id>/receive', methods=['POST'])
def receive_purchase_order(order_id):
    """采购订单入库"""
    order = PurchaseOrder.query.get(order_id)
    if not order:
        return error_response('采购订单不存在')
    if order.status != 'approved':
        return error_response('必须先审批才能入库')

    order.status = 'received'
    order.received_at = datetime.now()

    # 增加库存并生成入库记录
    if order.product_id and order.quantity > 0:
        product = Product.query.get(order.product_id)
        if product:
            product.stock += order.quantity

            # 生成入库记录
            record = InventoryRecord(
                record_no=generate_order_no('IR'),
                type='in',
                product_id=order.product_id,
                quantity=order.quantity,
                price=order.price,
                related_order=order.order_no,
                remark='采购入库'
            )
            db.session.add(record)

    db.session.commit()
    return success_response(order.to_dict(), '入库成功，库存已更新')


@app.route('/api/purchase_orders/<int:order_id>', methods=['PUT'])
def update_purchase_order(order_id):
    """更新采购订单"""
    order = PurchaseOrder.query.get(order_id)
    if not order:
        return error_response('采购订单不存在')

    data = request.get_json(silent=True) or request.form
    if data.get('supplier_id'):
        order.supplier_id = int(data['supplier_id'])
    if data.get('product_id'):
        order.product_id = int(data['product_id'])
    if data.get('quantity') is not None:
        order.quantity = float(data['quantity'])
    if data.get('price') is not None:
        order.price = float(data['price'])
        order.total_amount = order.quantity * order.price
    if data.get('remark'):
        order.remark = data['remark']
    if data.get('status'):
        order.status = data['status']

    db.session.commit()
    return success_response(order.to_dict(), '更新成功')


@app.route('/api/purchase_orders/<int:order_id>', methods=['DELETE'])
def delete_purchase_order(order_id):
    """删除采购订单"""
    order = PurchaseOrder.query.get(order_id)
    if not order:
        return error_response('采购订单不存在')
    db.session.delete(order)
    db.session.commit()
    return success_response(msg='删除成功')


# ============================================================
# 销售订单 API
# ============================================================
@app.route('/api/sales_orders', methods=['GET'])
def get_sales_orders():
    """获取销售订单列表"""
    orders = SalesOrder.query.order_by(SalesOrder.id.desc()).all()
    return success_response([o.to_dict() for o in orders])


@app.route('/api/sales_orders/<int:order_id>', methods=['GET'])
def get_sales_order(order_id):
    """获取单个销售订单"""
    order = SalesOrder.query.get(order_id)
    if not order:
        return error_response('销售订单不存在')
    return success_response(order.to_dict())


@app.route('/api/sales_orders', methods=['POST'])
def create_sales_order():
    """创建销售订单"""
    data = request.get_json(silent=True) or request.form
    customer_id = data.get('customer_id')
    product_id = data.get('product_id')

    if not customer_id:
        return error_response('请选择客户')

    try:
        customer_id = int(customer_id)
    except (ValueError, TypeError):
        return error_response('客户ID无效')

    # 验证客户存在
    if not Customer.query.get(customer_id):
        return error_response('客户不存在')

    # 验证商品（可选）
    if product_id:
        try:
            product_id = int(product_id)
            if not Product.query.get(product_id):
                return error_response('商品不存在')
        except (ValueError, TypeError):
            product_id = None

    quantity = float(data.get('quantity', 0))
    price = float(data.get('sale_price', data.get('price', 0)))
    total_amount = quantity * price

    order = SalesOrder(
        order_no=generate_order_no('SO'),
        customer_id=customer_id,
        product_id=product_id,
        quantity=quantity,
        price=price,
        total_amount=total_amount,
        status='pending',
        remark=data.get('remark', '')
    )
    db.session.add(order)
    db.session.commit()
    return success_response(order.to_dict(), '销售订单创建成功')


@app.route('/api/sales_orders/<int:order_id>/ship', methods=['POST'])
def ship_sales_order(order_id):
    """销售订单发货"""
    order = SalesOrder.query.get(order_id)
    if not order:
        return error_response('销售订单不存在')

    # 确认订单（从待确认 -> 已确认）
    if order.status == 'pending':
        order.status = 'confirmed'

    # 检查库存
    if order.product_id and order.quantity > 0:
        product = Product.query.get(order.product_id)
        if product and product.stock < order.quantity:
            return error_response(f'库存不足，当前库存：{product.stock}')

        # 扣减库存
        product.stock -= order.quantity

        # 生成出库记录
        record = InventoryRecord(
            record_no=generate_order_no('OR'),
            type='out',
            product_id=order.product_id,
            quantity=order.quantity,
            price=order.price,
            related_order=order.order_no,
            remark='销售出库'
        )
        db.session.add(record)

    order.status = 'shipped'
    order.shipped_at = datetime.now()
    db.session.commit()
    return success_response(order.to_dict(), '发货成功，库存已扣减')


@app.route('/api/sales_orders/<int:order_id>', methods=['PUT'])
def update_sales_order(order_id):
    """更新销售订单"""
    order = SalesOrder.query.get(order_id)
    if not order:
        return error_response('销售订单不存在')

    data = request.get_json(silent=True) or request.form
    if data.get('customer_id'):
        order.customer_id = int(data['customer_id'])
    if data.get('product_id'):
        order.product_id = int(data['product_id'])
    if data.get('quantity') is not None:
        order.quantity = float(data['quantity'])
    if data.get('price') is not None:
        order.price = float(data['price'])
        order.total_amount = order.quantity * order.price
    if data.get('remark'):
        order.remark = data['remark']
    if data.get('status'):
        order.status = data['status']
    if data.get('tracking_no'):
        order.tracking_no = data['tracking_no']

    db.session.commit()
    return success_response(order.to_dict(), '更新成功')


@app.route('/api/sales_orders/<int:order_id>', methods=['DELETE'])
def delete_sales_order(order_id):
    """删除销售订单"""
    order = SalesOrder.query.get(order_id)
    if not order:
        return error_response('销售订单不存在')
    db.session.delete(order)
    db.session.commit()
    return success_response(msg='删除成功')


# ============================================================
# 库存管理 API
# ============================================================
@app.route('/api/inventory_records', methods=['GET'])
def get_inventory_records():
    """获取库存出入库记录"""
    records = InventoryRecord.query.order_by(InventoryRecord.id.desc()).all()
    return success_response([r.to_dict() for r in records])


@app.route('/api/inventory/summary', methods=['GET'])
def get_inventory_summary():
    """获取库存汇总"""
    products = Product.query.order_by(Product.stock.asc()).all()
    result = []
    for p in products:
        status = '正常'
        if p.stock <= p.min_stock:
            status = '库存不足'
        if p.stock >= p.max_stock:
            status = '积压'
        result.append({
            'id': p.id,
            'code': p.code,
            'name': p.name,
            'category': p.category,
            'spec': p.spec,
            'stock': p.stock,
            'min_stock': p.min_stock,
            'max_stock': p.max_stock,
            'unit': p.unit,
            'status': status
        })
    return success_response(result)


@app.route('/api/inventory_records', methods=['POST'])
def create_inventory_record():
    """手动添加出入库记录"""
    data = request.get_json(silent=True) or request.form
    product_id = data.get('product_id')
    if not product_id:
        return error_response('请选择商品')

    product_id = int(product_id)
    product = Product.query.get(product_id)
    if not product:
        return error_response('商品不存在')

    record_type = data.get('type', 'in')
    quantity = float(data.get('quantity', 0))

    if record_type == 'out' and product.stock < quantity:
        return error_response(f'库存不足，当前库存：{product.stock}')

    # 更新库存
    if record_type == 'in':
        product.stock += quantity
    else:
        product.stock -= quantity

    # 生成记录
    record = InventoryRecord(
        record_no=generate_order_no('MAN'),
        type=record_type,
        product_id=product_id,
        quantity=quantity,
        price=float(data.get('price', 0)),
        related_order=data.get('related_order', ''),
        remark=data.get('remark', '手动调整')
    )
    db.session.add(record)
    db.session.commit()
    return success_response(record.to_dict(), '记录添加成功')


# ============================================================
# 仪表盘 API
# ============================================================
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    """获取仪表盘统计数据"""
    total_suppliers = Supplier.query.count()
    total_customers = Customer.query.count()
    total_products = Product.query.count()

    # 采购统计
    purchase_orders = PurchaseOrder.query.count()
    purchase_total = db.session.query(db.func.sum(PurchaseOrder.total_amount)).scalar() or 0

    # 销售统计
    sales_orders = SalesOrder.query.count()
    sales_total = db.session.query(db.func.sum(SalesOrder.total_amount)).scalar() or 0

    # 库存预警
    low_stock = Product.query.filter(Product.stock <= Product.min_stock).count()

    # 库存总价值
    inventory_value = db.session.query(
        db.func.sum(Product.stock * Product.purchase_price)
    ).scalar() or 0

    return success_response({
        'total_suppliers': total_suppliers,
        'total_customers': total_customers,
        'total_products': total_products,
        'purchase_orders': purchase_orders,
        'purchase_total': purchase_total,
        'sales_orders': sales_orders,
        'sales_total': sales_total,
        'inventory_value': inventory_value,
        'low_stock_count': low_stock
    }, '数据获取成功')


# ============================================================
# 初始化数据
# ============================================================
def init_sample_data():
    """初始化示例数据"""
    # 检查是否已有数据
    if User.query.count() > 0:
        return

    # 创建默认用户
    users = [
        {'username': 'admin', 'password': 'admin123', 'real_name': '系统管理员', 'role': 'admin', 'department': 'IT部'},
        {'username': 'manager', 'password': 'manager123', 'real_name': '张经理', 'role': 'manager', 'department': '总经办'},
        {'username': 'test', 'password': 'test123', 'real_name': '测试员', 'role': 'user', 'department': '测试部'},
        {'username': 'caigou', 'password': '123456', 'real_name': '采购员小李', 'role': 'user', 'department': '采购部'},
        {'username': 'xiaoshou', 'password': '123456', 'real_name': '销售员小王', 'role': 'user', 'department': '销售部'},
    ]
    for u in users:
        user = User(
            username=u['username'],
            real_name=u['real_name'],
            role=u['role'],
            department=u['department'],
            status=1
        )
        user.set_password(u['password'])
        db.session.add(user)

    # 创建示例供应商
    suppliers = [
        {'name': '深圳顺络电子股份有限公司', 'contact': '李明', 'phone': '0755-88881001', 'email': 'supply@shunluo.com', 'address': '深圳市龙华区观澜街道', 'level': 'A', 'remark': '长期合作伙伴'},
        {'name': '风华高科电子', 'contact': '王强', 'phone': '0758-28881002', 'email': 'fh@fenghua.com', 'address': '广东省肇庆市端州区', 'level': 'B', 'remark': '常规供应商'},
        {'name': '深圳华强电子', 'contact': '张伟', 'phone': '0755-88881003', 'email': 'sales@huaqiang.com', 'address': '深圳市福田区华强北', 'level': 'A', 'remark': '主要客户兼供应商'},
        {'name': '广州亿城电子', 'contact': '刘芳', 'phone': '020-66661004', 'email': 'info@yicheng.com', 'address': '广州市天河区', 'level': 'C', 'remark': '备选供应商'},
    ]
    for s in suppliers:
        supplier = Supplier(**s)
        db.session.add(supplier)

    # 创建示例客户
    customers = [
        {'name': '深圳市华强电子有限公司', 'contact': '王经理', 'phone': '0755-83332001', 'email': 'sales@huaqiang.com', 'address': '深圳市福田区华强北电子城', 'level': 'VIP', 'credit_limit': 100000},
        {'name': '深圳赛格电子市场', 'contact': '陈主管', 'phone': '0755-83332002', 'email': 'contact@saige.com', 'address': '深圳市福田区深南中路', 'level': 'VIP', 'credit_limit': 80000},
        {'name': '广州电子科技公司', 'contact': '李经理', 'phone': '020-62222003', 'email': 'guangzhou@elec.com', 'address': '广州市越秀区', 'level': '一般', 'credit_limit': 30000},
        {'name': '东莞市新科电子厂', 'contact': '赵厂长', 'phone': '0769-22222004', 'email': 'xinco@dg.com', 'address': '东莞市长安镇', 'level': '一般', 'credit_limit': 20000},
    ]
    for c in customers:
        customer = Customer(**c)
        db.session.add(customer)

    # 创建示例商品
    products = [
        {'code': 'SKU-0001', 'name': '贴片电阻 10KΩ ±1% 0805', 'spec': '0805', 'category': '电阻', 'unit': '个', 'purchase_price': 0.015, 'sale_price': 0.025, 'stock': 5000, 'min_stock': 1000, 'max_stock': 20000},
        {'code': 'SKU-0002', 'name': '贴片电容 10µF ±10% 0805', 'spec': '0805', 'category': '电容', 'unit': '个', 'purchase_price': 0.08, 'sale_price': 0.15, 'stock': 3000, 'min_stock': 500, 'max_stock': 15000},
        {'code': 'SKU-0003', 'name': '贴片电感 4.7µH ±20% 1206', 'spec': '1206', 'category': '电感', 'unit': '个', 'purchase_price': 0.25, 'sale_price': 0.5, 'stock': 1500, 'min_stock': 300, 'max_stock': 8000},
        {'code': 'SKU-0004', 'name': 'IC芯片 STM32F103C8T6', 'spec': 'LQFP-48', 'category': 'IC', 'unit': '片', 'purchase_price': 8.5, 'sale_price': 15.0, 'stock': 500, 'min_stock': 100, 'max_stock': 2000},
        {'code': 'SKU-0005', 'name': '二极管 1N4148', 'spec': 'DO-35', 'category': '二极管', 'unit': '个', 'purchase_price': 0.05, 'sale_price': 0.12, 'stock': 8000, 'min_stock': 2000, 'max_stock': 30000},
        {'code': 'SKU-0006', 'name': '三极管 S8050 NPN', 'spec': 'TO-92', 'category': '三极管', 'unit': '个', 'purchase_price': 0.08, 'sale_price': 0.18, 'stock': 6000, 'min_stock': 1000, 'max_stock': 25000},
    ]
    for p in products:
        product = Product(**p)
        db.session.add(product)

    db.session.commit()
    print('示例数据初始化完成！')


# ============================================================
# 启动应用
# ============================================================
if __name__ == '__main__':
    # 创建表
    with app.app_context():
        db.create_all()
        init_sample_data()

    print('=' * 50)
    print('明远电子科技 ERP 管理系统')
    print('访问地址： http://127.0.0.1:5000')
    print('测试账号： admin / admin123')
    print('           manager / manager123')
    print('           test / test123')
    print('=' * 50)

    app.run(host='127.0.0.1', port=5000, debug=True)
