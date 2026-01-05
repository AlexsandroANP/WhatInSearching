"""
敏感信息配置模块

此模块包含应用程序的敏感信息，如API密钥、端点等。
请确保此文件不被提交到版本控制系统中。
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# --- 模型 API 配置 ---
# AI模型API密钥和端点
MODEL_API_KEY = os.getenv("MODEL_API_KEY", "")
MODEL_API_ENDPOINT = os.getenv("MODEL_API_ENDPOINT", "https://api.example.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")

# --- Google Trends 配置 ---# 目前 Google Trends RSS 不需要 API 密钥，但如果未来需要可以在这里添加# GOOGLE_TRENDS_API_KEY = os.getenv("GOOGLE_TRENDS_API_KEY", "")

# --- 其他敏感信息 ---# 根据需要添加其他敏感信息
