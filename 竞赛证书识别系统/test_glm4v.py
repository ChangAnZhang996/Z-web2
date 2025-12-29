"""
测试GLM-4V API配置和连接
运行: python test_glm4v.py
"""
from __future__ import annotations

import os
from glm4v_api import load_api_key, test_api_connection

def main():
    print("=" * 50)
    print("GLM-4V API 配置测试")
    print("=" * 50)
    
    # 检查API Key
    api_key = load_api_key()
    if api_key:
        print(f"✓ API Key已配置: {api_key[:10]}...{api_key[-5:]}")
    else:
        print("✗ API Key未配置")
        print("\n请设置环境变量 GLM4V_API_KEY 或创建 .env 文件")
        print("示例：")
        print("  Windows PowerShell: $env:GLM4V_API_KEY='sk-your-key'")
        print("  Linux/Mac: export GLM4V_API_KEY='sk-your-key'")
        return
    
    # 测试连接
    print("\n测试API连接...")
    if test_api_connection(api_key):
        print("✓ API连接测试通过（基础检查）")
    else:
        print("✗ API连接测试失败")
    
    print("\n" + "=" * 50)
    print("提示：")
    print("1. 确保API Key有效且未过期")
    print("2. 检查网络连接")
    print("3. 查看智谱AI平台API文档：https://open.bigmodel.cn/dev/api")
    print("=" * 50)

if __name__ == "__main__":
    main()


