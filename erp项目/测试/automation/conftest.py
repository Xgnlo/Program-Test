"""
pytest 配置文件
提供测试夹具（fixtures）和钩子函数
"""
import os
import sys
import pytest
from playwright.sync_api import sync_playwright
from config import config
from utils import logger, load_yaml

# 添加项目路径到 sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 加载测试数据
TEST_DATA = load_yaml(os.path.join(os.path.dirname(__file__), "data", "test_data.yaml"))


@pytest.fixture(scope="session")
def playwright():
    """Playwright 会话级夹具"""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright):
    """浏览器会话级夹具"""
    browser_type = config.BROWSER.lower()
    
    if browser_type == "chromium":
        browser = playwright.chromium.launch(
            headless=config.HEADLESS,
            args=["--start-maximized"]
        )
    elif browser_type == "firefox":
        browser = playwright.firefox.launch(headless=config.HEADLESS)
    elif browser_type == "webkit":
        browser = playwright.webkit.launch(headless=config.HEADLESS)
    else:
        raise ValueError(f"不支持的浏览器类型: {browser_type}")
    
    logger.info(f"启动浏览器: {browser_type} (headless={config.HEADLESS})")
    
    yield browser
    
    browser.close()
    logger.info("浏览器已关闭")


@pytest.fixture(scope="function")
def page(browser):
    """页面函数级夹具"""
    context = browser.new_context(
        viewport={
            "width": config.VIEWPORT_WIDTH,
            "height": config.VIEWPORT_HEIGHT
        },
        ignore_https_errors=True
    )
    page = context.new_page()
    page.set_default_timeout(config.DEFAULT_TIMEOUT)
    
    yield page
    
    page.close()
    context.close()


@pytest.fixture(scope="session")
def test_data():
    """测试数据夹具"""
    return TEST_DATA


@pytest.fixture(scope="session")
def login_data(test_data):
    """登录测试数据"""
    return test_data.get("login", {})


@pytest.fixture(scope="session")
def supplier_data(test_data):
    """供应商测试数据"""
    return test_data.get("suppliers", {})


@pytest.fixture(scope="session")
def customer_data(test_data):
    """客户测试数据"""
    return test_data.get("customers", {})


@pytest.fixture(scope="session")
def product_data(test_data):
    """商品测试数据"""
    return test_data.get("products", {})


@pytest.fixture(scope="function")
def login_page(page):
    """登录页面夹具"""
    from pages.login_page import LoginPage
    return LoginPage(page)


@pytest.fixture(scope="function")
def dashboard_page(page):
    """仪表盘页面夹具"""
    from pages.dashboard_page import DashboardPage
    return DashboardPage(page)


@pytest.fixture(scope="function")
def supplier_page(page):
    """供应商页面夹具"""
    from pages.supplier_page import SupplierPage
    return SupplierPage(page)


@pytest.fixture(scope="function")
def customer_page(page):
    """客户页面夹具"""
    from pages.customer_page import CustomerPage
    return CustomerPage(page)


@pytest.fixture(scope="function")
def product_page(page):
    """商品页面夹具"""
    from pages.product_page import ProductPage
    return ProductPage(page)


@pytest.fixture(scope="function")
def logged_in_page(page, login_page):
    """已登录状态的页面夹具"""
    login_page.login(config.ADMIN_USERNAME, config.ADMIN_PASSWORD)
    login_page.verify_login_success()
    yield page


# ==================== pytest Hooks ====================
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试失败时自动截图"""
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call" and rep.failed:
        page = item.funcargs.get("page")
        if page:
            try:
                from utils import take_screenshot
                take_screenshot(page, item.name)
            except Exception as e:
                logger.error(f"截图失败: {e}")


def pytest_configure(config):
    """配置 pytest"""
    config.addinivalue_line(
        "markers",
        "smoke: Smoke test cases"
    )
    config.addinivalue_line(
        "markers",
        "data_driven: Data-driven test cases"
    )


def pytest_html_report_title(report):
    """设置 HTML 报告标题"""
    report.title = "ERP 自动化测试报告"


def pytest_html_results_summary(prefix, summary, postfix):
    """HTML 报告摘要信息"""
    prefix.extend([
        f"平台地址: {config.BASE_URL}",
        f"浏览器: {config.BROWSER}",
        f"环境: {config.ENV}",
    ])
