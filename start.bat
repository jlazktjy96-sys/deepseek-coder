@echo off
echo =========================================
echo DeepSeek源码生成器启动器
echo GitHub: https://github.com/jlazktjy96-sys/deepseek-coder
echo =========================================
echo.

REM 检查是否在正确的目录
if exist "deepseek_coder.py" (
    goto :RUN_APP
)

REM 尝试查找安装目录
if exist "%USERPROFILE%\.deepseek-coder\deepseek_coder.py" (
    cd /d "%USERPROFILE%\.deepseek-coder"
    goto :RUN_APP
)

if exist "%USERPROFILE%\DeepSeekCoder\deepseek_coder.py" (
    cd /d "%USERPROFILE%\DeepSeekCoder"
    goto :RUN_APP
)

echo ❌ 未找到DeepSeek源码生成器
echo.
echo 请先运行安装脚本：
echo 1. 下载 install.bat
echo 2. 双击运行 install.bat
echo.
echo 或从GitHub下载：
echo https://github.com/jlazktjy96-sys/deepseek-coder
echo.
pause
exit /b 1

:RUN_APP
echo ✅ 找到程序文件
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Python
    echo 请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM 检查依赖
echo 🔍 检查依赖包...
pip list | findstr requests >nul
if errorlevel 1 (
    echo 📦 安装依赖包...
    pip install requests python-dotenv -i https://pypi.tuna.tsinghua.edu.cn/simple
)

echo.
echo 🤖 DeepSeek源码生成器 v1.0
echo 📝 输入需求，生成完整项目代码
echo.

if "%1"=="" (
    echo 📋 使用方法：
    echo   配置API密钥: deepseek-coder config 您的API密钥
    echo   创建项目: deepseek-coder create "项目需求描述"
    echo   查看帮助: deepseek-coder help
    echo.
    echo 💡 示例：
    echo   deepseek-coder create "创建一个TODO应用"
    echo   deepseek-coder create "数据分析脚本" -n analysis -l python
    echo.
    pause
) else (
    python deepseek_coder.py %*
)