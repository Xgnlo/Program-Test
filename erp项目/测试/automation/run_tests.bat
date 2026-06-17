@echo off
chcp 65001 >nul
REM ==============================================================
REM Playwright + Pytest 自动化测试一键执行脚本
REM 使用方法：双击或在 cmd 中执行 run_tests.bat
REM 运行前请先启动 ERP 平台：cd ..\..\平台 && python app.py
REM ==============================================================

setlocal
set "TEST_DIR=%~dp0"
set "REPORT_DIR=%TEST_DIR%reports"
set "PLATE_DIR=%~dp0..\..\平台"

if not exist "%REPORT_DIR%" mkdir "%REPORT_DIR%"

echo.
echo ============================================
echo   Playwright + Pytest 自动化测试套件
echo ============================================
echo.
echo [提示] 请确保 ERP 平台已启动 (http://127.0.0.1:5000)
echo        如需启动平台，请另开终端执行: cd %PLATE_DIR% && python app.py
echo.

:menu
echo ------------------------------------------------------------
echo 请选择要运行的测试:
echo   1. 安装依赖并初始化 Playwright
echo   2. 运行所有测试
echo   3. 运行登录测试 (test_login.py)
echo   4. 运行供应商测试 (test_supplier.py)
echo   5. 运行客户测试 (test_customer.py)
echo   6. 运行商品测试 (test_product.py)
echo   7. 仅列出测试用例（不执行）
echo   8. 退出
echo ------------------------------------------------------------
set /p "choice=请输入选择 [1-8]: "

if "%choice%"=="1" goto install
if "%choice%"=="2" goto all
if "%choice%"=="3" goto login
if "%choice%"=="4" goto supplier
if "%choice%"=="5" goto customer
if "%choice%"=="6" goto product
if "%choice%"=="7" goto collect
if "%choice%"=="8" goto end

echo 无效的选项，请重新输入。
goto menu

:install
echo.
echo [开始] 安装依赖...
cd /d "%TEST_DIR%"
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
echo.
echo [开始] 初始化 Playwright...
playwright install chromium
echo.
echo [完成] 依赖安装完成
goto menu

:all
echo.
echo [开始] 运行所有测试...
cd /d "%TEST_DIR%"
python -m pytest tests/ -v --html="%REPORT_DIR%\all_report.html" --self-contained-html
echo.
echo [完成] 测试报告: %REPORT_DIR%\all_report.html
goto menu

:login
echo.
echo [开始] 运行登录测试...
cd /d "%TEST_DIR%"
python -m pytest tests/test_login.py -v --html="%REPORT_DIR%\login_report.html" --self-contained-html
echo.
echo [完成] 登录测试报告: %REPORT_DIR%\login_report.html
goto menu

:supplier
echo.
echo [开始] 运行供应商测试...
cd /d "%TEST_DIR%"
python -m pytest tests/test_supplier.py -v --html="%REPORT_DIR%\supplier_report.html" --self-contained-html
echo.
echo [完成] 供应商测试报告: %REPORT_DIR%\supplier_report.html
goto menu

:customer
echo.
echo [开始] 运行客户测试...
cd /d "%TEST_DIR%"
python -m pytest tests/test_customer.py -v --html="%REPORT_DIR%\customer_report.html" --self-contained-html
echo.
echo [完成] 客户测试报告: %REPORT_DIR%\customer_report.html
goto menu

:product
echo.
echo [开始] 运行商品测试...
cd /d "%TEST_DIR%"
python -m pytest tests/test_product.py -v --html="%REPORT_DIR%\product_report.html" --self-contained-html
echo.
echo [完成] 商品测试报告: %REPORT_DIR%\product_report.html
goto menu

:collect
echo.
echo [收集] 测试用例清单:
cd /d "%TEST_DIR%"
python -m pytest tests/ --collect-only -q
goto menu

:end
echo.
echo 测试结束，再见。
endlocal
pause