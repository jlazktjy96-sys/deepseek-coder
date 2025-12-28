@echo off
echo =========================================
echo DeepSeek源码生成器 - 一键安装脚本
echo GitHub: https://github.com/jlazktjy96-sys/deepseek-coder
echo =========================================
echo.

setlocal enabledelayedexpansion

REM 检查管理员权限（可选）
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  建议以管理员身份运行此脚本
    echo 右键 -> 以管理员身份运行
    echo.
)

REM 设置GitHub信息
set "GITHUB_USER=jlazktjy96-sys"
set "REPO_NAME=deepseek-coder"
set "BRANCH=main"
set "BASE_URL=https://raw.githubusercontent.com/%GITHUB_USER%/%REPO_NAME%/%BRANCH%"

REM 设置安装目录
set "INSTALL_DIR=%USERPROFILE%\.deepseek-coder"
set "APP_DIR=%USERPROFILE%\DeepSeekCoder"

echo 📁 系统安装目录: %INSTALL_DIR%
echo 📁 应用运行目录: %APP_DIR%
echo.

REM 步骤1：检查Python
echo 🔍 步骤1/5：检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未检测到Python
    echo.
    echo 请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    echo.
    echo 安装时请务必勾选:
    echo   ☑️ Add Python to PATH
    echo   ☑️ Install for all users
    echo.
    echo 安装完成后重新运行此脚本
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
echo ✅ Python已安装: !PYTHON_VERSION!
echo.

REM 步骤2：创建目录
echo 📁 步骤2/5：创建目录结构...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%APP_DIR%" mkdir "%APP_DIR%"
cd /d "%INSTALL_DIR%"

echo ✅ 目录创建完成
echo.

REM 步骤3：下载核心文件
echo 📥 步骤3/5：下载核心文件...
echo.

echo 📄 下载主程序...
powershell -Command "try {Invoke-WebRequest -Uri '%BASE_URL%/deepseek_coder.py' -OutFile 'deepseek_coder.py' -ErrorAction Stop; echo '  ✅ 下载成功'} catch {echo '  ❌ 下载失败'}"
if not exist "deepseek_coder.py" (
    echo ❌ 主程序下载失败，使用备用源...
    call :CREATE_LOCAL_FILES
)

echo 📄 下载配置文件...
powershell -Command "try {Invoke-WebRequest -Uri '%BASE_URL%/.env.example' -OutFile '.env.example' -ErrorAction Stop; echo '  ✅ 下载成功'} catch {echo '  ❌ 下载失败'}"

echo 📄 下载依赖配置...
powershell -Command "try {Invoke-WebRequest -Uri '%BASE_URL%/requirements.txt' -OutFile 'requirements.txt' -ErrorAction Stop; echo '  ✅ 下载成功'} catch {echo '  ❌ 下载失败'}"

echo ✅ 文件下载完成
echo.

REM 步骤4：安装依赖
echo 📦 步骤4/5：安装Python依赖...
echo 🔧 更新pip...
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

echo 📦 安装依赖包...
pip install requests python-dotenv -i https://pypi.tuna.tsinghua.edu.cn/simple

if exist "requirements.txt" (
    echo 📦 安装额外依赖...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
)

echo ✅ 依赖安装完成
echo.

REM 步骤5：创建快捷命令
echo 🔧 步骤5/5：创建系统命令...
echo.

REM 创建批处理文件
(
echo @echo off
echo setlocal enabledelayedexpansion
echo.
echo REM DeepSeek源码生成器命令
echo REM GitHub: https://github.com/jlazktjy96-sys/deepseek-coder
echo.
echo set "SCRIPT_DIR=%INSTALL_DIR%"
echo.
echo REM 检查Python
echo python --version ^>nul 2^>^&1
echo if errorlevel 1 (
echo     echo ❌ 未检测到Python，请先安装Python 3.8+
echo     echo 下载地址: https://www.python.org/downloads/
echo     pause
echo     exit /b 1
echo )
echo.
echo REM 运行主程序
echo python "%SCRIPT_DIR%\deepseek_coder.py" %%*
echo.
echo REM 如果直接双击运行，则暂停
echo if "%%1"=="" pause
) > deepseek-coder.bat

REM 复制到用户应用目录
copy deepseek-coder.bat "%APP_DIR%\deepseek-coder.bat" >nul 2>&1

REM 添加到用户PATH
echo 🔧 添加到系统PATH...
set "USER_PATH_REG=HKCU\Environment"
reg query "%USER_PATH_REG%" /v Path | findstr /i "%INSTALL_DIR%" >nul
if errorlevel 1 (
    for /f "tokens=2*" %%A in ('reg query "%USER_PATH_REG%" /v Path 2^>nul ^| findstr /i "Path"') do set "CURRENT_PATH=%%B"
    if "!CURRENT_PATH!"=="" (
        set "NEW_PATH=%INSTALL_DIR%"
    ) else (
        set "NEW_PATH=!CURRENT_PATH!;%INSTALL_DIR%"
    )
    reg add "%USER_PATH_REG%" /v Path /t REG_EXPAND_SZ /d "!NEW_PATH!" /f >nul 2>&1
    echo ✅ 已添加到用户PATH
) else (
    echo ✅ 已在PATH中
)

REM 创建桌面快捷方式
echo 📋 创建桌面快捷方式...
(
echo Set oWS = WScript.CreateObject("WScript.Shell")
echo sLinkFile = "%USERPROFILE%\Desktop\DeepSeek源码生成器.lnk"
echo Set oLink = oWS.CreateShortcut(sLinkFile)
echo oLink.TargetPath = "%APP_DIR%\deepseek-coder.bat"
echo oLink.WorkingDirectory = "%APP_DIR%"
echo oLink.Description = "DeepSeek源码生成器"
echo oLink.IconLocation = "%SystemRoot%\System32\SHELL32.dll,21"
echo oLink.Save
) > "%TEMP%\create_shortcut.vbs"
cscript //nologo "%TEMP%\create_shortcut.vbs" >nul
del "%TEMP%\create_shortcut.vbs" >nul 2>&1

echo ✅ 桌面快捷方式已创建
echo.

echo =========================================
echo 🎉 安装完成！
echo =========================================
echo.
echo 📋 使用说明：
echo 1. 配置API密钥：
echo    打开CMD，运行: deepseek-coder config 您的API密钥
echo.
echo 2. 创建项目：
echo    deepseek-coder create "项目需求描述"
echo    示例: deepseek-coder create "创建一个Flask网站"
echo.
echo 3. 高级选项：
echo    deepseek-coder create "需求" -n 项目名 -l 语言
echo    示例: deepseek-coder create "数据分析" -n analysis -l python
echo.
echo 4. 获取API密钥：
echo    https://platform.deepseek.com/api_keys
echo.
echo 💡 提示：
echo   - 如果命令无法运行，请重新打开CMD窗口
echo   - 项目默认生成在: %APP_DIR%
echo   - 桌面已有快捷方式
echo.
echo 🔗 GitHub仓库：
echo   https://github.com/jlazktjy96-sys/deepseek-coder
echo.
echo 按任意键退出...
pause >nul
exit /b 0

:CREATE_LOCAL_FILES
echo ⚠️  创建本地版本文件...
(
echo import os
echo import sys
echo import requests
echo 
echo print("DeepSeek源码生成器 - 本地版")
echo print("请访问GitHub获取完整版本")
echo print("https://github.com/jlazktjy96-sys/deepseek-coder")
) > deepseek_coder.py
exit /b