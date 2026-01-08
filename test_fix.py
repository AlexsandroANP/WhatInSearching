"""
测试脚本：验证 config.PROMPTS 访问修复

此脚本用于验证修复后的 config.PROMPTS 访问方式是否正确，
确保不再出现 'module' object is not subscriptable 错误。
"""

import sys
import os

# 添加当前目录到 Python 路径，确保可以导入模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config


def test_prompts_access():
    """测试通过点号访问 config.PROMPTS 中的属性"""
    print("=== 测试 config.PROMPTS 访问方式 ===")
    
    try:
        # 测试通过点号访问（正确方式）
        user_prompt = config.current_config.PROMPTS.AI_DEFAULT_USER_PROMPT
        placeholder = config.current_config.PROMPTS.AI_DEFAULT_TABLE_CONTENT_PLACEHOLDER
        system_prompt = config.current_config.PROMPTS.AI_DEFAULT_SYSTEM_PROMPT
        
        print("✅ 成功通过点号访问 config.PROMPTS 中的属性")
        print(f"  - AI_DEFAULT_USER_PROMPT: {user_prompt[:50]}...")
        print(f"  - AI_DEFAULT_TABLE_CONTENT_PLACEHOLDER: {placeholder}")
        print(f"  - AI_DEFAULT_SYSTEM_PROMPT: {system_prompt[:50]}...")
        
    except Exception as e:
        print(f"❌ 通过点号访问时出错: {type(e).__name__}: {e}")
        return False
    
    try:
        # 测试通过方括号访问（应该失败，用于验证错误处理）
        user_prompt_error = config.current_config.PROMPTS["AI_DEFAULT_USER_PROMPT"]
        print("❌ 意外：通过方括号访问竟然成功了，这不符合预期")
        return False
    except TypeError as e:
        print(f"✅ 预期行为：通过方括号访问失败，错误信息: {type(e).__name__}: {e}")
    except Exception as e:
        print(f"⚠️  通过方括号访问时出现非预期错误: {type(e).__name__}: {e}")
    
    return True


def test_global_trends_analyzer_import():
    """测试导入 global_trends_analyzer 模块，验证修复是否解决了导入错误"""
    print("\n=== 测试导入 global_trends_analyzer 模块 ===")
    
    try:
        import global_trends_analyzer
        print("✅ 成功导入 global_trends_analyzer 模块，修复有效！")
        return True
    except Exception as e:
        print(f"❌ 导入 global_trends_analyzer 模块时出错: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("开始测试 config.PROMPTS 访问修复...\n")
    
    # 运行测试
    test1_passed = test_prompts_access()
    test2_passed = test_global_trends_analyzer_import()
    
    print("\n=== 测试结果汇总 ===")
    print(f"测试 1 (点号访问): {'通过' if test1_passed else '失败'}")
    print(f"测试 2 (模块导入): {'通过' if test2_passed else '失败'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 所有测试通过！修复成功！")
        print("你现在可以正常使用 global_trends_analyzer.py 文件了。")
    else:
        print("\n❌ 测试失败，修复可能不完整。")
        sys.exit(1)
