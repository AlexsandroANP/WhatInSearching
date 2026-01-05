"""
提示词文本资源模块

此模块包含应用程序中使用的所有提示词文本，便于统一管理和多语言支持。
"""

# 日志消息模板
LOG_FETCH_START = "正在拉取 {region_name} ({region_code}) 的数据... (尝试 {attempt}/{max_retries})"
LOG_FETCH_SUCCESS = "{region_name} 数据拉取成功，长度: {content_length}"
LOG_FETCH_ERROR = "拉取 {region_name} 数据失败，状态码: {status_code}"
LOG_FETCH_RATE_LIMIT = "收到 429 错误，为 {region_name} 等待更长时间后重试..."
LOG_FETCH_COMPLETE = "总共拉取到 {count} 个新条目"
LOG_MERGE_COMPLETE = "数据合并完成，共 {count} 个条目"
LOG_SAVE_SUCCESS = "数据已保存到 {filename}，共 {count} 个条目"
LOG_SAVE_ERROR = "保存数据到文件 {filename} 时出错: {error}"
LOG_LOAD_SUCCESS = "已加载现有数据文件: {filename}, 包含 {count} 个条目"
LOG_LOAD_ERROR = "加载现有数据文件 {filename} 时出错: {error}"
LOG_XML_PARSE_ERROR = "解析 {region_name} 的 XML 数据时出错: {error}"
LOG_CHANNEL_MISSING = "在 {region_name} 的数据中未找到 channel 元素"
LOG_DATE_PARSE_ERROR = "无法解析 {region_name} - {title} 的日期: {date_str} ({error}), 使用当前时间"

# Streamlit AI 应用提示词
AI_DEFAULT_USER_PROMPT = "请你对这些热点进行分析，给出一个整体趋势判断，对重点的热点做解释，推测关注群体的画像和社媒内容营销建议"
AI_DEFAULT_TABLE_CONTENT_PLACEHOLDER = "{table_content}"
AI_DEFAULT_SYSTEM_PROMPT = """你是一位 Google Trends 热点分析专家。
**严格仅使用以下字段**：  
- `news_title`: 新闻完整标题
- `source`: 信源媒体名称
- `title`: 搜索关键词
- `traffic_num`: 相对流量指数
- `pub_date`: 发布时间
- `regions`: 覆盖区域

# 系统提示：印度网络搜索热点趋势分析智能体

## 🎯 核心身份
你是 **INDIA PULSE AI**，一位顶尖数字营销策略专家，专注于印度社交媒体与病毒式趋势分析。
拥有8年以上在孟买、德里、海得拉巴和班加罗尔市场的实战经验，你将数据科学严谨性与深厚文化直觉完美结合。
你精通印地语、英语，并理解泰米尔语、泰卢固语、旁遮普语等区域文化细微差别。
你的使命：将原始趋势数据转化为可执行的增长策略，同时尊重印度的文化根基。

## 任务
1. 舆情分析；
2. 结合新闻标题的信息，对热点进行解释；
3. 识别出话题生命周期，突发(short-lived)、持续(sustained)、阶段(cyclical/event-driven)；
3. 用户提出的其它需求；

默认使用中文语言。"""