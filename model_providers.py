# 模型供应商配置

# 模型供应商列表
MODEL_PROVIDERS = [
    {
        "name": "OpenAI",
        "endpoint": "https://api.openai.com/v1",
        "models_endpoint": "/models",
        "default_models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        "api_key_required": True,
        "description": "OpenAI官方API"
    },
    {
        "name": "Anthropic",
        "endpoint": "https://api.anthropic.com/v1",
        "models_endpoint": "/models",
        "default_models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240229"],
        "api_key_required": True,
        "description": "Anthropic官方API"
    },
    {
        "name": "DeepSeek",
        "endpoint": "https://api.deepseek.com/v1",
        "models_endpoint": "/models",
        "default_models": ["deepseek-chat", "deepseek-coder"],
        "api_key_required": True,
        "description": "深度求索官方API"
    },
    {
        "name": "Fireworks",
        "endpoint": "https://api.fireworks.ai/inference",
        "models_endpoint": "/models",
        "default_models": [],
        "api_key_required": True,
        "description": "Fireworks AI API"
    },
    {
        "name": "Zhinao",
        "endpoint": "https://api.360.cn",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "360智脑API"
    },
    {
        "name": "Hunyuan",
        "endpoint": "https://api.hunyuan.cloud.tencent.com",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "腾讯混元API"
    },
    {
        "name": "NVIDIA",
        "endpoint": "https://integrate.api.nvidia.com",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "NVIDIA API"
    },
    {
        "name": "Azure OpenAI",
        "endpoint": "https://{your-resource-name}.openai.azure.com/openai/deployments/{deployment-name}/chat/completions?api-version={api-version}",
        "models_endpoint": None,
        "default_models": ["gpt-4", "gpt-3.5-turbo"],
        "api_key_required": True,
        "description": "Azure OpenAI服务"
    },
    {
        "name": "Baidu Cloud",
        "endpoint": "https://qianfan.baidubce.com/v2/",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "百度云API"
    },
    {
        "name": "Tencent Cloud TI",
        "endpoint": "https://api.lkeap.cloud.tencent.com",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "腾讯云TI API"
    },
    {
        "name": "GPUStack",
        "endpoint": "",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "GPUStack API"
    },
    {
        "name": "VoyageAI",
        "endpoint": "https://api.voyageai.com",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "VoyageAI API"
    },
    {
        "name": "Qiniu",
        "endpoint": "https://api.qnaigc.com",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "七牛云API"
    },
    {
        "name": "Cephalon",
        "endpoint": "https://cephalon.cloud/user-center/v1/model",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "Cephalon API"
    },
    {
        "name": "Lanyun",
        "endpoint": "https://maas-api.lanyun.net",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "蓝云API"
    },
    {
        "name": "VertexAI",
        "endpoint": "https://console.cloud.google.com/apis/api/aiplatform.googleapis.com/overview",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "Google VertexAI API"
    },
    {
        "name": "Google Gemini",
        "endpoint": "https://generativelanguage.googleapis.com/v1/models/{model}:generateContent",
        "models_endpoint": None,
        "default_models": ["gemini-pro", "gemini-ultra"],
        "api_key_required": True,
        "description": "Google Gemini API"
    },
    {
        "name": "ByteDance",
        "endpoint": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        "models_endpoint": None,
        "default_models": ["ep-20240101123456-abcde"],
        "api_key_required": True,
        "description": "字节跳动API"
    },
    {
        "name": "Custom",
        "endpoint": "",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "自定义API端点"
    }
]

# 获取供应商配置
def get_provider_config(provider_name):
    """根据供应商名称获取配置"""
    for provider in MODEL_PROVIDERS:
        if provider["name"] == provider_name:
            return provider
    return None

# 获取默认供应商列表
def get_provider_names():
    """获取所有供应商名称列表"""
    return [provider["name"] for provider in MODEL_PROVIDERS]

# 获取供应商默认模型
def get_provider_default_models(provider_name):
    """获取指定供应商的默认模型列表"""
    provider = get_provider_config(provider_name)
    if provider:
        return provider["default_models"]
    return []

# 获取供应商默认端点
def get_provider_default_endpoint(provider_name):
    """获取指定供应商的默认端点"""
    provider = get_provider_config(provider_name)
    if provider:
        return provider["endpoint"]
    return ""
