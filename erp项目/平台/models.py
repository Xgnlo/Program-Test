"""
ERP 系统数据模型
明远电子科技有限公司 - 数据库表定义
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """用户表 - 员工账号"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)  # 用户名
    password_hash = db.Column(db.String(255), nullable=False)  # 密码哈希
    real_name = db.Column(db.String(50))  # 真实姓名
    role = db.Column(db.String(20), default='user')  # 角色：admin/manager/user
    department = db.Column(db.String(50))  # 部门
    phone = db.Column(db.String(20))  # 电话
    email = db.Column(db.String(100))  # 邮箱
    status = db.Column(db.Integer, default=1)  # 状态：1启用 0禁用
    created_at = db.Column(db.DateTime, default=datetime.now)  # 创建时间

    def set_password(self, password):
        """设置密码（加密存储）"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """转换为字典格式（用于API返回）"""
        return {
            'id': self.id,
            'username': self.username,
            'real_name': self.real_name or self.username,
            'role': self.role,
            'department': self.department,
            'phone': self.phone,
            'email': self.email,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }


class Supplier(db.Model):
    """供应商表"""
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)  # 供应商名称
    contact = db.Column(db.String(50))  # 联系人
    phone = db.Column(db.String(20))  # 电话
    email = db.Column(db.String(100))  # 邮箱
    address = db.Column(db.String(200))  # 地址
    level = db.Column(db.String(10), default='C')  # 等级：A/B/C
    remark = db.Column(db.Text)  # 备注
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 反向关联
    purchase_orders = db.relationship('PurchaseOrder', backref='supplier', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contact': self.contact,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'level': self.level,
            'remark': self.remark,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }


class Customer(db.Model):
    """客户表"""
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)  # 客户名称
    contact = db.Column(db.String(50))  # 联系人
    phone = db.Column(db.String(20))  # 电话
    email = db.Column(db.String(100))  # 邮箱
    address = db.Column(db.String(200))  # 地址
    level = db.Column(db.String(20), default='一般')  # 客户等级：VIP/一般/潜在
    credit_limit = db.Column(db.Float, default=10000)  # 信用额度
    remark = db.Column(db.Text)  # 备注
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 反向关联
    sales_orders = db.relationship('SalesOrder', backref='customer', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contact': self.contact,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'level': self.level,
            'credit_limit': self.credit_limit,
            'remark': self.remark,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }


class Product(db.Model):
    """商品表 - 物料/产品目录"""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(50), unique=True, nullable=False)  # SKU编码
    name = db.Column(db.String(100), nullable=False)  # 商品名称
    spec = db.Column(db.String(100))  # 规格
    category = db.Column(db.String(50))  # 分类
    unit = db.Column(db.String(20), default='个')  # 单位
    purchase_price = db.Column(db.Float, default=0.0)  # 采购指导价
    sale_price = db.Column(db.Float, default=0.0)  # 销售指导价
    stock = db.Column(db.Float, default=0.0)  # 当前库存
    min_stock = db.Column(db.Float, default=0.0)  # 安全库存
    max_stock = db.Column(db.Float, default=10000)  # 库存上限
    remark = db.Column(db.Text)  # 备注
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'spec': self.spec,
            'category': self.category,
            'unit': self.unit,
            'purchase_price': self.purchase_price,
            'sale_price': self.sale_price,
            'stock': self.stock,
            'min_stock': self.min_stock,
            'max_stock': self.max_stock,
            'remark': self.remark,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }


class PurchaseOrder(db.Model):
    """采购订单表"""
    __tablename__ = 'purchase_orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_no = db.Column(db.String(50), unique=True, nullable=False)  # 采购单号
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)  # 供应商ID
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))  # 商品ID
    quantity = db.Column(db.Float, default=0.0)  # 采购数量
    price = db.Column(db.Float, default=0.0)  # 采购单价
    total_amount = db.Column(db.Float, default=0.0)  # 总金额
    status = db.Column(db.String(20), default='pending')  # 状态：pending待审批/approved已审批/received已入库/canceled已取消
    expect_date = db.Column(db.Date)  # 预计到货日期
    remark = db.Column(db.Text)  # 备注
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 采购人
    created_at = db.Column(db.DateTime, default=datetime.now)
    approved_at = db.Column(db.DateTime)  # 审批时间
    received_at = db.Column(db.DateTime)  # 入库时间

    def to_dict(self):
        supplier_name = self.supplier.name if self.supplier else ''
        product_name = ''
        product_code = ''
        # 获取商品信息需要查询 Product
        if self.product_id:
            p = Product.query.get(self.product_id)
            if p:
                product_name = p.name
                product_code = p.code
        return {
            'id': self.id,
            'order_no': self.order_no,
            'supplier_id': self.supplier_id,
            'supplier_name': supplier_name,
            'product_id': self.product_id,
            'product_name': product_name,
            'product_code': product_code,
            'quantity': self.quantity,
            'price': self.price,
            'total_amount': self.total_amount,
            'status': self.status,
            'status_text': self.get_status_text(),
            'expect_date': self.expect_date.strftime('%Y-%m-%d') if self.expect_date else '',
            'remark': self.remark,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }

    def get_status_text(self):
        status_map = {
            'pending': '待审批',
            'approved': '已审批',
            'received': '已入库',
            'canceled': '已取消'
        }
        return status_map.get(self.status, self.status)


class SalesOrder(db.Model):
    """销售订单表"""
    __tablename__ = 'sales_orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_no = db.Column(db.String(50), unique=True, nullable=False)  # 销售单号
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)  # 客户ID
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))  # 商品ID
    quantity = db.Column(db.Float, default=0.0)  # 销售数量
    price = db.Column(db.Float, default=0.0)  # 销售单价
    total_amount = db.Column(db.Float, default=0.0)  # 总金额
    status = db.Column(db.String(20), default='pending')  # 状态：pending待确认/confirmed已确认/shipped已发货/canceled已取消
    expect_date = db.Column(db.Date)  # 预计发货日期
    tracking_no = db.Column(db.String(100))  # 物流单号
    remark = db.Column(db.Text)  # 备注
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 销售员
    created_at = db.Column(db.DateTime, default=datetime.now)
    shipped_at = db.Column(db.DateTime)  # 发货时间

    def to_dict(self):
        customer_name = self.customer.name if self.customer else ''
        product_name = ''
        product_code = ''
        if self.product_id:
            p = Product.query.get(self.product_id)
            if p:
                product_name = p.name
                product_code = p.code
        return {
            'id': self.id,
            'order_no': self.order_no,
            'customer_id': self.customer_id,
            'customer_name': customer_name,
            'product_id': self.product_id,
            'product_name': product_name,
            'product_code': product_code,
            'quantity': self.quantity,
            'price': self.price,
            'total_amount': self.total_amount,
            'status': self.status,
            'status_text': self.get_status_text(),
            'expect_date': self.expect_date.strftime('%Y-%m-%d') if self.expect_date else '',
            'tracking_no': self.tracking_no,
            'remark': self.remark,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }

    def get_status_text(self):
        status_map = {
            'pending': '待确认',
            'confirmed': '已确认',
            'shipped': '已发货',
            'canceled': '已取消'
        }
        return status_map.get(self.status, self.status)


class InventoryRecord(db.Model):
    """库存出入库记录表"""
    __tablename__ = 'inventory_records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    record_no = db.Column(db.String(50), unique=True, nullable=False)  # 记录编号
    type = db.Column(db.String(20))  # 类型：in入库 out出库
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)  # 商品ID
    quantity = db.Column(db.Float, default=0.0)  # 数量
    price = db.Column(db.Float, default=0.0)  # 单价
    related_order = db.Column(db.String(100))  # 关联单号（采购/销售单号）
    remark = db.Column(db.Text)  # 备注
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 操作人
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        product_name = ''
        product_code = ''
        p = Product.query.get(self.product_id)
        if p:
            product_name = p.name
            product_code = p.code
        return {
            'id': self.id,
            'record_no': self.record_no,
            'type': self.type,
            'type_text': '入库' if self.type == 'in' else '出库',
            'product_id': self.product_id,
            'product_name': product_name,
            'product_code': product_code,
            'quantity': self.quantity,
            'price': self.price,
            'related_order': self.related_order,
            'remark': self.remark,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }
