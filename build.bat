@echo off
chcp 65001 >nul
echo ================================
echo  密码生成与管理器 - 打包脚本
echo ================================

set PYTHON_DIR=%LOCALAPPDATA%\Programs\Python\Python312
set PATH=%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%PATH%

echo.
echo [1] 单文件模式 (推荐, 约 40MB, 便携)
echo [2] 多文件模式 (主程序 2MB, 总文件夹约 100MB)
echo.
set /p MODE="请选择打包模式 (1/2): "

if "%MODE%"=="1" (
    echo 正在打包单文件模式...
    pyinstaller --onefile --windowed --name "密码生成与管理器" --icon "resources/icon.ico" --add-data "app;app" --add-data "ui;ui" --add-data "resources;resources" --exclude-module numpy --exclude-module pandas --exclude-module matplotlib --exclude-module pygame --exclude-module PIL --exclude-module tkinter --exclude-module unittest --exclude-module pydoc --exclude-module multiprocessing --exclude-module concurrent --noconfirm main.py
) else if "%MODE%"=="2" (
    echo 正在打包多文件模式...
    pyinstaller --onedir --windowed --name "密码生成与管理器" --icon "resources/icon.ico" --add-data "app;app" --add-data "ui;ui" --add-data "resources;resources" --exclude-module numpy --exclude-module pandas --exclude-module matplotlib --exclude-module pygame --exclude-module PIL --exclude-module tkinter --exclude-module unittest --exclude-module pydoc --exclude-module multiprocessing --exclude-module concurrent --noconfirm main.py
) else (
    echo 无效选择，退出。
    pause
    exit /b
)

if %errorlevel% equ 0 (
    echo.
    echo 打包成功！输出在 dist\ 目录
) else (
    echo.
    echo 打包失败，请检查错误信息
)

pause
