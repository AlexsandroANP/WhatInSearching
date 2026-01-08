"""
测试配置模块是否正常工作
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import current_config

print("测试配置模块加载...")

# 测试基本配置访问
print(f"DEBUG: {current_config.DEBUG}")
print(f"LOG_LEVEL: {current_config.LOG_LEVEL}")
print(f"OUTPUT_DIR: {current_config.OUTPUT_DIR}")

# 测试区域配置
print(f"\n区域配置数量: {len(current_config.REGIONS)}")
print(f"第一个区域: {list(current_config.REGIONS.keys())[0]}")

# 测试提示词访问
print("\n测试提示词访问...")
print(f"提示词模块是否可用: {hasattr(current_config, 'PROMPTS')}")

if hasattr(current_config, 'PROMPTS'):
    # 测试访问具体提示词
    if hasattr(current_config.PROMPTS, 'LOG_FETCH_START'):
        print(f"LOG_FETCH_START: {current_config.PROMPTS.LOG_FETCH_START}")
    else:
        print("无法访问LOG_FETCH_START")
    
    if hasattr(current_config.PROMPTS, 'AI_DEFAULT_USER_PROMPT'):
        print(f"AI_DEFAULT_USER_PROMPT: {current_config.PROMPTS.AI_DEFAULT_USER_PROMPT}")
    else:
        print("无法访问AI_DEFAULT_USER_PROMPT")
    
    # 测试修改后的变量名
    if hasattr(current_config.PROMPTS, 'INDIA_TRENDS_SYSTEM_PROMPT'):
        print("INDIA_TRENDS_SYSTEM_PROMPT: 已成功修改")
    else:
        print("无法访问INDIA_TRENDS_SYSTEM_PROMPT")
else:
    print("PROMPTS属性不可用")

print("\n测试完成！")
