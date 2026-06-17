// ==================== 通用工具函数 ====================
function apiGet(url) {
    return fetch('/api' + url).then(r => r.json());
}

function apiPost(url, data) {
    return fetch('/api' + url, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    }).then(r => r.json());
}

function apiPut(url, data) {
    return fetch('/api' + url, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    }).then(r => r.json());
}

function apiDelete(url) {
    return fetch('/api' + url, {
        method: 'DELETE'
    }).then(r => r.json());
}

function showSuccess(msg) {
    const div = document.createElement('div');
    div.className = 'success-flash';
    div.textContent = msg;
    document.body.appendChild(div);
    setTimeout(() => div.remove(), 2500);
}

function showError(msg) {
    const div = document.createElement('div');
    div.className = 'error-flash';
    div.textContent = msg;
    document.body.appendChild(div);
    setTimeout(() => div.remove(), 2500);
}

function confirmAction(msg) {
    return confirm(msg);
}

function setTitle(title) {
    document.getElementById('pageTitle').textContent = title;
}

function doLogout() {
    if (confirmAction('确定要退出登录吗？')) {
        localStorage.clear();
        window.location.href = '/';
    }
}

function formatMoney(num) {
    if (!num && num !== 0) return '0.00';
    return parseFloat(num).toFixed(2);
}

// ==================== 仪表盘 ====================
function loadDashboard() {
    setTitle('数据总览');
    apiGet('/dashboard').then(data => {
        if (data.code === 0) {
            const d = data.data;
            document.getElementById('supplierCount').textContent = d.total_suppliers;
            document.getElementById('customerCount').textContent = d.total_customers;
            document.getElementById('productCount').textContent = d.total_products;
            document.getElementById('purchaseCount').textContent = d.purchase_orders;
            document.getElementById('salesCount').textContent = d.sales_orders;
            document.getElementById('salesTotal').textContent = '￥' + formatMoney(d.sales_total);
            document.getElementById('inventoryValue').textContent = '￥' + formatMoney(d.inventory_value);
            document.getElementById('lowStockCount').textContent = d.low_stock_count;
        }
    });
}

// ==================== 通用渲染函数 ====================
function renderTable(headers, rows, actions) {
    let html = '<div class="table-container"><table><thead><tr>';
    headers.forEach(h => html += '<th>' + h + '</th>');
    if (actions) html += '<th>操作</th>';
    html += '</tr></thead><tbody>';

    if (rows.length === 0) {
        html += '<tr><td colspan="' + (headers.length + (actions ? 1 : 0)) + '" class="empty-state">暂无数据</td></tr>';
    } else {
        rows.forEach(row => {
            html += '<tr>';
            row.forEach(cell => html += '<td>' + cell + '</td>');
            if (actions) html += '<td>' + actions(row[row.length - 1] ? row[row.length - 1] : row[0]) + '</td>';
            html += '</tr>';
        });
    }
    html += '</tbody></table></div>';
    return html;
}

function renderModal(title, formFields, onSubmit) {
    const modalHtml = `
        <div class="modal-overlay active" id="modalOverlay">
            <div class="modal">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="modal-close" onclick="closeModal()">×</button>
                </div>
                <div class="modal-body">
                    <div class="modal-form-grid" id="modalFormGrid">${formFields}</div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-default" onclick="closeModal()">取消</button>
                    <button class="btn btn-primary" id="modalSubmitBtn">确认</button>
                </div>
            </div>
        </div>
    `;
    const existing = document.getElementById('modalOverlay');
    if (existing) existing.remove();

    const wrapper = document.createElement('div');
    wrapper.innerHTML = modalHtml;
    document.body.appendChild(wrapper.firstElementChild);

    document.getElementById('modalSubmitBtn').onclick = onSubmit;
}

function closeModal() {
    const overlay = document.getElementById('modalOverlay');
    if (overlay) overlay.remove();
}

// ==================== 用户管理 ====================
function loadUsers() {
    setTitle('用户管理');
    apiGet('/users').then(data => {
        if (data.code === 0) {
            const rows = data.data.map(u => [
                u.id, u.username, u.real_name, u.role, u.department,
                u.phone || '-', u.email || '-',
                u.status === 1 ? '<span class="status-badge status-received">启用</span>' : '<span class="status-badge status-low">禁用</span>',
                u.id
            ]);
            const contentArea = document.getElementById('contentArea');
            contentArea.innerHTML = `
                <div class="card">
                    <div class="card-header">
                        <h2>用户列表</h2>
                        <button class="btn btn-primary" onclick="showAddUser()">+ 新增用户</button>
                    </div>
                    <div class="card-body">
                        ${renderTable(
                            ['ID', '用户名', '姓名', '角色', '部门', '电话', '邮箱', '状态'],
                            rows,
                            id => `<button class="btn btn-sm btn-info" onclick="showEditUser(${id})">编辑</button> <button class="btn btn-sm btn-danger" onclick="deleteUser(${id})">删除</button>`
                        )}
                    </div>
                </div>
            `;
        }
    });
}

function showAddUser() {
    const fields = `
        <div><label>用户名 *</label><input type="text" id="f_username" placeholder="用户名"></div>
        <div><label>密码 *</label><input type="password" id="f_password" placeholder="密码" value="123456"></div>
        <div><label>姓名</label><input type="text" id="f_realname" placeholder="真实姓名"></div>
        <div><label>角色</label><select id="f_role"><option value="user">普通用户</option><option value="manager">管理员</option><option value="admin">超级管理员</option></select></div>
        <div><label>部门</label><input type="text" id="f_department" placeholder="部门"></div>
        <div><label>电话</label><input type="text" id="f_phone" placeholder="电话"></div>
        <div class="full-width"><label>邮箱</label><input type="email" id="f_email" placeholder="邮箱"></div>
    `;
    renderModal('新增用户', fields, function() {
        const data = {
            username: document.getElementById('f_username').value.trim(),
            password: document.getElementById('f_password').value,
            real_name: document.getElementById('f_realname').value.trim(),
            role: document.getElementById('f_role').value,
            department: document.getElementById('f_department').value.trim(),
            phone: document.getElementById('f_phone').value.trim(),
            email: document.getElementById('f_email').value.trim()
        };
        if (!data.username) { showError('用户名不能为空'); return; }
        apiPost('/users', data).then(res => {
            if (res.code === 0) { showSuccess('用户创建成功'); closeModal(); loadUsers(); }
            else { showError(res.msg); }
        });
    });
}

function showEditUser(id) {
    apiGet('/users/' + id).then(data => {
        if (data.code !== 0) { showError('获取用户信息失败'); return; }
        const u = data.data;
        const fields = `
            <div><label>用户名</label><input type="text" id="f_username" value="${u.username}"></div>
            <div><label>新密码</label><input type="password" id="f_password" placeholder="不改则留空"></div>
            <div><label>姓名</label><input type="text" id="f_realname" value="${u.real_name || ''}"></div>
            <div><label>角色</label><select id="f_role">
                <option value="user" ${u.role==='user'?'selected':''}>普通用户</option>
                <option value="manager" ${u.role==='manager'?'selected':''}>管理员</option>
                <option value="admin" ${u.role==='admin'?'selected':''}>超级管理员</option>
            </select></div>
            <div><label>部门</label><input type="text" id="f_department" value="${u.department || ''}"></div>
            <div><label>电话</label><input type="text" id="f_phone" value="${u.phone || ''}"></div>
            <div class="full-width"><label>邮箱</label><input type="email" id="f_email" value="${u.email || ''}"></div>
        `;
        renderModal('编辑用户', fields, function() {
            const submitData = {
                username: document.getElementById('f_username').value,
                real_name: document.getElementById('f_realname').value,
                role: document.getElementById('f_role').value,
                department: document.getElementById('f_department').value,
                phone: document.getElementById('f_phone').value,
                email: document.getElementById('f_email').value
            };
            const pw = document.getElementById('f_password').value;
            if (pw) submitData.password = pw;
            apiPut('/users/' + id, submitData).then(res => {
                if (res.code === 0) { showSuccess('更新成功'); closeModal(); loadUsers(); }
                else { showError(res.msg); }
            });
        });
    });
}

function deleteUser(id) {
    if (!confirmAction('确定删除该用户吗？')) return;
    apiDelete('/users/' + id).then(res => {
        if (res.code === 0) { showSuccess('删除成功'); loadUsers(); }
        else { showError(res.msg); }
    });
}

// ==================== 供应商管理 ====================
function loadSuppliers() {
    setTitle('供应商管理');
    const keyword = document.getElementById('searchInput') ? document.getElementById('searchInput').value.trim() : '';
    apiGet('/suppliers?keyword=' + keyword).then(data => {
        if (data.code === 0) {
            const rows = data.data.map(s => [
                s.id, s.name, s.contact || '-', s.phone || '-', s.email || '-', s.address || '-',
                '<span class="status-badge status-' + (s.level === 'A' ? 'received' : s.level === 'B' ? 'confirmed' : 'pending') + '">' + s.level + '级</span>',
                s.remark || '-', s.id
            ]);
            const contentArea = document.getElementById('contentArea');
            contentArea.innerHTML = `
                <div class="card">
                    <div class="card-header">
                        <h2>供应商列表</h2>
                        <div class="toolbar">
                            <div class="search-box">
                                <input type="text" id="searchInput" placeholder="搜索供应商名称" value="${keyword}" onkeypress="if(event.key==='Enter')loadSuppliers()">
                                <button class="btn btn-info" onclick="loadSuppliers()">搜索</button>
                            </div>
                            <button class="btn btn-primary" onclick="showAddSupplier()">+ 新增供应商</button>
                        </div>
                    </div>
                    <div class="card-body">
                        ${renderTable(
                            ['ID', '供应商名称', '联系人', '电话', '邮箱', '地址', '等级', '备注'],
                            rows,
                            id => `<button class="btn btn-sm btn-info" onclick="showEditSupplier(${id})">编辑</button> <button class="btn btn-sm btn-danger" onclick="deleteSupplier(${id})">删除</button>`
                        )}
                    </div>
                </div>
            `;
        }
    });
}

function showAddSupplier() {
    const fields = `
        <div><label>供应商名称 *</label><input type="text" id="f_name" placeholder="供应商名称"></div>
        <div><label>联系人</label><input type="text" id="f_contact" placeholder="联系人"></div>
        <div><label>电话</label><input type="text" id="f_phone" placeholder="电话"></div>
        <div><label>邮箱</label><input type="email" id="f_email" placeholder="邮箱"></div>
        <div class="full-width"><label>地址</label><input type="text" id="f_address" placeholder="地址"></div>
        <div><label>等级</label><select id="f_level"><option value="A">A级</option><option value="B">B级</option><option value="C">C级</option></select></div>
        <div class="full-width"><label>备注</label><textarea id="f_remark" placeholder="备注"></textarea></div>
    `;
    renderModal('新增供应商', fields, function() {
        const data = {
            name: document.getElementById('f_name').value.trim(),
            contact: document.getElementById('f_contact').value.trim(),
            phone: document.getElementById('f_phone').value.trim(),
            email: document.getElementById('f_email').value.trim(),
            address: document.getElementById('f_address').value.trim(),
            level: document.getElementById('f_level').value,
            remark: document.getElementById('f_remark').value.trim()
        };
        if (!data.name) { showError('供应商名称不能为空'); return; }
        apiPost('/suppliers', data).then(res => {
            if (res.code === 0) { showSuccess('供应商创建成功'); closeModal(); loadSuppliers(); }
            else { showError(res.msg); }
        });
    });
}

function showEditSupplier(id) {
    apiGet('/suppliers/' + id).then(data => {
        if (data.code !== 0) { showError('获取信息失败'); return; }
        const s = data.data;
        const fields = `
            <div><label>供应商名称 *</label><input type="text" id="f_name" value="${s.name}"></div>
            <div><label>联系人</label><input type="text" id="f_contact" value="${s.contact || ''}"></div>
            <div><label>电话</label><input type="text" id="f_phone" value="${s.phone || ''}"></div>
            <div><label>邮箱</label><input type="email" id="f_email" value="${s.email || ''}"></div>
            <div class="full-width"><label>地址</label><input type="text" id="f_address" value="${s.address || ''}"></div>
            <div><label>等级</label><select id="f_level">
                <option value="A" ${s.level==='A'?'selected':''}>A级</option>
                <option value="B" ${s.level==='B'?'selected':''}>B级</option>
                <option value="C" ${s.level==='C'?'selected':''}>C级</option>
            </select></div>
            <div class="full-width"><label>备注</label><textarea id="f_remark">${s.remark || ''}</textarea></div>
        `;
        renderModal('编辑供应商', fields, function() {
            const submitData = {
                name: document.getElementById('f_name').value,
                contact: document.getElementById('f_contact').value,
                phone: document.getElementById('f_phone').value,
                email: document.getElementById('f_email').value,
                address: document.getElementById('f_address').value,
                level: document.getElementById('f_level').value,
                remark: document.getElementById('f_remark').value
            };
            apiPut('/suppliers/' + id, submitData).then(res => {
                if (res.code === 0) { showSuccess('更新成功'); closeModal(); loadSuppliers(); }
                else { showError(res.msg); }
            });
        });
    });
}

function deleteSupplier(id) {
    if (!confirmAction('确定删除该供应商吗？')) return;
    apiDelete('/suppliers/' + id).then(res => {
        if (res.code === 0) { showSuccess('删除成功'); loadSuppliers(); }
        else { showError(res.msg); }
    });
}

// ==================== 客户管理 ====================
function loadCustomers() {
    setTitle('客户管理');
    const keyword = document.getElementById('searchInput') ? document.getElementById('searchInput').value.trim() : '';
    apiGet('/customers?keyword=' + keyword).then(data => {
        if (data.code === 0) {
            const rows = data.data.map(c => [
                c.id, c.name, c.contact || '-', c.phone || '-', c.email || '-', c.address || '-',
                '<span class="status-badge status-' + (c.level === 'VIP' ? 'received' : 'confirmed') + '">' + c.level + '</span>',
                '￥' + formatMoney(c.credit_limit), c.id
            ]);
            const contentArea = document.getElementById('contentArea');
            contentArea.innerHTML = `
                <div class="card">
                    <div class="card-header">
                        <h2>客户列表</h2>
                        <div class="toolbar">
                            <div class="search-box">
                                <input type="text" id="searchInput" placeholder="搜索客户名称" value="${keyword}" onkeypress="if(event.key==='Enter')loadCustomers()">
                                <button class="btn btn-info" onclick="loadCustomers()">搜索</button>
                            </div>
                            <button class="btn btn-primary" onclick="showAddCustomer()">+ 新增客户</button>
                        </div>
                    </div>
                    <div class="card-body">
                        ${renderTable(
                            ['ID', '客户名称', '联系人', '电话', '邮箱', '地址', '等级', '信用额度'],
                            rows,
                            id => `<button class="btn btn-sm btn-info" onclick="showEditCustomer(${id})">编辑</button> <button class="btn btn-sm btn-danger" onclick="deleteCustomer(${id})">删除</button>`
                        )}
                    </div>
                </div>
            `;
        }
    });
}

function showAddCustomer() {
    const fields = `
        <div><label>客户名称 *</label><input type="text" id="f_name" placeholder="客户名称"></div>
        <div><label>联系人</label><input type="text" id="f_contact" placeholder="联系人"></div>
        <div><label>电话</label><input type="text" id="f_phone" placeholder="电话"></div>
        <div><label>邮箱</label><input type="email" id="f_email" placeholder="邮箱"></div>
        <div class="full-width"><label>地址</label><input type="text" id="f_address" placeholder="地址"></div>
        <div><label>等级</label><select id="f_level"><option value="VIP">VIP客户</option><option value="一般">一般客户</option><option value="潜在">潜在客户</option></select></div>
        <div><label>信用额度</label><input type="number" id="f_credit" placeholder="信用额度" value="10000"></div>
        <div class="full-width"><label>备注</label><textarea id="f_remark" placeholder="备注"></textarea></div>
    `;
    renderModal('新增客户', fields, function() {
        const data = {
            name: document.getElementById('f_name').value.trim(),
            contact: document.getElementById('f_contact').value.trim(),
            phone: document.getElementById('f_phone').value.trim(),
            email: document.getElementById('f_email').value.trim(),
            address: document.getElementById('f_address').value.trim(),
            level: document.getElementById('f_level').value,
            credit_limit: parseFloat(document.getElementById('f_credit').value) || 0,
            remark: document.getElementById('f_remark').value.trim()
        };
        if (!data.name) { showError('客户名称不能为空'); return; }
        apiPost('/customers', data).then(res => {
            if (res.code === 0) { showSuccess('客户创建成功'); closeModal(); loadCustomers(); }
            else { showError(res.msg); }
        });
    });
}

function showEditCustomer(id) {
    apiGet('/customers/' + id).then(data => {
        if (data.code !== 0) { showError('获取信息失败'); return; }
        const c = data.data;
        const fields = `
            <div><label>客户名称 *</label><input type="text" id="f_name" value="${c.name}"></div>
            <div><label>联系人</label><input type="text" id="f_contact" value="${c.contact || ''}"></div>
            <div><label>电话</label><input type="text" id="f_phone" value="${c.phone || ''}"></div>
            <div><label>邮箱</label><input type="email" id="f_email" value="${c.email || ''}"></div>
            <div class="full-width"><label>地址</label><input type="text" id="f_address" value="${c.address || ''}"></div>
            <div><label>等级</label><select id="f_level">
                <option value="VIP" ${c.level==='VIP'?'selected':''}>VIP客户</option>
                <option value="一般" ${c.level==='一般'?'selected':''}>一般客户</option>
                <option value="潜在" ${c.level==='潜在'?'selected':''}>潜在客户</option>
            </select></div>
            <div><label>信用额度</label><input type="number" id="f_credit" value="${c.credit_limit || 0}"></div>
            <div class="full-width"><label>备注</label><textarea id="f_remark">${c.remark || ''}</textarea></div>
        `;
        renderModal('编辑客户', fields, function() {
            const submitData = {
                name: document.getElementById('f_name').value,
                contact: document.getElementById('f_contact').value,
                phone: document.getElementById('f_phone').value,
                email: document.getElementById('f_email').value,
                address: document.getElementById('f_address').value,
                level: document.getElementById('f_level').value,
                credit_limit: parseFloat(document.getElementById('f_credit').value) || 0,
                remark: document.getElementById('f_remark').value
            };
            apiPut('/customers/' + id, submitData).then(res => {
                if (res.code === 0) { showSuccess('更新成功'); closeModal(); loadCustomers(); }
                else { showError(res.msg); }
            });
        });
    });
}

function deleteCustomer(id) {
    if (!confirmAction('确定删除该客户吗？')) return;
    apiDelete('/customers/' + id).then(res => {
        if (res.code === 0) { showSuccess('删除成功'); loadCustomers(); }
        else { showError(res.msg); }
    });
}

// ==================== 商品管理 ====================
function loadProducts() {
    setTitle('商品管理');
    const keyword = document.getElementById('searchInput') ? document.getElementById('searchInput').value.trim() : '';
    apiGet('/products?keyword=' + keyword).then(data => {
        if (data.code === 0) {
            const rows = data.data.map(p => {
                const stockStatus = p.stock <= p.min_stock ? 'low' : (p.stock >= p.max_stock ? 'pending' : 'received');
                return [
                    p.id, p.code, p.name, p.spec || '-', p.category || '-', p.unit,
                    '￥' + formatMoney(p.purchase_price), '￥' + formatMoney(p.sale_price),
                    p.stock,
                    '<span class="status-badge status-' + stockStatus + '">' + p.stock + '</span>',
                    p.id
                ];
            });
            const contentArea = document.getElementById('contentArea');
            contentArea.innerHTML = `
                <div class="card">
                    <div class="card-header">
                        <h2>商品列表</h2>
                        <div class="toolbar">
                            <div class="search-box">
                                <input type="text" id="searchInput" placeholder="搜索商品名称/编码" value="${keyword}" onkeypress="if(event.key==='Enter')loadProducts()">
                                <button class="btn btn-info" onclick="loadProducts()">搜索</button>
                            </div>
                            <button class="btn btn-primary" onclick="showAddProduct()">+ 新增商品</button>
                        </div>
                    </div>
                    <div class="card-body">
                        ${renderTable(
                            ['ID', '编码', '名称', '规格', '分类', '单位', '采购价', '销售价', '库存', '状态'],
                            rows,
                            id => `<button class="btn btn-sm btn-info" onclick="showEditProduct(${id})">编辑</button> <button class="btn btn-sm btn-danger" onclick="deleteProduct(${id})">删除</button>`
                        )}
                    </div>
                </div>
            `;
        }
    });
}

function showAddProduct() {
    const fields = `
        <div><label>商品编码 *</label><input type="text" id="f_code" placeholder="SKU编码"></div>
        <div><label>商品名称 *</label><input type="text" id="f_name" placeholder="商品名称"></div>
        <div><label>规格</label><input type="text" id="f_spec" placeholder="规格型号"></div>
        <div><label>分类</label><input type="text" id="f_category" placeholder="分类"></div>
        <div><label>单位</label><input type="text" id="f_unit" value="个"></div>
        <div><label>采购价</label><input type="number" id="f_pp" step="0.01" placeholder="采购价" value="0"></div>
        <div><label>销售价</label><input type="number" id="f_sp" step="0.01" placeholder="销售价" value="0"></div>
        <div><label>当前库存</label><input type="number" id="f_stock" placeholder="库存数量" value="0"></div>
        <div><label>安全库存</label><input type="number" id="f_ms" placeholder="安全库存" value="0"></div>
        <div><label>库存上限</label><input type="number" id="f_maxs" placeholder="库存上限" value="10000"></div>
        <div class="full-width"><label>备注</label><textarea id="f_remark" placeholder="备注"></textarea></div>
    `;
    renderModal('新增商品', fields, function() {
        const data = {
            code: document.getElementById('f_code').value.trim(),
            name: document.getElementById('f_name').value.trim(),
            spec: document.getElementById('f_spec').value.trim(),
            category: document.getElementById('f_category').value.trim(),
            unit: document.getElementById('f_unit').value.trim(),
            purchase_price: parseFloat(document.getElementById('f_pp').value) || 0,
            sale_price: parseFloat(document.getElementById('f_sp').value) || 0,
            stock: parseFloat(document.getElementById('f_stock').value) || 0,
            min_stock: parseFloat(document.getElementById('f_ms').value) || 0,
            max_stock: parseFloat(document.getElementById('f_maxs').value) || 10000,
            remark: document.getElementById('f_remark').value.trim()
        };
        if (!data.name || !data.code) { showError('商品编码和名称不能为空'); return; }
        apiPost('/products', data).then(res => {
            if (res.code === 0) { showSuccess('商品创建成功'); closeModal(); loadProducts(); }
            else { showError(res.msg); }
        });
    });
}

function showEditProduct(id) {
    apiGet('/products/' + id).then(data => {
        if (data.code !== 0) { showError('获取信息失败'); return; }
        const p = data.data;
        const fields = `
            <div><label>商品编码 *</label><input type="text" id="f_code" value="${p.code}"></div>
            <div><label>商品名称 *</label><input type="text" id="f_name" value="${p.name}"></div>
            <div><label>规格</label><input type="text" id="f_spec" value="${p.spec || ''}"></div>
            <div><label>分类</label><input type="text" id="f_category" value="${p.category || ''}"></div>
            <div><label>单位</label><input type="text" id="f_unit" value="${p.unit || '个'}"></div>
            <div><label>采购价</label><input type="number" id="f_pp" step="0.01" value="${p.purchase_price}"></div>
            <div><label>销售价</label><input type="number" id="f_sp" step="0.01" value="${p.sale_price}"></div>
            <div><label>当前库存</label><input type="number" id="f_stock" value="${p.stock}"></div>
            <div><label>安全库存</label><input type="number" id="f_ms" value="${p.min_stock}"></div>
            <div><label>库存上限</label><input type="number" id="f_maxs" value="${p.max_stock}"></div>
            <div class="full-width"><label>备注</label><textarea id="f_remark">${p.remark || ''}</textarea></div>
        `;
        renderModal('编辑商品', fields, function() {
            const submitData = {
                code: document.getElementById('f_code').value,
                name: document.getElementById('f_name').value,
                spec: document.getElementById('f_spec').value,
                category: document.getElementById('f_category').value,
                unit: document.getElementById('f_unit').value,
                purchase_price: parseFloat(document.getElementById('f_pp').value) || 0,
                sale_price: parseFloat(document.getElementById('f_sp').value) || 0,
                stock: parseFloat(document.getElementById('f_stock').value) || 0,
                min_stock: parseFloat(document.getElementById('f_ms').value) || 0,
                max_stock: parseFloat(document.getElementById('f_maxs').value) || 0,
                remark: document.getElementById('f_remark').value
            };
            apiPut('/products/' + id, submitData).then(res => {
                if (res.code === 0) { showSuccess('更新成功'); closeModal(); loadProducts(); }
                else { showError(res.msg); }
            });
        });
    });
}

function deleteProduct(id) {
    if (!confirmAction('确定删除该商品吗？')) return;
    apiDelete('/products/' + id).then(res => {
        if (res.code === 0) { showSuccess('删除成功'); loadProducts(); }
        else { showError(res.msg); }
    });
}

// ==================== 采购订单 ====================
function loadPurchaseOrders() {
    setTitle('采购订单管理');
    apiGet('/purchase_orders').then(data => {
        if (data.code === 0) {
            const rows = data.data.map(o => {
                const statusMap = {pending: '待审批', approved: '已审批', received: '已入库', canceled: '已取消'};
                const statusClass = o.status === 'pending' ? 'pending' : o.status === 'approved' ? 'confirmed' : o.status === 'received' ? 'received' : 'low';
                let actions = '';
                if (o.status === 'pending') {
                    actions += ' <button class="btn btn-sm btn-success" onclick="approvePurchase(' + o.id + ')">审批</button>';
                }
                if (o.status === 'approved') {
                    actions += ' <button class="btn btn-sm btn-success" onclick="receivePurchase(' + o.id + ')">入库</button>';
                }
                actions += ' <button class="btn btn-sm btn-danger" onclick="deletePurchase(' + o.id + ')">删除</button>';
                return [
                    o.id, o.order_no, o.supplier_name, o.product_name,
                    o.quantity, '￥' + formatMoney(o.price), '￥' + formatMoney(o.total_amount),
                    '<span class="status-badge status-' + statusClass + '">' + statusMap[o.status] + '</span>',
                    actions
                ];
            });
            const contentArea = document.getElementById('contentArea');
            contentArea.innerHTML = `
                <div class="card">
                    <div class="card-header">
                        <h2>采购订单列表</h2>
                        <button class="btn btn-primary" onclick="showAddPurchase()">+ 新建采购单</button>
                    </div>
                    <div class="card-body">
                        ${renderTable(
                            ['ID', '订单号', '供应商', '商品', '数量', '单价', '金额', '状态'],
                            rows.map(r => r.slice(0, 8))
                        )}
                        <div style="display:none" id="orderActions">${JSON.stringify(data.data.map(o => o.id))}</div>
                    </div>
                </div>
            `;
            // 手动添加操作列
            const table = document.querySelector('.card-body table');
            if (table && data.data.length > 0) {
                const rows2 = table.querySelectorAll('tbody tr');
                data.data.forEach((o, i) => {
                    if (rows2[i]) {
                        const statusMap = {pending: '待审批', approved: '已审批', received: '已入库', canceled: '已取消'};
                        let actions = '';
                        if (o.status === 'pending') actions += `<button class="btn btn-sm btn-success" onclick="approvePurchase(${o.id})">审批</button> `;
                        if (o.status === 'approved') actions += `<button class="btn btn-sm btn-success" onclick="receivePurchase(${o.id})">入库</button> `;
                        actions += `<button class="btn btn-sm btn-danger" onclick="deletePurchase(${o.id})">删除</button>`;
                        const cell = document.createElement('td');
                        cell.innerHTML = actions;
                        rows2[i].appendChild(cell);
                    }
                });
            }
        }
    });
}

function showAddPurchase() {
    // 获取供应商列表
    Promise.all([apiGet('/suppliers'), apiGet('/products')]).then(results => {
        const suppliers = results[0].code === 0 ? results[0].data : [];
        const products = results[1].code === 0 ? results[1].data : [];
        let supplierOptions = suppliers.map(s => '<option value="' + s.id + '">' + s.name + '</option>').join('');
        let productOptions = '<option value="">无</option>' + products.map(p => '<option value="' + p.id + '">' + p.code + ' ' + p.name + '</option>').join('');
        const fields = `
            <div><label>供应商 *</label><select id="f_supplier">${supplierOptions}</select></div>
            <div><label>商品</label><select id="f_product">${productOptions}</select></div>
            <div><label>采购数量</label><input type="number" id="f_qty" value="100" min="0"></div>
            <div><label>采购单价</label><input type="number" id="f_price" step="0.01" value="0" min="0"></div>
            <div class="full-width"><label>备注</label><textarea id="f_remark" placeholder="备注"></textarea></div>
        `;
        renderModal('新建采购订单', fields, function() {
            const data = {
                supplier_id: parseInt(document.getElementById('f_supplier').value),
                product_id: parseInt(document.getElementById('f_product').value) || null,
                quantity: parseFloat(document.getElementById('f_qty').value) || 0,
                price: parseFloat(document.getElementById('f_price').value) || 0,
                remark: document.getElementById('f_remark').value.trim()
            };
            apiPost('/purchase_orders', data).then(res => {
                if (res.code === 0) { showSuccess('采购订单创建成功'); closeModal(); loadPurchaseOrders(); }
                else { showError(res.msg); }
            });
        });
    });
}

function approvePurchase(id) {
    if (!confirmAction('确定审批该订单吗？')) return;
    apiPost('/purchase_orders/' + id + '/approve').then(res => {
        if (res.code === 0) { showSuccess('审批成功'); loadPurchaseOrders(); }
        else { showError(res.msg); }
    });
}

function receivePurchase(id) {
    if (!confirmAction('确定入库吗？这将增加商品库存。')) return;
    apiPost('/purchase_orders/' + id + '/receive').then(res => {
        if (res.code === 0) { showSuccess('入库成功'); loadPurchaseOrders(); }
        else { showError(res.msg); }
    });
}

function deletePurchase(id) {
    if (!confirmAction('确定删除该采购订单吗？')) return;
    apiDelete('/purchase_orders/' + id).then(res => {
        if (res.code === 0) { showSuccess('删除成功'); loadPurchaseOrders(); }
        else { showError(res.msg); }
    });
}

// ==================== 销售订单 ====================
function loadSalesOrders() {
    setTitle('销售订单管理');
    apiGet('/sales_orders').then(data => {
        if (data.code === 0) {
            const rows = data.data.map(o => {
                const statusMap = {pending: '待确认', confirmed: '已确认', shipped: '已发货', canceled: '已取消'};
                const statusClass = o.status === 'pending' ? 'pending' : o.status === 'confirmed' ? 'confirmed' : o.status === 'shipped' ? 'received' : 'low';
                let actions = '';
                if (o.status === 'pending' || o.status === 'confirmed') {
                    actions += ' <button class="btn btn-sm btn-success" onclick="shipSale(' + o.id + ')">发货</button> ';
                }
                actions += ' <button class="btn btn-sm btn-danger" onclick="deleteSale(' + o.id + ')">删除</button>';
                return [
                    o.id, o.order_no, o.customer_name, o.product_name,
                    o.quantity, '￥' + formatMoney(o.price), '￥' + formatMoney(o.total_amount),
                    '<span class="status-badge status-' + statusClass + '">' + statusMap[o.status] + '</span>',
                    actions
                ];
            });
            const contentArea = document.getElementById('contentArea');
            contentArea.innerHTML = `
                <div class="card">
                    <div class="card-header">
                        <h2>销售订单列表</h2>
                        <button class="btn btn-primary" onclick="showAddSale()">+ 新建销售单</button>
                    </div>
                    <div class="card-body">
                        ${renderTable(
                            ['ID', '订单号', '客户', '商品', '数量', '单价', '金额', '状态'],
                            rows.map(r => r.slice(0, 8))
                        )}
                        ${(() => {
                            const table = document.querySelector('.card-body table');
                            if (table) {
                                const rows2 = table.querySelectorAll('tbody tr');
                                data.data.forEach((o, i) => {
                                    if (rows2[i]) {
                                        let actions = '';
                                        if (o.status === 'pending' || o.status === 'confirmed') actions += `<button class="btn btn-sm btn-success" onclick="shipSale(${o.id})">发货</button> `;
                                        actions += `<button class="btn btn-sm btn-danger" onclick="deleteSale(${o.id})">删除</button>`;
                                        const cell = document.createElement('td');
                                        cell.innerHTML = actions;
                                        rows2[i].appendChild(cell);
                                    }
                                });
                            }
                            return '';
                        })()}
                    </div>
                </div>
            `;
        }
    });
}

function showAddSale() {
    Promise.all([apiGet('/customers'), apiGet('/products')]).then(results => {
        const customers = results[0].code === 0 ? results[0].data : [];
        const products = results[1].code === 0 ? results[1].data : [];
        let customerOptions = customers.map(c => '<option value="' + c.id + '">' + c.name + '</option>').join('');
        let productOptions = '<option value="">无</option>' + products.map(p => '<option value="' + p.id + '">(' + p.stock + ') ' + p.code + ' ' + p.name + '</option>').join('');
        const fields = `
            <div><label>客户 *</label><select id="f_customer">${customerOptions}</select></div>
            <div><label>商品</label><select id="f_product">${productOptions}</select></div>
            <div><label>销售数量</label><input type="number" id="f_qty" value="10" min="0"></div>
            <div><label>销售单价</label><input type="number" id="f_price" step="0.01" value="0" min="0"></div>
            <div class="full-width"><label>备注</label><textarea id="f_remark" placeholder="备注"></textarea></div>
        `;
        renderModal('新建销售订单', fields, function() {
            const data = {
                customer_id: parseInt(document.getElementById('f_customer').value),
                product_id: parseInt(document.getElementById('f_product').value) || null,
                quantity: parseFloat(document.getElementById('f_qty').value) || 0,
                price: parseFloat(document.getElementById('f_price').value) || 0,
                remark: document.getElementById('f_remark').value.trim()
            };
            apiPost('/sales_orders', data).then(res => {
                if (res.code === 0) { showSuccess('销售订单创建成功'); closeModal(); loadSalesOrders(); }
                else { showError(res.msg); }
            });
        });
    });
}

function shipSale(id) {
    if (!confirmAction('确定发货吗？这将扣减商品库存。')) return;
    apiPost('/sales_orders/' + id + '/ship').then(res => {
        if (res.code === 0) { showSuccess('发货成功'); loadSalesOrders(); }
        else { showError(res.msg); }
    });
}

function deleteSale(id) {
    if (!confirmAction('确定删除该销售订单吗？')) return;
    apiDelete('/sales_orders/' + id).then(res => {
        if (res.code === 0) { showSuccess('删除成功'); loadSalesOrders(); }
        else { showError(res.msg); }
    });
}

// ==================== 库存管理 ====================
function loadInventory() {
    setTitle('库存管理');
    apiGet('/inventory/summary').then(data => {
        if (data.code === 0) {
            const rows = data.data.map(p => {
                const stockStatus = p.status === '库存不足' ? 'low' : p.status === '积压' ? 'pending' : 'received';
                return [
                    p.id, p.code, p.name, p.spec || '-', p.unit, p.stock, p.min_stock, p.max_stock,
                    '<span class="status-badge status-' + stockStatus + '">' + p.status + '</span>'
                ];
            });
            const contentArea = document.getElementById('contentArea');
            contentArea.innerHTML = `
                <div class="card">
                    <div class="card-header">
                        <h2>库存明细</h2>
                        <button class="btn btn-info" onclick="loadInventory()">刷新</button>
                    </div>
                    <div class="card-body">
                        ${renderTable(
                            ['ID', '编码', '商品名称', '规格', '单位', '库存数量', '安全库存', '库存上限', '状态'],
                            rows
                        )}
                    </div>
                </div>
            `;
        }
    });
}
