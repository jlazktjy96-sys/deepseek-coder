#!/usr/bin/env python3
"""
DeepSeek源码生成器 v1.0
GitHub: https://github.com/jlazktjy96-sys/deepseek-coder
输入自然语言需求，生成完整项目代码
"""

import os
import sys
import json
import requests
import argparse
import shutil
from pathlib import Path
from datetime import datetime
import re

def load_config():
    """加载配置文件"""
    config_paths = [
        ".env",
        os.path.expanduser("~/.deepseek-coder/.env"),
        os.path.expanduser("~/.deepseek_coder_env")
    ]
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if api_key:
        return api_key
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip() and not line.startswith('#'):
                            if '=' in line:
                                key, value = line.strip().split('=', 1)
                                if key.strip() == 'DEEPSEEK_API_KEY':
                                    api_key = value.strip().strip('"\'')
                                    return api_key
            except:
                continue
    
    return None

def save_config(api_key):
    """保存API密钥"""
    config_dir = os.path.expanduser("~/.deepseek-coder")
    os.makedirs(config_dir, exist_ok=True)
    
    config_file = os.path.join(config_dir, ".env")
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(f'DEEPSEEK_API_KEY={api_key}\n')
    
    return config_file

def call_deepseek_api(prompt, api_key, model="deepseek-chat", max_tokens=4000):
    """调用DeepSeek API"""
    if not api_key:
        return "❌ 错误：未设置API密钥"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "stream": False
    }
    
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        elif response.status_code == 401:
            return "❌ 错误：API密钥无效"
        elif response.status_code == 429:
            return "❌ 错误：请求过于频繁，请稍后再试"
        else:
            return f"❌ 错误：API返回状态码 {response.status_code}"
            
    except requests.exceptions.Timeout:
        return "❌ 错误：请求超时"
    except requests.exceptions.ConnectionError:
        return "❌ 错误：网络连接失败"
    except Exception as e:
        return f"❌ 错误：{str(e)}"

def generate_project_structure(prompt, project_name, language="python"):
    """生成项目结构"""
    structure_prompt = f"""请为以下需求设计完整的项目结构：

项目名称：{project_name}
编程语言：{language}
需求描述：{prompt}

请提供以下内容：
1. 项目目录结构（树状格式）
2. 主要文件及其功能说明
3. 建议的技术栈和依赖包

请使用中文回复，格式清晰易读。"""
    
    return structure_prompt

def generate_file_content(prompt, file_path, project_name, language="python"):
    """生成单个文件内容"""
    file_prompt = f"""请为以下项目需求编写 {file_path} 文件：

项目名称：{project_name}
编程语言：{language}
文件路径：{file_path}
项目需求：{prompt}

要求：
1. 生成完整、可直接运行的代码
2. 包含详细的注释
3. 实现错误处理
4. 遵循最佳实践
5. 如果是配置文件，请提供完整的配置示例

请只返回代码内容，不要额外解释。"""
    
    return file_prompt

def create_project(prompt, project_name, api_key, language="python"):
    """创建完整项目"""
    print(f"\n{'='*60}")
    print(f"🚀 开始生成项目：{project_name}")
    print(f"📝 需求描述：{prompt}")
    print(f"💻 编程语言：{language}")
    print(f"{'='*60}")
    
    # 创建项目目录
    project_path = Path(project_name)
    if project_path.exists():
        print(f"⚠️  目录已存在：{project_name}")
        choice = input("是否覆盖？(y/n): ").lower()
        if choice != 'y':
            print("❌ 操作取消")
            return None
    
    project_path.mkdir(exist_ok=True)
    
    # 1. 生成项目结构说明
    print("\n📂 生成项目结构...")
    structure_prompt = generate_project_structure(prompt, project_name, language)
    structure = call_deepseek_api(structure_prompt, api_key)
    
    with open(project_path / "PROJECT_STRUCTURE.md", "w", encoding="utf-8") as f:
        f.write(f"# {project_name} - 项目结构\n\n")
        f.write(structure)
    
    print("✅ 项目结构生成完成")
    
    # 2. 生成主文件（根据语言决定文件名）
    main_files = {
        "python": "main.py",
        "javascript": "index.js",
        "java": "src/main/java/Main.java",
        "go": "main.go",
        "php": "index.php"
    }
    
    main_file = main_files.get(language, "main.py")
    main_path = project_path / main_file
    
    print(f"\n📄 生成主文件：{main_file}")
    main_prompt = generate_file_content(prompt, main_file, project_name, language)
    main_code = call_deepseek_api(main_prompt, api_key)
    
    main_path.parent.mkdir(parents=True, exist_ok=True)
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(main_code)
    
    print("✅ 主文件生成完成")
    
    # 3. 生成README文档
    print("\n📚 生成项目文档...")
    readme_prompt = f"""请为以下项目编写完整的README.md文档：

项目名称：{project_name}
编程语言：{language}
项目需求：{prompt}
项目结构：{structure[:500]}...

请包含以下部分：
1. 项目简介
2. 功能特性
3. 安装部署
4. 使用说明
5. 配置说明
6. API文档（如果有）
7. 贡献指南
8. 许可证信息

请使用中文编写，格式规范。"""
    
    readme_content = call_deepseek_api(readme_prompt, api_key)
    
    with open(project_path / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✅ 项目文档生成完成")
    
    # 4. 生成配置文件
    print("\n⚙️  生成配置文件...")
    
    # 根据语言生成不同的配置文件
    configs = []
    
    if language == "python":
        configs.append(("requirements.txt", "Python依赖包"))
        configs.append((".gitignore", "Git忽略文件"))
        configs.append(("setup.py", "Python包配置"))
    elif language == "javascript":
        configs.append(("package.json", "Node.js包配置"))
        configs.append((".gitignore", "Git忽略文件"))
    elif language == "java":
        configs.append(("pom.xml", "Maven配置"))
        configs.append((".gitignore", "Git忽略文件"))
    
    for config_file, description in configs:
        config_prompt = f"""请为{language}项目生成{config_file}文件。
项目名称：{project_name}
需求：{prompt}

{description}，请提供完整的配置内容。"""
        
        config_content = call_deepseek_api(config_prompt, api_key, max_tokens=2000)
        
        config_path = project_path / config_file
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(config_content)
        
        print(f"  ✅ 生成：{config_file}")
    
    # 5. 显示项目信息
    print(f"\n{'='*60}")
    print(f"🎉 项目生成完成！")
    print(f"📁 项目路径：{project_path.absolute()}")
    print(f"{'='*60}")
    
    # 显示项目树状结构
    print("\n📂 项目结构：")
    display_project_tree(project_path)
    
    return project_path

def display_project_tree(path, prefix=""):
    """显示项目树状结构"""
    try:
        items = sorted(os.listdir(path))
        for i, item in enumerate(items):
            item_path = os.path.join(path, item)
            is_last = (i == len(items) - 1)
            
            if os.path.isdir(item_path):
                print(f"{prefix}{'└── ' if is_last else '├── '}{item}/")
                new_prefix = prefix + ("    " if is_last else "│   ")
                display_project_tree(item_path, new_prefix)
            else:
                ext = os.path.splitext(item)[1]
                if ext == '.py':
                    print(f"{prefix}{'└── ' if is_last else '├── '}{item}")
                elif ext == '.md':
                    print(f"{prefix}{'└── ' if is_last else '├── '}{item}")
                else:
                    print(f"{prefix}{'└── ' if is_last else '├── '}{item}")
    except Exception as e:
        print(f"  无法显示目录结构：{str(e)}")

def main():
    """命令行主函数"""
    parser = argparse.ArgumentParser(
        description="DeepSeek源码生成器 - 输入需求，生成完整项目代码",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例：
  %(prog)s config sk-xxxxxxxxxxxxxxxxxxxx   # 配置API密钥
  %(prog)s create "创建一个Flask网站"       # 创建项目
  %(prog)s create "数据分析脚本" -n analysis -l python  # 创建Python项目
  
获取API密钥：https://platform.deepseek.com/api_keys
GitHub仓库：https://github.com/jlazktjy96-sys/deepseek-coder"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # 创建项目命令
    create_parser = subparsers.add_parser("create", help="创建新项目")
    create_parser.add_argument("prompt", help="项目需求描述")
    create_parser.add_argument("-n", "--name", default="my_project", help="项目名称")
    create_parser.add_argument("-l", "--language", default="python", 
                              choices=["python", "javascript", "java", "go", "php", "csharp"],
                              help="编程语言")
    
    # 配置命令
    config_parser = subparsers.add_parser("config", help="配置API密钥")
    config_parser.add_argument("api_key", help="DeepSeek API密钥")
    
    # 帮助命令
    subparsers.add_parser("help", help="显示帮助信息")
    
    # 如果没有参数，显示帮助
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    
    args = parser.parse_args()
    
    # 显示标题
    print("\n" + "="*60)
    print("🤖 DeepSeek源码生成器 v1.0")
    print("="*60)
    
    if args.command == "config":
        config_file = save_config(args.api_key)
        print(f"✅ API密钥已保存到：{config_file}")
        print("🔑 现在可以开始创建项目了！")
        
    elif args.command == "create":
        api_key = load_config()
        
        if not api_key:
            print("❌ 未找到API密钥")
            print("\n请先配置API密钥：")
            print("  deepseek-coder config 您的API密钥")
            print("\n或设置环境变量：")
            print("  set DEEPSEEK_API_KEY=您的API密钥")
            print("\n获取API密钥：https://platform.deepseek.com/api_keys")
            sys.exit(1)
        
        # 测试API密钥
        print("🔍 验证API密钥...")
        test_result = call_deepseek_api("测试连接", api_key, max_tokens=10)
        
        if "❌ 错误" in test_result:
            print(f"❌ API密钥验证失败：{test_result}")
            print("请检查API密钥是否正确，或重新配置：deepseek-coder config 新密钥")
            sys.exit(1)
        
        print("✅ API密钥验证成功")
        
        # 创建项目
        project_path = create_project(args.prompt, args.name, api_key, args.language)
        
        if project_path:
            print("\n📋 下一步：")
            print(f"  1. 进入项目目录：cd {args.name}")
            
            if args.language == "python":
                print("  2. 安装依赖：pip install -r requirements.txt")
                print("  3. 运行项目：python main.py")
            elif args.language == "javascript":
                print("  2. 安装依赖：npm install")
                print("  3. 运行项目：npm start")
            
            print(f"\n💡 提示：生成的代码可能需要微调才能运行")
        
    elif args.command == "help":
        parser.print_help()
        print("\n📖 详细说明：")
        print("  1. 首先获取DeepSeek API密钥")
        print("  2. 使用 config 命令配置密钥")
        print("  3. 使用 create 命令创建项目")
        print("  4. 根据需要修改生成的代码")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()