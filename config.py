"""
应用程序配置模块

此模块包含应用程序的所有配置参数，包括区域信息、URL模板和其他设置。
"""

# --- 区域配置 ---
# 目标网址 URL 相关内容整合为 REGIONS 配置项
# 使用国家作为顶级键，支持多国家/地区扩展
# 添加了timezone字段，用于基于时区的调度
REGIONS = {
    "India": {
        "name": "India",
        "timezone": "Asia/Kolkata",  # GMT+5:30
        "regions": [
            {'code': 'IN-RJ', 'name': 'Rajasthan'},
            {'code': 'IN-DL', 'name': 'Delhi'},
            {'code': 'IN-MH', 'name': 'Maharashtra'},
            {'code': 'IN-TN', 'name': 'Tamil Nadu'},
            {'code': 'IN-UP', 'name': 'Uttar Pradesh'},
            {'code': 'IN-AP', 'name': 'Andhra Pradesh'},
            {'code': 'IN-AS', 'name': 'Assam'},
            {'code': 'IN-KA', 'name': 'Karnataka'},
            {'code': 'IN-BR', 'name': 'Bihar'},
            {'code': 'IN-CT', 'name': 'Chhattisgarh'},
            {'code': 'IN-GJ', 'name': 'Gujarat'},
            {'code': 'IN-HR', 'name': 'Haryana'},
            {'code': 'IN-TG', 'name': 'Telangana'},
            {'code': 'IN-JH', 'name': 'Jharkhand'},
            {'code': 'IN-KL', 'name': 'Kerala'},
            {'code': 'IN-WB', 'name': 'West Bengal'},
            {'code': 'IN-MP', 'name': 'Madhya Pradesh'},
            {'code': 'IN-OR', 'name': 'Odisha'},
            {'code': 'IN-PB', 'name': 'Punjab'},
            {'code': 'IN-UT', 'name': 'Uttarakhand'},
            {'code': 'IN', 'name': 'India(ALL Regions)'},
            {'code': 'IN-CH', 'name': 'Chandigarh'}
        ]
    },
    "United Kingdom": {
        "name": "United Kingdom",
        "timezone": "Europe/London",  # GMT/BST
        "regions": [
            {'code': 'GB', 'name': 'United Kingdom(ALL Regions)'},
            {'code': 'GB-ENG', 'name': 'England'},
            {'code': 'GB-NIR', 'name': 'Northern Ireland'},
            {'code': 'GB-SCT', 'name': 'Scotland'},
            {'code': 'GB-WLS', 'name': 'Wales'}
        ]
    },
    "Australia": {
        "name": "Australia",
        "timezone": "Australia/Sydney",  # GMT+10/+11
        "regions": [
            {'code': 'AU', 'name': 'Australia(all region)'},
            {'code': 'AU-NSW', 'name': 'New South Wales'},
            {'code': 'AU-QLD', 'name': 'Queensland'},
            {'code': 'AU-VIC', 'name': 'Victoria'}
        ]
    },
    "United States": {
        "name": "United States",
        "timezone": "America/New_York",  # GMT-5/-4 (Eastern Time)
        "regions": [
            {'code': 'US', 'name': 'United States(all regions)'},
            {'code': 'US-AL', 'name': 'Alabama'},
            {'code': 'US-CA', 'name': 'California'},
            {'code': 'US-TX', 'name': 'Texas'},
            {'code': 'US-FL', 'name': 'Florida'},
            {'code': 'US-NY', 'name': 'New York'},
            {'code': 'US-PA', 'name': 'Pennsylvania'},
            {'code': 'US-IL', 'name': 'Illinois'},
            {'code': 'US-OH', 'name': 'Ohio'},
            {'code': 'US-GA', 'name': 'Georgia'},
            {'code': 'US-NC', 'name': 'North Carolina'},
            {'code': 'US-MI', 'name': 'Michigan'},
            {'code': 'US-NJ', 'name': 'New Jersey'},
            {'code': 'US-VA', 'name': 'Virginia'},
            {'code': 'US-WA', 'name': 'Washington'},
            {'code': 'US-AZ', 'name': 'Arizona'},
            {'code': 'US-MA', 'name': 'Massachusetts'},
            {'code': 'US-TN', 'name': 'Tennessee'},
            {'code': 'US-IN', 'name': 'Indiana'},
            {'code': 'US-MD', 'name': 'Maryland'},
            {'code': 'US-MO', 'name': 'Missouri'},
            {'code': 'US-WI', 'name': 'Wisconsin'},
            {'code': 'US-CO', 'name': 'Colorado'},
            {'code': 'US-MN', 'name': 'Minnesota'},
            {'code': 'US-SC', 'name': 'South Carolina'},
            {'code': 'US-LA', 'name': 'Louisiana'},
            {'code': 'US-KY', 'name': 'Kentucky'},
            {'code': 'US-OR', 'name': 'Oregon'},
            {'code': 'US-OK', 'name': 'Oklahoma'},
            {'code': 'US-CT', 'name': 'Connecticut'},
            {'code': 'US-UT', 'name': 'Utah'},
            {'code': 'US-IA', 'name': 'Iowa'},
            {'code': 'US-NV', 'name': 'Nevada'},
            {'code': 'US-AR', 'name': 'Arkansas'},
            {'code': 'US-MS', 'name': 'Mississippi'},
            {'code': 'US-KS', 'name': 'Kansas'},
            {'code': 'US-NM', 'name': 'New Mexico'},
            {'code': 'US-NE', 'name': 'Nebraska'},
            {'code': 'US-ID', 'name': 'Idaho'},
            {'code': 'US-WV', 'name': 'West Virginia'},
            {'code': 'US-HI', 'name': 'Hawaii'},
            {'code': 'US-NH', 'name': 'New Hampshire'},
            {'code': 'US-ME', 'name': 'Maine'},
            {'code': 'US-RI', 'name': 'Rhode Island'},
            {'code': 'US-MT', 'name': 'Montana'},
            {'code': 'US-DE', 'name': 'Delaware'},
            {'code': 'US-SD', 'name': 'South Dakota'},
            {'code': 'US-ND', 'name': 'North Dakota'},
            {'code': 'US-AK', 'name': 'Alaska'},
            {'code': 'US-VT', 'name': 'Vermont'},
            {'code': 'US-WY', 'name': 'Wyoming'}
        ]
    },
    "France": {
        "name": "France",
        "timezone": "Europe/Paris",  # GMT+1/+2
        "regions": [
            {'code': 'FR', 'name': 'France(all regions)'},
            {'code': 'FR-A', 'name': 'Alsace'},
            {'code': 'FR-B', 'name': 'Aquitaine'},
            {'code': 'FR-C', 'name': 'Auvergne'},
            {'code': 'FR-D', 'name': 'Burgundy'},
            {'code': 'FR-E', 'name': 'Brittany'},
            {'code': 'FR-F', 'name': 'Centre-Val de Loire'},
            {'code': 'FR-G', 'name': 'Champagne-Ardenne'},
            {'code': 'FR-H', 'name': 'Corsica'},
            {'code': 'FR-I', 'name': 'Franche-Comte'},
            {'code': 'FR-J', 'name': 'Ile-de-France'},
            {'code': 'FR-K', 'name': 'Languedoc-Roussillon'},
            {'code': 'FR-L', 'name': 'Limousin'},
            {'code': 'FR-M', 'name': 'Lorraine'},
            {'code': 'FR-N', 'name': 'Midi-Pyrenees'},
            {'code': 'FR-O', 'name': 'Nord-Pas-de-Calais'},
            {'code': 'FR-P', 'name': 'Lower Normandy'},
            {'code': 'FR-Q', 'name': 'Lower Normandy'},
            {'code': 'FR-R', 'name': 'Pays de la Loire'},
            {'code': 'FR-S', 'name': 'Picardy'},
            {'code': 'FR-T', 'name': 'Poitou-Charentes'},
            {'code': 'FR-U', 'name': 'Provence-Alpes-Cote dAzur'},
            {'code': 'FR-V', 'name': 'Rhone-Alpes'}
        ]
    },
    "Thailand": {
        "name": "Thailand",
        "timezone": "Asia/Bangkok",  # GMT+7
        "regions": [
            {'code': 'TH', 'name': 'Thailand(all region)'}
        ]
    },
    "Malaysia": {
        "name": "Malaysia",
        "timezone": "Asia/Kuala_Lumpur",  # GMT+8
        "regions": [
            {'code': 'MY', 'name': 'Malaysia(all region)'},
            {'code': 'MY-1', 'name': 'Johor'},
            {'code': 'MY-2', 'name': 'Kedah'},
            {'code': 'MY-3', 'name': 'Kelantan'},
            {'code': 'MY-4', 'name': 'Malacca'},
            {'code': 'MY-5', 'name': 'Negeri Sembilan'},
            {'code': 'MY-6', 'name': 'Pahang'},
            {'code': 'MY-7', 'name': 'Penang'},
            {'code': 'MY-8', 'name': 'Perak'},
            {'code': 'MY-9', 'name': 'Perlis'},
            {'code': 'MY-10', 'name': 'Selangor'},
            {'code': 'MY-11', 'name': 'Terengganu'},
            {'code': 'MY-12', 'name': 'Sabah'},
            {'code': 'MY-13', 'name': 'Sarawak'},
            {'code': 'MY-14', 'name': 'Federal Territory of Kuala Lumpur'},
            {'code': 'MY-15', 'name': 'Labuan Federal Territory'},
            {'code': 'MY-16', 'name': 'Putrajaya'}
        ]
    },
    "Vietnam": {
        "name": "Vietnam",
        "timezone": "Asia/Ho_Chi_Minh",  # GMT+7
        "regions": [
            {'code': 'VN', 'name': 'Vietnam(all regions)'}
        ]
    }
}

# --- 应用程序配置 ---
# Google Trends RSS URL 模板
GOOGLE_TRENDS_RSS_URL = "https://trends.google.com/trending/rss?geo={code}"

# 请求配置
REQUEST_TIMEOUT = 30
REQUEST_MAX_RETRIES = 3
REQUEST_DELAY_BETWEEN_REGIONS = (1, 2)
REQUEST_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"

# 代理配置
USE_PROXY = True  # 是否启用代理
HTTP_PROXY_HOST = "127.0.0.1"  # 代理服务器地址
HTTP_PROXY_PORT = 10808  # 代理服务器端口

# 输出配置
OUTPUT_DIR = "JSONs"
OUTPUT_FILE_PREFIX = "trends_"
OUTPUT_FILE_EXTENSION = ".json"

# 调度器配置
SCHEDULER_CRON_EXPRESSION = "0,30 11,17,23 * * *"  # 每天 11:00, 11:30, 17:00, 17:30, 23:00, 23:30 运行

# --- 提示词配置 ---
PROMPTS = {
    # 日志消息模板
    "LOG_FETCH_START": "正在拉取 {region_name} ({region_code}) 的数据... (尝试 {attempt}/{max_retries})",
    "LOG_FETCH_SUCCESS": "{region_name} 数据拉取成功，长度: {content_length}",
    "LOG_FETCH_ERROR": "拉取 {region_name} 数据失败，状态码: {status_code}",
    "LOG_FETCH_RATE_LIMIT": "收到 429 错误，为 {region_name} 等待更长时间后重试...",
    "LOG_FETCH_COMPLETE": "总共拉取到 {count} 个新条目",
    "LOG_MERGE_COMPLETE": "数据合并完成，共 {count} 个条目",
    "LOG_SAVE_SUCCESS": "数据已保存到 {filename}，共 {count} 个条目",
    "LOG_SAVE_ERROR": "保存数据到文件 {filename} 时出错: {error}",
    "LOG_LOAD_SUCCESS": "已加载现有数据文件: {filename}, 包含 {count} 个条目",
    "LOG_LOAD_ERROR": "加载现有数据文件 {filename} 时出错: {error}",
    "LOG_XML_PARSE_ERROR": "解析 {region_name} 的 XML 数据时出错: {error}",
    "LOG_CHANNEL_MISSING": "在 {region_name} 的数据中未找到 channel 元素",
    "LOG_DATE_PARSE_ERROR": "无法解析 {region_name} - {title} 的日期: {date_str} ({error}), 使用当前时间",

    # Streamlit AI 应用提示词
    "AI_DEFAULT_USER_PROMPT" : "请你对这些热点进行分析，给出一个整体趋势判断，对重点的热点做解释，推测关注群体的画像和社媒内容营销建议",
    "AI_DEFAULT_TABLE_CONTENT_PLACEHOLDER": "{table_content}",
    "AI_DEFAULT_SYSTEM_PROMPT": """你是 **GLOBAL TRENDS AI**，一位顶尖数字营销策略专家，专注于全球社交媒体与病毒式趋势分析，擅长区域营销。你具备多年在全球主要市场的实战经验，能够结合数据科学的严谨性与各地文化的深刻理解，分析不同区域的社交媒体热度、趋势和用户行为。

### **任务目标**：
1. **趋势分析**：
   - 根据热点的流量指数（`traffic_num`）和发布时间（`pub_date`），推测热点的热度变化趋势，判断它是短期爆发、长期持续，还是由事件驱动的周期性热点。
   - 分析热点在不同地区（`regions`）的分布，探索地域差异对热度变化的影响。

2. **热点解读**：
   - 结合新闻标题（`news_title`）和搜索关键词（`title`），分析热点的背景，推测它为何成为关注焦点。
   - 提出热点背后的社会、文化或政治因素，并分析其可能的深层原因。

3. **用户画像分析**：
   - 基于流量指数和地域分布（`regions`），推测关注该热点的主要群体特征，例如年龄、性别、职业和兴趣等。
   - 分析是否存在特定群体或区域对该热点的高度关注，帮助理解不同受众的需求。

4. **社交媒体营销建议**：
   - 提出具体的社交媒体内容策略，建议使用哪些平台（如 Twitter、Instagram、LinkedIn 等），并推荐合适的内容形式（如图文、视频等）。
   - 推荐适合的传播方式（如使用话题标签、互动活动等）以提升热点的社交媒体曝光度和互动性。

### **数据处理规范**：
- 仅使用以下字段进行分析：
  - `news_title`: 新闻标题，提炼热点的核心。
  - `source`: 媒体来源，评估传播力。
  - `title`: 搜索关键词，分析热点的受关注度。
  - `traffic_num`: 流量指数，衡量热点热度。
  - `pub_date`: 发布时间，分析热点的时效性。
  - `regions`: 热点的地域分布，揭示文化和地域差异。

### **行为指导**：
- 你应根据以下规范进行数据分析：
  - **趋势分析**：根据流量指数（`traffic_num`）和发布时间（`pub_date`）推测热点的热度变化趋势。判断热点是短期爆发（突发）、长期持续（持续）还是由事件驱动的周期性热点。
  - **热点解读**：结合新闻标题（`news_title`）和搜索关键词（`title`），分析热点背后的社会、文化或政治背景，推测热点为什么会成为关注焦点。
  - **用户画像分析**：通过流量指数、地域分布（`regions`）和趋势变化，推测热点的关注群体特征，包括年龄、性别、职业等。
  - **社交媒体策略**：提供具体的社交媒体内容建议，包括推荐平台、内容形式（如图文、视频）和传播策略（如话题标签、互动活动等）。

### **默认语言**：中文"""
}

# --- 开发/生产环境配置 ---
class Config:
    """基础配置类"""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = "INFO"
    GOOGLE_TRENDS_RSS_URL = GOOGLE_TRENDS_RSS_URL
    REQUEST_TIMEOUT = REQUEST_TIMEOUT
    REQUEST_MAX_RETRIES = REQUEST_MAX_RETRIES
    REQUEST_DELAY_BETWEEN_REGIONS = REQUEST_DELAY_BETWEEN_REGIONS
    REQUEST_USER_AGENT = REQUEST_USER_AGENT
    OUTPUT_DIR = OUTPUT_DIR
    OUTPUT_FILE_PREFIX = OUTPUT_FILE_PREFIX
    OUTPUT_FILE_EXTENSION = OUTPUT_FILE_EXTENSION
    SCHEDULER_CRON_EXPRESSION = SCHEDULER_CRON_EXPRESSION
    REGIONS = REGIONS
    PROMPTS = PROMPTS
    # 代理配置
    USE_PROXY = USE_PROXY
    HTTP_PROXY_HOST = HTTP_PROXY_HOST
    HTTP_PROXY_PORT = HTTP_PROXY_PORT

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = "INFO"

# 配置映射，用于根据环境选择配置
CONFIG_MAP = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}

# 获取当前环境的配置
def get_config(env: str = "default") -> Config:
    """
    获取指定环境的配置对象
    
    Args:
        env (str): 环境名称 (development/production/default)
    
    Returns:
        Config: 配置对象
    """
    return CONFIG_MAP.get(env, CONFIG_MAP["default"])

# 默认配置对象
current_config = get_config()
