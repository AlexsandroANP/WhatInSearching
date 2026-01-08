import sys
import os

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from global_trends_analyzer import estimate_tokens

def test_token_estimation():
    """测试 token 估算功能"""
    print("=== 测试 token 估算功能 ===")
    
    # 测试文本
    test_texts = [
        "Hello, world!",
        "这是一个测试文本，用于测试 token 估算功能。",
        "This is a longer test text to verify token estimation works correctly for English text.",
        "这是一个更长的测试文本，用于验证中文文本的 token 估算是否正确工作。" * 10,
    ]
    
    # 测试模型
    test_models = ["gpt-4o", "gpt-3.5-turbo"]
    
    for model in test_models:
        print(f"\n--- 测试模型: {model} ---")
        for i, text in enumerate(test_texts):
            try:
                tokens = estimate_tokens(text, model)
                print(f"文本 {i+1}: {len(text)} 字符 -> {tokens} tokens")
            except Exception as e:
                print(f"文本 {i+1}: 估算失败 - {e}")

def test_token_counting_logic():
    """测试 token 累计逻辑"""
    print("\n=== 测试 token 累计逻辑 ===")
    
    # 模拟初始 token 数量
    initial_system_prompt = "You are a helpful assistant."
    initial_user_prompt = "Analyze the following data: ..."
    
    # 模拟后续对话
    follow_up_user_message = "What are the key insights?"
    follow_up_ai_response = "The key insights are: 1. ... 2. ... 3. ..."
    
    try:
        # 计算初始 token
        system_tokens = estimate_tokens(initial_system_prompt, "gpt-4o")
        user_tokens = estimate_tokens(initial_user_prompt, "gpt-4o")
        initial_total = system_tokens + user_tokens
        
        print(f"初始系统提示词: {system_tokens} tokens")
        print(f"初始用户输入: {user_tokens} tokens")
        print(f"初始总计: {initial_total} tokens")
        
        # 计算后续对话 token
        follow_up_user_tokens = estimate_tokens(follow_up_user_message, "gpt-4o")
        follow_up_ai_tokens = estimate_tokens(follow_up_ai_response, "gpt-4o")
        follow_up_total = follow_up_user_tokens + follow_up_ai_tokens
        
        print(f"\n后续用户消息: {follow_up_user_tokens} tokens")
        print(f"后续 AI 回复: {follow_up_ai_tokens} tokens")
        print(f"后续总计: {follow_up_total} tokens")
        
        # 计算累计 token
        cumulative_total = initial_total + follow_up_total
        print(f"\n累计总计: {cumulative_total} tokens")
        
        return True
    except Exception as e:
        print(f"测试失败: {e}")
        return False

if __name__ == "__main__":
    test_token_estimation()
    success = test_token_counting_logic()
    
    if success:
        print("\n✅ 所有测试通过！")
    else:
        print("\n❌ 测试失败！")
        sys.exit(1)
