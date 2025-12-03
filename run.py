#!/usr/bin/env python3
"""
启动PDF提取工具的脚本
"""
import os
import sys
import subprocess

def main():
    # 检查依赖
    try:
        import streamlit
    except ImportError:
        print("正在安装依赖包...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # 启动Streamlit应用
    os.system("streamlit run app.py")

if __name__ == "__main__":
    main()