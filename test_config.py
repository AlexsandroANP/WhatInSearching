#!/usr/bin/env python3
"""
配置测试脚本，用于验证配置文件是否正常工作
"""

import os
import sys

# 确保可以导入当前目录的模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_import():
    """测试导入配置模块"""
    print("测试导入配置模块...")
    try:
        from config import Config, DevelopmentConfig, ProductionConfig, get_config
        print("✅ 成功导入配置模块")
        return True
    except Exception as e:
        print(f"❌ 导入配置模块失败: {e}")
        return False

def test_prompts_config():
    """测试提示词配置是否正确"""
    print("\n测试提示词配置...")
    try:
        from config import get_config
        config = get_config()
        
        # 检查是否有PROMPTS配置
        if hasattr(config, 'PROMPTS'):
            print("✅ 配置中包含PROMPTS属性")
            
            # 检查几个关键的提示词
            required_prompts = [
                "LOG_FETCH_START",
                "LOG_FETCH_SUCCESS",
                "AI_DEFAULT_SYSTEM_PROMPT"
            ]
            
            for prompt_key in required_prompts:
                if prompt_key in config.PROMPTS:
                    print(f"✅ 包含提示词: {prompt_key}")
                else:
                    print(f"❌ 缺少提示词: {prompt_key}")
            
            return True
        else:
            print("❌ 配置中没有PROMPTS属性")
            return False
    except Exception as e:
        print(f"❌ 测试提示词配置失败: {e}")
        return False

def test_env_config():
    """测试环境变量配置"""
    print("\n测试环境变量配置...")
    try:
        from credentials import MODEL_API_KEY, MODEL_API_ENDPOINT, MODEL_NAME
        print(f"✅ 成功导入凭证: {MODEL_API_KEY}, {MODEL_API_ENDPOINT}, {MODEL_NAME}")
        return True
    except Exception as e:
        print(f"❌ 测试环境变量配置失败: {e}")
        return False

def test_streamlit_ai_import():
    """测试streamlit_AI.py是否能正确导入配置"""
    print("\n测试streamlit_AI.py导入配置...")
    try:
        # 测试导入streamlit_AI模块
        import streamlit_AI
        print("✅ streamlit_AI模块导入成功")
        return True
    except Exception as e:
        print(f"❌ streamlit_AI模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== 配置验证测试 ===")
    
    # 运行所有测试
    results = [
        test_config_import(),
        test_prompts_config(),
        test_env_config(),
        test_streamlit_ai_import()
    ]
    
    print("\n=== 测试结果 ===")
    if all(results):
        print("✅ 所有测试通过！配置系统工作正常。")
        sys.exit(0)
    else:
        print("❌ 部分测试失败，请检查配置文件。")
        sys.exit(1)
