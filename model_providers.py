# 模型供应商配置

# 配置来源：Cherry Studio 开源项目
# 项目地址：https://github.com/CherryHQ/cherry-studio
# 配置文件：https://github.com/CherryHQ/cherry-studio/blob/main/src/renderer/src/config/providers.ts
# 最后更新时间：2026-01-11
# 尊重开源精神，基于 Cherry Studio 项目的配置信息进行整理

import os
import re
import json
import urllib.request

# 模型供应商列表
MODEL_PROVIDERS = [
        {
        "name": "17chuhai",
        "endpoint": "https://api.17chuhai.top/v1",
        "models_endpoint": "/models",
        "default_models": [],
        "api_key_required": True,
        "description": "17ChuHai API"
    },
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
    },
    {
        "name": "OpenRouter",
        "endpoint": "https://openrouter.ai/api/v1",
        "models_endpoint": "/models",
        "default_models": [],
        "api_key_required": True,
        "description": "OpenRouter API"
    },
    {
        "name": "Groq",
        "endpoint": "https://api.groq.com/openai",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "Groq API"
    },
    {
        "name": "OVMS",
        "endpoint": "http://localhost:8000/v3/",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": False,
        "description": "OpenVINO Model Server"
    },
    {
        "name": "Ollama",
        "endpoint": "http://localhost:11434",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": False,
        "description": "Ollama本地模型服务器"
    },
    {
        "name": "LM Studio",
        "endpoint": "http://localhost:1234",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": False,
        "description": "LM Studio本地模型服务器"
    },
    {
        "name": "Grok",
        "endpoint": "https://api.x.ai",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "Grok API"
    },
    {
        "name": "Hyperbolic",
        "endpoint": "https://api.hyperbolic.xyz",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "Hyperbolic API"
    },
    {
        "name": "Mistral",
        "endpoint": "https://api.mistral.ai",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "Mistral AI API"
    },
    {
        "name": "Jina",
        "endpoint": "https://api.jina.ai",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "Jina AI API"
    },
    {
        "name": "AIHubMix",
        "endpoint": "https://aihubmix.com",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "AIHubMix API"
    },
    {
        "name": "TokenFlux",
        "endpoint": "",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "TokenFlux API"
    },
    {
        "name": "New API",
        "endpoint": "http://localhost:3000",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": False,
        "description": "New API本地服务器"
    },
    {
        "name": "AWS Bedrock",
        "endpoint": "",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "AWS Bedrock API"
    },
    {
        "name": "Poe",
        "endpoint": "https://api.poe.com/v1/",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "Poe API"
    },
    {
        "name": "AIOnly",
        "endpoint": "https://api.aiionly.com",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "AIOnly API"
    },
    {
        "name": "LongCat",
        "endpoint": "https://api.longcat.chat/openai",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "LongCat API"
    },
    {
        "name": "Hugging Face",
        "endpoint": "https://router.huggingface.co/v1/",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "Hugging Face API"
    },
    {
        "name": "Gateway",
        "endpoint": "https://ai-gateway.vercel.sh/v1/ai",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "Vercel AI Gateway"
    },
    {
        "name": "Cerebras",
        "endpoint": "https://api.cerebras.ai/v1",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "Cerebras API"
    },
    {
        "name": "Mimo",
        "endpoint": "https://api.xiaomimimo.com",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "Xiaomi Mimo API"
    },
    {
        "name": "CherryIN",
        "endpoint": "https://open.cherryin.net",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "CherryIN API"
    },
    {
        "name": "Silicon",
        "endpoint": "https://api.siliconflow.cn",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "Silicon Flow API"
    },
    {
        "name": "OcoolAI",
        "endpoint": "https://api.ocoolai.com",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "OcoolAI API"
    },
    {
        "name": "ZhiPu",
        "endpoint": "https://open.bigmodel.cn/api/paas/v4/",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "智谱AI API"
    },
    {
        "name": "AlayaNew",
        "endpoint": "https://deepseek.alayanew.com",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "AlayaNew API"
    },
    {
        "name": "DMXAPI",
        "endpoint": "https://www.dmxapi.cn",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "DMXAPI"
    },
    {
        "name": "BurnCloud",
        "endpoint": "https://ai.burncloud.com",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "BurnCloud API"
    },
    {
        "name": "302.AI",
        "endpoint": "https://api.302.ai",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "302.AI API"
    },
    {
        "name": "PH8",
        "endpoint": "https://ph8.co",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "PH8 API"
    },
    {
        "name": "SophNet",
        "endpoint": "https://www.sophnet.com/api/open-apis/v1",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "SophNet API"
    },
    {
        "name": "PPIO",
        "endpoint": "https://api.ppinfra.com/v3/openai/",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "PPIO API"
    },
    {
        "name": "Github Models",
        "endpoint": "https://models.github.ai/inference",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "Github Models API"
    },
    {
        "name": "Github Copilot",
        "endpoint": "https://api.githubcopilot.com/",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "Github Copilot API"
    },
    {
        "name": "Yi",
        "endpoint": "https://api.lingyiwanwu.com",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "Yi API"
    },
    {
        "name": "Moonshot AI",
        "endpoint": "https://api.moonshot.cn",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "Moonshot AI API"
    },
    {
        "name": "BAICHUAN AI",
        "endpoint": "https://api.baichuan-ai.com",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "BAICHUAN AI API"
    },
    {
        "name": "Bailian",
        "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1/",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "Bailian API"
    },
    {
        "name": "StepFun",
        "endpoint": "https://api.stepfun.com",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "StepFun API"
    },
    {
        "name": "Doubao",
        "endpoint": "https://ark.cn-beijing.volces.com/api/v3/",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "Doubao API"
    },
    {
        "name": "Infini",
        "endpoint": "https://cloud.infini-ai.com/maas",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "Infini API"
    },
    {
        "name": "MiniMax",
        "endpoint": "https://api.minimaxi.com/v1",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "MiniMax API"
    },
    {
        "name": "Together",
        "endpoint": "https://api.together.xyz",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "Together API"
    },
    {
        "name": "Perplexity",
        "endpoint": "https://api.perplexity.ai/",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "Perplexity API"
    },
    {
        "name": "ModelScope",
        "endpoint": "https://api-inference.modelscope.cn/v1/",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "ModelScope API"
    },
    {
        "name": "Xirang",
        "endpoint": "https://wishub-x1.ctyun.cn",
        "models_endpoint": None,
        "default_models": [],
        "api_key_required": True,
        "description": "Xirang API"
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


def update_model_providers_from_github():
    """
    从 GitHub Cherry Studio 项目下载最新的模型供应商配置并更新本地配置
    
    步骤：
    1. 从 GitHub API 获取 providers.ts 文件内容
    2. 解析文件，提取模型供应商配置
    3. 更新 MODEL_PROVIDERS 列表
    4. 清理临时文件
    """
    global MODEL_PROVIDERS
    
    print("开始从 GitHub 更新模型供应商配置...")
    
    # GitHub API URL 获取 providers.ts 文件
    api_url = "https://api.github.com/repos/CherryHQ/cherry-studio/contents/src/renderer/src/config/providers.ts"
    
    try:
        # 发送请求获取文件信息
        with urllib.request.urlopen(api_url) as response:
            if response.getcode() == 200:
                file_info = json.loads(response.read().decode('utf-8'))
                # 解码 base64 内容
                import base64
                file_content = base64.b64decode(file_info['content']).decode('utf-8')
                
                # 保存到临时文件
                temp_file = "providers.ts"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(file_content)
                
                print(f"成功下载 providers.ts 文件")
                
                # 解析文件，提取模型供应商配置
                print("解析模型供应商配置...")
                
                # 提取所有供应商配置
                providers = []
                
                # 使用更灵活的正则表达式匹配每个供应商的配置
                # 匹配格式：id: {
                #   name: "Name",
                #   apiHost: "https://api.example.com",
                #   ...
                # },
                provider_pattern = re.compile(r'\s*(\w+):\s*{([\s\S]*?)},', re.MULTILINE)
                provider_matches = provider_pattern.findall(file_content)
                
                print(f"找到 {len(provider_matches)} 个供应商配置")
                
                for provider_id, provider_config in provider_matches:
                    # 提取名称
                    name_match = re.search(r'name:\s*["\']([^"\']+)["\']', provider_config)
                    if not name_match:
                        continue
                    
                    name = name_match.group(1)
                    
                    # 提取 API 主机
                    api_host_match = re.search(r'apiHost:\s*["\']([^"\']+)["\']', provider_config)
                    endpoint = api_host_match.group(1) if api_host_match else ""
                    
                    # 提取是否需要 API 密钥
                    api_key_required = True  # 默认需要
                    
                    # 构建供应商配置
                    provider = {
                        "name": name,
                        "endpoint": endpoint,
                        "models_endpoint": None,
                        "default_models": [],
                        "api_key_required": api_key_required,
                        "description": f"{name} API"
                    }
                    
                    providers.append(provider)
                    print(f"添加供应商: {name} ({endpoint})")
                
                if providers:
                    # 更新 MODEL_PROVIDERS 列表
                    # 保留原有的默认模型配置
                    existing_providers = {p["name"]: p for p in MODEL_PROVIDERS}
                    
                    for provider in providers:
                        if provider["name"] in existing_providers:
                            # 保留原有的默认模型配置
                            provider["default_models"] = existing_providers[provider["name"]].get("default_models", [])
                            provider["models_endpoint"] = existing_providers[provider["name"]].get("models_endpoint", None)
                            provider["description"] = existing_providers[provider["name"]].get("description", provider["description"])
                        existing_providers[provider["name"]] = provider
                    
                    # 转换回列表
                    MODEL_PROVIDERS = list(existing_providers.values())
                    
                    print(f"成功更新模型供应商配置，共 {len(MODEL_PROVIDERS)} 个供应商")
                    
                    # 清理临时文件
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                        print(f"已删除临时文件 {temp_file}")
                    
                    return True
                else:
                    print("未找到供应商配置")
                    # 清理临时文件
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                    return False
            else:
                print(f"请求 GitHub API 失败，状态码: {response.getcode()}")
                return False
    except Exception as e:
        print(f"更新过程中发生错误: {str(e)}")
        # 清理临时文件
        if os.path.exists("providers.ts"):
            os.remove("providers.ts")
        return False


# 如果直接运行此脚本，则执行更新操作
if __name__ == "__main__":
    success = update_model_providers_from_github()
    if success:
        print("模型供应商配置更新成功！")
        print(f"当前供应商数量: {len(MODEL_PROVIDERS)}")
        print("前 5 个供应商:")
        for provider in MODEL_PROVIDERS[:5]:
            print(f"- {provider['name']}: {provider['endpoint']}")
    else:
        print("模型供应商配置更新失败")
