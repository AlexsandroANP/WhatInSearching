import streamlit as st
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
import tiktoken  # 用于估算 token 数量
import openai
from openai import OpenAI
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import requests

# 导入配置模块
from config import get_config
config = get_config()

# 导入模型供应商配置
from model_providers import (
    get_provider_config,
    get_provider_names,
    get_provider_default_models,
    get_provider_default_endpoint
)

# --- 设置工作目录为脚本所在目录 ---
# 获取当前脚本的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 切换到脚本所在目录
os.chdir(script_dir)
# st.write(f"工作目录已设置为: {os.getcwd()}") # 可选：打印当前工作目录以确认


# --- 配置 ---
# 1. 指定包含 JSON 文件的文件夹路径 (请修改为你自己的路径)
FOLDER_PATH = 'JSONs'  # <--- 修改此路径
JSON_FILENAME_PATTERN = 'trends_{}.json' # JSON 文件名的模式，{} 会被日期替换

# 导入配置和凭证模块
# 从config中获取提示词配置
AI_DEFAULT_USER_PROMPT = config.PROMPTS.AI_DEFAULT_USER_PROMPT
AI_DEFAULT_TABLE_CONTENT_PLACEHOLDER = config.PROMPTS.AI_DEFAULT_TABLE_CONTENT_PLACEHOLDER
AI_DEFAULT_SYSTEM_PROMPT = config.PROMPTS.AI_DEFAULT_SYSTEM_PROMPT
from credentials import (
    MODEL_API_KEY,
    MODEL_API_ENDPOINT,
    MODEL_NAME
)

# --- AI 配置 ---
# 你可以在这里修改默认值，优先使用环境变量
DEFAULT_ENDPOINT = MODEL_API_ENDPOINT  # 从凭证模块导入
DEFAULT_API_KEY = MODEL_API_KEY  # 从凭证模块导入
DEFAULT_MODEL = MODEL_NAME  # 从凭证模块导入
DEFAULT_MAX_TOKENS = 128*1024  # 64K tokens
DEFAULT_USER_PROMPT = AI_DEFAULT_USER_PROMPT  # 从提示词模块导入
DEFAULT_TABLE_CONTENT_PLACEHOLDER = AI_DEFAULT_TABLE_CONTENT_PLACEHOLDER  # 从提示词模块导入
DEFAULT_SYSTEM_PROMPT = AI_DEFAULT_SYSTEM_PROMPT  # 从提示词模块导入
DEFAULT_SUPPLIER = "OpenAI"  # 默认供应商


# --- 函数定义 ---
def parse_pub_date(pub_date_str):
    """解析 ISO 8601 格式的 pubDate 字符串为 datetime 对象"""
    # 示例格式: "2025-10-21T17:20:00-07:00", "2025-12-30"
    try:
        # Python 的 fromisoformat 在 3.11+ 中支持带时区的格式，对于旧版本，需要手动处理
        # 移除时区偏移部分并手动解析
        # 格式为 YYYY-MM-DDTHH:MM:SS+HH:MM 或 -HH:MM
        # 这里简单地移除时区部分，只取日期时间
        # 更精确的处理可以使用 dateutil 库
        # 为了兼容性，这里手动分割
        if pub_date_str:
            # 检查是否包含时间部分
            if 'T' in pub_date_str:
                # 分割日期时间和时区
                dt_part = pub_date_str.split('T')[0]
                time_part = pub_date_str.split('T')[1].split('-')[0].split('+')[0] # 移除时区
                full_dt_str = f"{dt_part}T{time_part}"
                # 直接解析完整的日期时间字符串，不进行额外的分割
                dt = datetime.fromisoformat(full_dt_str.replace('Z', '+00:00'))
            else:
                # 简单日期格式，如 "2025-12-30"
                dt = datetime.strptime(pub_date_str, '%Y-%m-%d')
            return dt.date()
    except ValueError:
        try:
            # 尝试其他可能的格式
            dt = datetime.strptime(pub_date_str.split('T')[0], '%Y-%m-%d')
            return dt.date()
        except ValueError:
            st.warning(f"无法解析日期字符串: {pub_date_str}")
            return None
    return None

def is_date_in_range(pub_date_str, start_date, end_date):
    """检查 pubDate 是否在指定范围内"""
    parsed_date = parse_pub_date(pub_date_str)
    if parsed_date:
        return start_date <= parsed_date <= end_date
    return False

def load_and_process_file_for_date(target_date, results_list):
    """加载并处理指定日期的 JSON 文件，将每个新闻项作为一行添加到列表中"""
    filename = JSON_FILENAME_PATTERN.format(target_date.strftime('%Y-%m-%d'))
    
    # 搜索所有国家子文件夹中的JSON文件
    search_paths = [FOLDER_PATH]
    
    # 添加所有国家子文件夹
    try:
        for item in os.listdir(FOLDER_PATH):
            item_path = os.path.join(FOLDER_PATH, item)
            if os.path.isdir(item_path):
                search_paths.append(item_path)
    except Exception as e:
        st.warning(f"无法读取文件夹结构: {e}")
    
    # 处理每个可能的文件路径
    for search_path in search_paths:
        # 检查所有匹配日期前缀的文件，包括带国家后缀的
        base_name, ext = os.path.splitext(filename)
        matching_files = []
        
        try:
            # 获取该路径下所有以base_name开头的文件
            all_files = os.listdir(search_path)
            matching_files = [f for f in all_files if f.startswith(base_name)]
        except Exception as e:
            continue
        
        for matching_file in matching_files:
                file_path = os.path.join(search_path, matching_file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except json.JSONDecodeError as e:
                    st.error(f"解码 JSON 文件错误 {file_path}: {e}")
                    continue
                except FileNotFoundError:
                    # 这个错误理论上不会触发，因为上面已经检查了文件是否存在
                    st.error(f"文件未找到 (此错误不应出现): {file_path}")
                    continue
                except Exception as e:
                    st.error(f"读取文件时发生意外错误 {file_path}: {e}")
                    continue

                if not isinstance(data, list):
                    st.warning(f"警告: {file_path} 中的数据不是列表。跳过。")
                    continue

                # 从文件夹路径提取国家信息
                # 例如：JSONs/India/trends_2025-10-14.json → "India"
                folder_country = None
                # 检查search_path是否是FOLDER_PATH的子目录
                if search_path != FOLDER_PATH:
                    # 获取search_path相对于FOLDER_PATH的路径
                    relative_path = os.path.relpath(search_path, FOLDER_PATH)
                    # 获取相对路径的第一部分，即国家名称
                    folder_country = relative_path.split(os.sep)[0]
                    # 验证这个国家名称是否真的存在
                    if not os.path.isdir(os.path.join(FOLDER_PATH, folder_country)):
                        folder_country = None

                for item in data:
                    # 1. 筛选 traffic_num (这里假设是 traffic_num，原代码是 traffic)
                    # 调整阈值为0，显示所有流量数据
                    if item.get('traffic_num', 0) < 0: # 可以根据需要调整阈值
                        continue

                    # 2. 筛选 pub_date 是否为当天 (因为文件名已经限定了日期范围)
                    # 我们仍然可以检查 pub_date，以确保它与文件名代表的日期一致
                    pub_date_str = item.get('pub_date')
                    if not pub_date_str:
                        continue # 没有日期的条目跳过

                    # 解析 pub_date，确认它确实是目标日期
                    item_date = parse_pub_date(pub_date_str)
                    if item_date != target_date:
                        continue # pubDate 与文件日期不匹配，跳过

                    # 3. 提取所需信息
                    search_term = item.get('title', 'N/A')
                    traffic_num = item.get('traffic_num', 0)
                    pub_date = item_date # 使用解析后的日期
                    regions = item.get('regions', [])
                    # 如果JSON中没有国家信息，则使用文件夹名称作为国家
                    country = item.get('country', folder_country)
                    news_list = item.get('news', [])

                    if not news_list:
                         continue # 如果没有 news 项，则跳过

                    # 遍历 news 列表，为每个 news_item 创建一行记录
                    for news_item in news_list:
                        news_title = news_item.get('title', 'N/A')
                        news_source = news_item.get('source', 'N/A')

                        # 添加这一行到结果列表
                        results_list.append({
                            "Search Term": search_term,
                            "News Title": news_title,
                            "News Source": news_source,
                            "Traffic Num": traffic_num,
                            "Pub Date": pub_date,
                            "Regions": regions, # 可以保留整个列表
                            "Country": country # 添加国家信息
                        })

@st.cache_data

def load_data_by_date_range(start_date, end_date, _progress_callback=None):
    """根据日期范围加载数据"""
    all_extracted_data_list = []
    current_date = start_date
    total_days = (end_date - start_date).days + 1
    current_day = 0
    
    while current_date <= end_date:
        # print(f"Attempting to load file for date: {current_date.strftime('%Y-%m-%d')}") # 可选：显示加载进度
        load_and_process_file_for_date(current_date, all_extracted_data_list)
        current_date += timedelta(days=1)
        current_day += 1
        
        # 调用进度回调函数
        if _progress_callback:
            progress = current_day / total_days
            _progress_callback(progress, f"正在加载 {current_date.strftime('%Y-%m-%d')} 的数据...")

    # 按发布日期（降序）和流量数（降序）排序
    all_extracted_data_list.sort(key=lambda x: (x["Pub Date"], x["Traffic Num"]), reverse=True)
    return all_extracted_data_list

@st.cache_data

def estimate_tokens(text, model_name="gpt-4o"):
    """
    估算文本的 token 数量
    """
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base") # fallback
    num_tokens = len(encoding.encode(text))
    return num_tokens



def refresh_model_list(endpoint, api_key):
    """从指定端点刷新模型列表"""
    with st.status("正在刷新模型列表...", expanded=True) as status:
        try:
            st.write("🔄 尝试使用 OpenAI 客户端获取模型列表...")
            # 首先尝试使用 OpenAI 客户端获取模型列表
            try:
                client = OpenAI(base_url=endpoint, api_key=api_key)
                models = client.models.list()
                model_options = [m.id for m in models.data]
                # 更新会话状态中的模型列表
                st.session_state['model_options'] = model_options
                status.update(label="模型列表刷新成功", state="complete", expanded=False)
                st.toast("✅ 模型列表已更新！", icon="🔄")
                return
            except Exception as e:
                # OpenAI 客户端失败，尝试使用通用 HTTP 请求
                st.write(f"⚠️ OpenAI 客户端方式失败，尝试使用 HTTP 请求: {e}")
            
            st.write("🔄 尝试使用 HTTP 请求获取模型列表...")
            # 尝试使用通用 HTTP 请求获取模型列表
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            # 构建模型列表端点 URL
            models_endpoint = endpoint
            if not models_endpoint.endswith('/v1/models'):
                if models_endpoint.endswith('/'):
                    models_endpoint += 'v1/models'
                else:
                    models_endpoint += '/v1/models'
            
            st.write(f"🌐 访问端点: {models_endpoint}")
            response = requests.get(models_endpoint, headers=headers, timeout=10)
            response.raise_for_status()  # 检查响应状态
            
            st.write("📝 解析响应数据...")
            # 解析响应
            data = response.json()
            # 尝试不同的响应格式
            if 'data' in data:
                # OpenAI 格式
                model_options = [m['id'] for m in data['data']]
                st.write(f"✅ 找到 {len(model_options)} 个模型")
            elif 'models' in data:
                # 其他格式，假设 models 字段包含模型列表
                model_options = [m['id'] if 'id' in m else m['name'] for m in data['models']]
                st.write(f"✅ 找到 {len(model_options)} 个模型")
            else:
                # 尝试直接提取模型 ID
                model_options = []
                status.update(label="解析模型列表失败", state="error", expanded=True)
                st.error("无法解析模型列表响应格式")
                return
            
            if model_options:
                # 更新会话状态中的模型列表
                st.session_state['model_options'] = model_options
                status.update(label="模型列表刷新成功", state="complete", expanded=False)
                st.toast("✅ 模型列表已更新！", icon="🔄")
            else:
                status.update(label="未找到模型列表", state="error", expanded=True)
                st.error("未找到模型列表")
        except Exception as e:
            status.update(label="获取模型列表失败", state="error", expanded=True)
            st.error(f"获取模型列表失败: {e}")

@st.cache_data

def generate_simple_markdown_table(df_filtered, max_rows=100000):
    """
    生成简化版的 markdown 表格
    """
    if df_filtered.empty:
        return "No data to display."

    # 限制行数以减少 token
    df_to_use = df_filtered.head(max_rows)

    # 重命名列以符合要求
    df_simple = df_to_use.rename(columns={
        "标题": "news_title",
        "信源": "source",
        "搜索词": "title",
        "流量": "traffic_num",
        "发布日期": "pub_date",
        "地区": "regions",
        "国家": "country"
    })

    # 转换日期格式和流量格式
    df_simple["pub_date"] = df_simple["pub_date"].astype(str)
    df_simple["traffic_num"] = df_simple["traffic_num"].astype(int)

    # 生成 markdown 表格
    lines = []
    lines.append('')
    lines.append("news_title | source | title | traffic_num | pub_date | regions | country")
    lines.append("---|---|---|---|---|---|---")

    for _, row in df_simple.iterrows():
        line = f"{row['news_title']} | {row['source']} | {row['title']} | {row['traffic_num']} | {row['pub_date']} | {row['regions']} | {row['country']}"
        lines.append(line)

    return "\n".join(lines)


# --- Streamlit 应用 ---
st.set_page_config(page_title="Global Trending Now 看板", layout="wide")

# 页面标题和简介
header_container = st.container(border=True)
with header_container:
    st.title("🔍 Global Trending Now")
    st.markdown("### 全球热点搜索趋势分析平台")
    st.markdown("实时追踪全球各国热点搜索趋势，提供数据可视化和AI分析功能")

# 应用功能介绍
features_container = st.container(border=True)
with features_container:
    st.markdown("## 📋 功能简介")
    col_features1, col_features2, col_features3 = st.columns(3)
    with col_features1:
        st.subheader("📊 数据可视化")
        st.markdown("- 国家新闻数量分布")
        st.markdown("- 国家平均流量对比")
        st.markdown("- 流量趋势分析")
        st.markdown("- 新闻来源分布")
    with col_features2:
        st.subheader("🔧 数据筛选")
        st.markdown("- 按国家筛选")
        st.markdown("- 按地区筛选")
        st.markdown("- 按流量阈值筛选")
        st.markdown("- 多维度组合筛选")
    with col_features3:
        st.subheader("🤖 AI 分析")
        st.markdown("- 热点趋势智能分析")
        st.markdown("- 多语言支持")
        st.markdown("- 实时对话交互")
        st.markdown("- 深度洞察生成")

# 使用指南
guide_container = st.container(border=True)
with guide_container:
    st.markdown("## 🚀 使用指南")
    st.markdown("1. **选择日期范围**：在下方选择您要分析的数据时间范围（近3天、7天或30天）")
    st.markdown("2. **应用筛选条件**：根据需要按国家、地区或流量进行数据筛选")
    st.markdown("3. **查看数据可视化**：浏览生成的各类图表，了解全球热点趋势")
    st.markdown("4. **配置AI分析**：在右侧设置AI模型和端点（如需使用自定义端点）")
    st.markdown("5. **启动AI分析**：点击'启动AI分析'按钮，获取AI生成的深度洞察")
    st.markdown("6. **与AI对话**：根据分析结果，继续与AI进行深入讨论")

# 初始化 session state 来存储数据
if 'data' not in st.session_state:
    st.session_state['data'] = []
if 'selected_date_range' not in st.session_state:
    st.session_state['selected_date_range'] = '7d' # 默认为近7天
if 'df' not in st.session_state:
    st.session_state['df'] = None
if 'df_filtered' not in st.session_state:
    st.session_state['df_filtered'] = None
if 'ai_active' not in st.session_state:
    st.session_state['ai_active'] = False
if 'ai_messages' not in st.session_state:
    st.session_state['ai_messages'] = []
if 'token_count' not in st.session_state:
    st.session_state['token_count'] = 0
if 'ai_client' not in st.session_state:
    st.session_state['ai_client'] = None

# 日期范围选择区域 - 更突出的位置
st.markdown("## 📅 选择数据日期范围")
date_container = st.container(border=True)
with date_container:
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("近 3 天", width='stretch', type="primary" if st.session_state.selected_date_range == '3d' else "secondary"):
            start_date = (datetime.now().date() - timedelta(days=3))
            end_date = datetime.now().date()
            total_days = (end_date - start_date).days + 1
            
            # 创建进度条和状态容器
            with st.status(f"正在加载近3天数据...", expanded=True) as status:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def progress_callback(progress, message):
                    progress_bar.progress(progress)
                    status_text.text(message)
                
                st.session_state['data'] = load_data_by_date_range(start_date, end_date, progress_callback)
                st.session_state['selected_date_range'] = '3d'
                # 重置 AI 状态
                st.session_state['ai_active'] = False
                st.session_state['ai_messages'] = []
                st.session_state['ai_client'] = None
                
                status.update(label="近3天数据加载完成", state="complete", expanded=False)
                st.toast("✅ 近3天数据加载完成！", icon="📊")
                st.rerun()
    with col2:
        if st.button("近 7 天", width='stretch', type="primary" if st.session_state.selected_date_range == '7d' else "secondary"):
            start_date = (datetime.now().date() - timedelta(days=7))
            end_date = datetime.now().date()
            total_days = (end_date - start_date).days + 1
            
            # 创建进度条和状态容器
            with st.status(f"正在加载近7天数据...", expanded=True) as status:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def progress_callback(progress, message):
                    progress_bar.progress(progress)
                    status_text.text(message)
                
                st.session_state['data'] = load_data_by_date_range(start_date, end_date, progress_callback)
                st.session_state['selected_date_range'] = '7d'
                # 重置 AI 状态
                st.session_state['ai_active'] = False
                st.session_state['ai_messages'] = []
                st.session_state['ai_client'] = None
                
                status.update(label="近7天数据加载完成", state="complete", expanded=False)
                st.toast("✅ 近7天数据加载完成！", icon="📊")
                st.rerun()
    with col3:
        if st.button("近 30 天", width='stretch', type="primary" if st.session_state.selected_date_range == '30d' else "secondary"):
            start_date = (datetime.now().date() - timedelta(days=30))
            end_date = datetime.now().date()
            total_days = (end_date - start_date).days + 1
            
            # 创建进度条和状态容器
            with st.status(f"正在加载近30天数据...", expanded=True) as status:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def progress_callback(progress, message):
                    progress_bar.progress(progress)
                    status_text.text(message)
                
                st.session_state['data'] = load_data_by_date_range(start_date, end_date, progress_callback)
                st.session_state['selected_date_range'] = '30d'
                # 重置 AI 状态
                st.session_state['ai_active'] = False
                st.session_state['ai_messages'] = []
                st.session_state['ai_client'] = None
                
                status.update(label="近30天数据加载完成", state="complete", expanded=False)
                st.toast("✅ 近30天数据加载完成！", icon="📊")
                st.rerun()

# 如果 session state 中没有数据，则加载默认的近7天数据
if not st.session_state['data']:
    start_date = (datetime.now().date() - timedelta(days=7))
    end_date = datetime.now().date()
    
    # 创建进度条和状态容器
    with st.status("正在加载默认数据（近7天）...", expanded=True) as status:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def progress_callback(progress, message):
            progress_bar.progress(progress)
            status_text.text(message)
        
        st.session_state['data'] = load_data_by_date_range(start_date, end_date, progress_callback)
        st.session_state['selected_date_range'] = '7d'
        
        status.update(label="默认数据加载完成", state="complete", expanded=False)
        st.toast("✅ 默认数据加载完成！", icon="📊")

# 显示加载的数据
if st.session_state['data']:
    st.caption(f"数据范围: {min(item['Pub Date'] for item in st.session_state['data'])} 至 {max(item['Pub Date'] for item in st.session_state['data'])}，共找到 {len(st.session_state['data'])} 条相关新闻记录")
    st.caption(f"")

    # 创建 DataFrame 以便更好地展示
    import pandas as pd
    df_data = []
    for item in st.session_state['data']:
        regions_list = item["Regions"]
        regions_str = "; ".join(regions_list)
        # 处理国家信息，可能是字符串或集合
        country_info = item["Country"]
        if isinstance(country_info, (set, list)):
            country_str = "; ".join(country_info)
        else:
            country_str = country_info if country_info else "未知"
        df_data.append({
            "搜索词": item["Search Term"],
            "标题": item["News Title"],
            "信源": item["News Source"],
            "流量": item["Traffic Num"],
            "发布日期": item["Pub Date"],
            "地区": regions_str,
            "地区数量": len(regions_list),
            "国家": country_str
        })

    df = pd.DataFrame(df_data)
    st.session_state['df'] = df

    # --- 数据概览统计卡片 ---
    st.markdown("## 📊 数据概览")
    stats_container = st.container(border=True)
    with stats_container:
        # 第一行统计卡片：核心指标
        col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
        
        with col_stats1:
            total_records = len(df)
            st.metric("总新闻记录数", f"{total_records:,}")
        
        with col_stats2:
            unique_countries = df["国家"].nunique()
            st.metric("涉及国家数量", unique_countries)
        
        with col_stats3:
            avg_traffic = df["流量"].mean()
            st.metric("平均流量", f"{int(avg_traffic):,}")
        
        with col_stats4:
            unique_sources = df["信源"].nunique()
            st.metric("新闻来源数量", unique_sources)
        
        # 第二行统计卡片：国家相关指标
        col_stats5, col_stats6, col_stats7, col_stats8 = st.columns(4)
        
        with col_stats5:
            # 流量最高的国家
            top_traffic_country = df.groupby("国家")["流量"].sum().idxmax()
            top_traffic_value = df.groupby("国家")["流量"].sum().max()
            st.metric("流量最高的国家", top_traffic_country)
            st.caption(f"总流量: {int(top_traffic_value):,}")
        
        with col_stats6:
            # 新闻记录最多的国家
            top_news_country = df.groupby("国家").size().idxmax()
            top_news_count = df.groupby("国家").size().max()
            st.metric("新闻最多的国家", top_news_country)
            st.caption(f"总记录: {top_news_count:,}")
        
        with col_stats7:
            # 平均每条新闻的流量
            avg_traffic_per_news = df["流量"].sum() / len(df)
            st.metric("平均每条新闻流量", f"{int(avg_traffic_per_news):,}")
        
        with col_stats8:
            # 不同搜索词的数量
            unique_search_terms = df["搜索词"].nunique()
            st.metric("独特搜索词数量", unique_search_terms)
    
    # --- 筛选功能 ---
    st.markdown("## 🔍 数据筛选")
    
    # 创建筛选区域的容器
    filter_container = st.container(border=True)
    
    with filter_container:
        st.markdown("### 筛选条件")
        st.markdown("根据您的需求选择筛选条件，系统将实时更新数据展示和可视化结果")
        
        # 第一行筛选条件：主要筛选器
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            # 从实际数据中获取所有国家列表
            all_countries = df["国家"].unique().tolist()
            # 确保列表不为空
            if not all_countries:
                all_countries = []
            # 添加"所有国家"选项到开头
            all_countries.insert(0, "所有国家")
            country_filter = st.selectbox(
                "🌍 按国家筛选", 
                all_countries, 
                index=0, 
                key="country_filter",
                help="选择特定国家或查看所有国家的数据"
            )
        with col_f2:
            region_filter = st.text_input(
                "📍 按地区筛选", 
                "", 
                key="region_filter", 
                placeholder="例如: 加利福尼亚州, 纽约",
                help="支持多个地区，用逗号分隔"
            )
        with col_f3:
            min_traffic_filter = st.number_input(
                "📊 最低流量筛选", 
                min_value=0, 
                value=0, 
                step=100, 
                key="min_traffic_filter",
                help="筛选流量大于等于指定值的数据"
            )
        
        # 添加清除筛选按钮和筛选信息
        col_clear, col_info = st.columns([1, 3])
        with col_clear:
            if st.button("🗑️ 清除筛选", type="secondary", width='stretch'):
                with st.spinner("正在清除筛选条件..."):
                    # 重置所有筛选器
                    st.session_state['country_filter'] = "所有国家"
                    st.session_state['region_filter'] = ""
                    st.session_state['min_traffic_filter'] = 0
                    st.toast("✅ 筛选条件已清除！", icon="🗑️")
                    st.rerun()
        with col_info:
            active_filters = []
            if country_filter != "所有国家":
                active_filters.append(f"国家: {country_filter}")
            if region_filter:
                active_filters.append(f"地区: {region_filter}")
            if min_traffic_filter > 0:
                active_filters.append(f"最低流量: {min_traffic_filter}")
            
            if active_filters:
                st.info(f"当前激活的筛选条件: {', '.join(active_filters)}")
            else:
                st.info("未应用任何筛选条件，显示所有数据")

    with st.spinner("正在应用筛选条件..."):
        df_current = df.copy()
        # 国家筛选
        if country_filter != "所有国家":
            df_current = df_current[df_current["国家"] == country_filter]
        
        # 地区筛选
        if region_filter:
            regions_to_filter = [r.strip() for r in region_filter.split(",") if r.strip()]
            mask = False
            for r in regions_to_filter:
                mask = mask | df_current["地区"].str.contains(r, case=False, na=False)
            df_current = df_current[mask]
        
        # 最低流量筛选
        if min_traffic_filter > 0:
            df_current = df_current[df_current["流量"] >= min_traffic_filter]

        # 检查是否有筛选条件
        has_active_filters = (country_filter != "所有国家") or region_filter or (min_traffic_filter > 0)
        
        st.session_state['df_filtered'] = df_current
        # 显示筛选结果通知
        if has_active_filters:
            st.toast(f"✅ 筛选完成！共找到 {len(df_current)} 条记录", icon="🔍")
        else:
            st.toast("✅ 已显示所有数据", icon="📊")
    
    # 显示筛选结果统计
    filter_stats = []
    if country_filter != "所有国家":
        filter_stats.append(f"国家: {country_filter}")
    if region_filter:
        filter_stats.append(f"地区: {region_filter}")
    if min_traffic_filter > 0:
        filter_stats.append(f"最低流量: {min_traffic_filter}")
    
    if filter_stats:
        st.caption(f"当前筛选条件: {', '.join(filter_stats)} | 共 {len(df_current)} 条记录")
    else:
        st.caption(f"未应用筛选条件 | 共 {len(df_current)} 条记录")

    # --- 国家数据可视化图表 ---
    if not df_current.empty:
        st.markdown("## 📈 国家数据可视化")
        
        # 创建图表容器
        chart_container = st.container(border=True)
        
        with chart_container:
            # 设置图表样式，确保视觉一致性
            sns.set_style("darkgrid")
            sns.set_palette("deep")
            sns.set_context("notebook", font_scale=1.0)
            
            # 设置统一的图表配置
            plt.rcParams.update({
                'font.size': 12,
                'axes.titlesize': 14,
                'axes.labelsize': 12,
                'xtick.labelsize': 10,
                'ytick.labelsize': 10,
                'legend.fontsize': 10,
                'figure.figsize': (10, 6),
                'font.sans-serif': ['SimHei', 'DejaVu Sans', 'Arial Unicode MS', 'WenQuanYi Micro Hei'],  # 添加支持中文的字体
                'axes.unicode_minus': False  # 解决负号显示问题
            })
            
            # 第一行图表：国家新闻数量和平均流量
            st.markdown("### Country Core Metrics Comparison")
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                with st.spinner("正在生成国家新闻数量图表..."):
                    # 按国家分组统计新闻数量
                    country_news_count = df_current.groupby("国家").size().reset_index(name="新闻数量")
                    country_news_count = country_news_count.sort_values(by="新闻数量", ascending=False).head(10)
                    
                    # 创建图表
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.barplot(x="新闻数量", y="国家", data=country_news_count, hue="国家", palette="viridis", ax=ax, legend=False)
                    ax.set_xlabel("Number of News Records")
                    ax.set_ylabel("国家")
                    
                    # 根据筛选条件调整标题
                    if country_filter == "所有国家":
                        ax.set_title("News Records by Country")
                    else:
                        ax.set_title(f"{country_filter} 新闻记录数量")
                    
                    # 在柱状图上添加数值标签
                    for i, v in enumerate(country_news_count["新闻数量"]):
                        ax.text(v + 0.5, i, str(v), va='center', fontsize=10)
                    
                    # 设置图表边距
                    plt.tight_layout()
                    st.pyplot(fig)
            
            with col_chart2:
                with st.spinner("正在生成国家平均流量图表..."):
                    # 按国家分组计算平均流量
                    country_avg_traffic = df_current.groupby("国家")["流量"].mean().reset_index(name="平均流量")
                    country_avg_traffic["平均流量"] = country_avg_traffic["平均流量"].astype(int)
                    country_avg_traffic = country_avg_traffic.sort_values(by="平均流量", ascending=False).head(10)
                    
                    # 创建图表
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.barplot(x="平均流量", y="国家", data=country_avg_traffic, hue="国家", palette="plasma", ax=ax, legend=False)
                    ax.set_xlabel("Average Traffic")
                    ax.set_ylabel("国家")
                    
                    # 根据筛选条件调整标题
                    if country_filter == "所有国家":
                        ax.set_title("Average Traffic by Country")
                    else:
                        ax.set_title(f"{country_filter} 平均流量")
                    
                    # 在柱状图上添加数值标签
                    for i, v in enumerate(country_avg_traffic["平均流量"]):
                        ax.text(v + 0.5, i, f"{v:,}", va='center', fontsize=10)
                    
                    # 设置图表边距
                    plt.tight_layout()
                    st.pyplot(fig)

            # 第二行图表：流量趋势和新闻来源分布
            st.markdown("### Traffic Trend and Source Analysis")
            col_chart3, col_chart4 = st.columns(2)
            
            with col_chart3:
                with st.spinner("正在生成流量趋势图表..."):
                    # 按日期的流量趋势（如果选择了单个国家或数据量足够）
                    if len(df_current) > 5:
                        # 按日期分组计算总流量
                        daily_traffic = df_current.groupby("发布日期")["流量"].sum().reset_index(name="总流量")
                        daily_traffic = daily_traffic.sort_values(by="发布日期")
                        
                        # 创建图表
                        fig, ax = plt.subplots(figsize=(10, 6))
                        sns.lineplot(x="发布日期", y="总流量", data=daily_traffic, marker='o', ax=ax, color="#4C72B0")
                        ax.set_xlabel("Date")
                        ax.set_ylabel("Total Traffic")
                        
                        # 根据筛选条件调整标题
                        if country_filter == "所有国家":
                            ax.set_title("Global Traffic Trend")
                        else:
                            ax.set_title(f"{country_filter} 流量趋势")
                        
                        # 优化日期显示
                        plt.xticks(rotation=45, fontsize=8)
                        plt.grid(True, alpha=0.3)
                        
                        # 设置图表边距
                        plt.tight_layout()
                        st.pyplot(fig)
                    else:
                        st.info("数据量不足，无法显示流量趋势")
            
            with col_chart4:
                with st.spinner("正在生成新闻来源分布图表..."):
                    # 新闻来源分布饼图
                    st.markdown("#### News Source Distribution")
                    source_distribution = df_current.groupby("信源").size().reset_index(name="数量")
                    source_distribution = source_distribution.sort_values(by="数量", ascending=False).head(8)
                    
                    # 如果有超过8个来源，将剩余的合并为"其他"
                    if len(source_distribution) >= 8:
                        top_sources = source_distribution.head(7)
                        other_count = source_distribution.tail(len(source_distribution) - 7)["数量"].sum()
                        if other_count > 0:
                            top_sources.loc[len(top_sources)] = ["其他", other_count]
                        source_distribution = top_sources
                    
                    # 创建饼图
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.pie(source_distribution["数量"], labels=source_distribution["信源"], autopct='%1.1f%%', startangle=90)
                    ax.axis('equal')  # 确保饼图是圆形
                    
                    # 根据筛选条件调整标题
                    if country_filter == "所有国家":
                        ax.set_title("Global News Source Distribution")
                    else:
                        ax.set_title(f"{country_filter} 新闻来源分布")
                    
                    # 设置图表边距
                    plt.tight_layout()
                    st.pyplot(fig)
            
            # 第三行图表：流量分布和地区分布
            st.markdown("### Traffic and Regional Distribution Analysis")
            col_chart5, col_chart6 = st.columns(2)
            
            with col_chart5:
                with st.spinner("正在生成流量分布图表..."):
                    # 流量分布箱线图
                    st.markdown("#### Traffic Distribution")
                    if country_filter == "所有国家":
                        # 多国家流量分布对比
                        if len(df_current["国家"].unique()) > 1:
                            fig, ax = plt.subplots(figsize=(10, 6))
                            sns.boxplot(x="国家", y="流量", data=df_current, ax=ax, palette="Set3")
                            ax.set_xlabel("国家")
                            ax.set_ylabel("Traffic")
                            ax.set_title("Traffic Distribution by Country")
                            plt.xticks(rotation=45, fontsize=8)
                            plt.tight_layout()
                            st.pyplot(fig)
                        else:
                            # 单个国家流量分布
                            fig, ax = plt.subplots(figsize=(10, 6))
                            sns.boxplot(y="流量", data=df_current, ax=ax, palette="Set3")
                            ax.set_ylabel("Traffic")
                            ax.set_title(f"{country_filter} 流量分布")
                            plt.tight_layout()
                            st.pyplot(fig)
                    else:
                        # 单个国家不同地区的流量分布
                        if "地区" in df_current.columns and len(df_current["地区"].unique()) > 1:
                            fig, ax = plt.subplots(figsize=(10, 6))
                            # 只显示流量最大的前10个地区
                            top_regions = df_current.groupby("地区")["流量"].sum().nlargest(10).index
                            df_top_regions = df_current[df_current["地区"].isin(top_regions)]
                            sns.boxplot(x="地区", y="流量", data=df_top_regions, ax=ax, palette="Set3")
                            ax.set_xlabel("Region")
                            ax.set_ylabel("Traffic")
                            ax.set_title(f"{country_filter} 各地区流量分布")
                            plt.xticks(rotation=45, fontsize=8)
                            plt.tight_layout()
                            st.pyplot(fig)
                        else:
                            # 单个国家流量分布（无地区数据或地区数据不足）
                            fig, ax = plt.subplots(figsize=(10, 6))
                            sns.boxplot(y="流量", data=df_current, ax=ax, palette="Set3")
                            ax.set_ylabel("流量")
                            ax.set_title(f"{country_filter} 流量分布")
                            plt.tight_layout()
                            st.pyplot(fig)
            
            with col_chart6:
                with st.spinner("正在生成地区分布图表..."):
                    # 国家地区分布（仅当选择单个国家时）
                    if country_filter != "所有国家" and len(df_current) > 0:
                        # 按地区分组统计新闻数量
                        region_news_count = df_current.groupby("地区").size().reset_index(name="新闻数量")
                        region_news_count = region_news_count.sort_values(by="新闻数量", ascending=False).head(10)
                        
                        # 创建图表
                        fig, ax = plt.subplots(figsize=(10, 6))
                        sns.barplot(x="新闻数量", y="地区", data=region_news_count, hue="地区", palette="RdBu_r", ax=ax, legend=False)
                        ax.set_xlabel("Number of News Records")
                        ax.set_ylabel("Region")
                        ax.set_title(f"News Records by Region")
                        
                        # 在柱状图上添加数值标签
                        for i, v in enumerate(region_news_count["新闻数量"]):
                            ax.text(v + 0.5, i, str(v), va='center', fontsize=10)
                        
                        # 设置图表边距
                        plt.tight_layout()
                        st.pyplot(fig)
                    else:
                        # 当选择所有国家时，显示地区数量分布
                        region_count = df_current.groupby("国家")["地区数量"].mean().reset_index(name="平均地区数量")
                        region_count = region_count.sort_values(by="平均地区数量", ascending=False).head(10)
                        
                        fig, ax = plt.subplots(figsize=(10, 6))
                        sns.barplot(x="平均地区数量", y="国家", data=region_count, hue="国家", palette="Purples", ax=ax, legend=False)
                        ax.set_xlabel("Average Number of Regions")
                        ax.set_ylabel("国家")
                        ax.set_title("Average Regions Involved by Country")
                        
                        # 在柱状图上添加数值标签
                        for i, v in enumerate(region_count["平均地区数量"]):
                            ax.text(v + 0.05, i, f"{v:.1f}", va='center', fontsize=10)
                        
                        # 设置图表边距
                        plt.tight_layout()
                        st.pyplot(fig)
            
            # 重置Matplotlib设置，避免影响后续图表
            plt.close('all')
            sns.reset_orig()
    else:
        st.info("当前筛选条件下没有数据可用于可视化")

    # --- 始终显示原始表格（可排序）---
    st.subheader("📊 数据表格")
    if region_filter or min_traffic_filter > 0:
        st.caption(f"筛选结果: 共 {len(df_current)} 条记录")
    else:
        st.caption(f"共 {len(df)} 条记录")
    
    # 调整列顺序，将国家和地区列放在前面
    columns = [
        "国家", "地区", "搜索词", "标题", "信源", "流量", "发布日期", "地区数量"
    ]
    
    # 确保所有列都存在
    available_columns = [col for col in columns if col in df_current.columns]
    
    # 显示调整后的表格
    st.dataframe(
        df_current[available_columns], 
        width='stretch', 
        height=600,  # 固定高度避免页面太长
        column_config={
            "国家": st.column_config.Column(
                "国家",
                width="medium",
                help="新闻来源国家"
            ),
            "地区": st.column_config.Column(
                "地区",
                width="wide",
                help="新闻来源地区"
            ),
            "搜索词": st.column_config.Column(
                "搜索词",
                width="medium",
                help="热点搜索词"
            ),
            "标题": st.column_config.Column(
                "新闻标题",
                width="large",
                help="新闻标题"
            ),
            "信源": st.column_config.Column(
                "新闻来源",
                width="medium",
                help="新闻发布来源"
            ),
            "流量": st.column_config.NumberColumn(
                "流量",
                width="small",
                help="新闻流量数值",
                format="%d"
            ),
            "发布日期": st.column_config.DateColumn(
                "发布日期",
                width="small",
                help="新闻发布日期"
            ),
            "地区数量": st.column_config.NumberColumn(
                "涉及地区数量",
                width="small",
                help="该新闻涉及的地区数量"
            )
        }
    )

    # --- AI 功能区域 ---
    if st.session_state['data']:  # 仅当有数据时才显示 AI 功能
        st.subheader("🤖 AI 分析功能")

        # AI 配置设置
        with st.expander("⚙️ AI 配置", expanded=True):
            # 初始化会话状态中的 AI 配置
            if 'ai_config' not in st.session_state:
                st.session_state['ai_config'] = {
                    'api_key': DEFAULT_API_KEY,
                    'endpoint': DEFAULT_ENDPOINT,
                    'model': DEFAULT_MODEL,
                    'supplier': DEFAULT_SUPPLIER
                }
            if 'model_options' not in st.session_state:
                st.session_state['model_options'] = get_provider_default_models(DEFAULT_SUPPLIER)
            
            # 模型供应商选择
            provider_names = get_provider_names()
            model_supplier = st.selectbox(
                "模型供应商", 
                provider_names, 
                index=provider_names.index(st.session_state['ai_config'].get('supplier', DEFAULT_SUPPLIER)),
                key="model_supplier"
            )
            
            # 当供应商变化时更新配置并自动获取模型列表
            if model_supplier != st.session_state['ai_config'].get('supplier'):
                st.session_state['ai_config']['supplier'] = model_supplier
                # 根据供应商设置默认端点
                default_endpoint = get_provider_default_endpoint(model_supplier)
                st.session_state['ai_config']['endpoint'] = default_endpoint
                # 设置默认模型列表
                default_models = get_provider_default_models(model_supplier)
                st.session_state['model_options'] = default_models
                # 如果有默认模型，设置第一个为当前模型
                if default_models:
                    st.session_state['ai_config']['model'] = default_models[0]
                # 自动刷新模型列表
                if model_supplier != "Custom" and st.session_state['ai_config'].get('api_key'):
                    refresh_model_list(st.session_state['ai_config']['endpoint'], st.session_state['ai_config']['api_key'])
            
            # 端点规范化函数
            def normalize_endpoint(endpoint):
                """规范化端点URL，确保符合标准格式"""
                if not endpoint:
                    return endpoint
                
                # 添加协议（如果缺少）
                if not endpoint.startswith('http://') and not endpoint.startswith('https://'):
                    endpoint = 'https://' + endpoint
                
                # 移除尾部斜杠
                endpoint = endpoint.rstrip('/')
                
                # 确保以 /v1 结尾
                if not endpoint.endswith('/v1'):
                    endpoint += '/v1'
                
                return endpoint
            
            # 根据供应商显示不同的配置选项
            if model_supplier == "Custom":
                # 自定义供应商显示端点输入
                ai_endpoint = st.text_input(
                    "自定义端点", 
                    value=st.session_state['ai_config'].get('endpoint', DEFAULT_ENDPOINT), 
                    key="ai_endpoint"
                )
                if ai_endpoint != st.session_state['ai_config'].get('endpoint'):
                    # 规范化端点
                    normalized_endpoint = normalize_endpoint(ai_endpoint)
                    st.session_state['ai_config']['endpoint'] = normalized_endpoint
                    # 显示规范化后的端点
                    st.info(f"规范化后的端点: {normalized_endpoint}")
            else:
                # 默认供应商隐藏自定义端点，使用配置中的默认端点
                default_endpoint = get_provider_default_endpoint(model_supplier)
                st.session_state['ai_config']['endpoint'] = default_endpoint
                # 显示当前端点信息
                st.info(f"当前端点: {default_endpoint}")
            
            # API Key 输入
            ai_api_key = st.text_input(
                "API Key", 
                type="password", 
                value=st.session_state['ai_config'].get('api_key', DEFAULT_API_KEY), 
                key="ai_api_key"
            )
            if ai_api_key != st.session_state['ai_config'].get('api_key'):
                st.session_state['ai_config']['api_key'] = ai_api_key
                # 当 API Key 变化时，如果不是自定义供应商，自动刷新模型列表
                if model_supplier != "Custom":
                    refresh_model_list(st.session_state['ai_config']['endpoint'], ai_api_key)
            
            # 模型选择和刷新
            col_model, col_refresh = st.columns([3, 1])
            with col_model:
                # 获取模型列表
                model_options = st.session_state.get('model_options', get_provider_default_models(model_supplier))
                # 确保模型选项不为空
                if not model_options:
                    model_options = ["请先刷新模型列表"]
                # 确保当前模型在选项列表中
                current_model = st.session_state['ai_config'].get('model')
                if current_model and current_model not in model_options:
                    model_options.insert(0, current_model)
                ai_model = st.selectbox(
                    "选择模型", 
                    model_options,
                    index=model_options.index(current_model) if current_model in model_options else 0,
                    key="ai_model"
                )
                if ai_model != current_model:
                    st.session_state['ai_config']['model'] = ai_model
            with col_refresh:
                st.markdown(" ")  # 调整垂直对齐
                if st.button("🔄 刷新模型", key="refresh_models"):
                    current_endpoint = st.session_state['ai_config']['endpoint']
                    current_api_key = st.session_state['ai_config']['api_key']
                    refresh_model_list(current_endpoint, current_api_key)
        
        # 模型测试按钮
        if st.button("🧪 测试模型连通性", key="test_model"):
            test_endpoint = st.session_state['ai_config']['endpoint']
            test_api_key = st.session_state['ai_config']['api_key']
            test_model = st.session_state['ai_config']['model']
            
            if not test_api_key.strip():
                st.error("请先填写 API Key")
            else:
                with st.status("正在测试模型连通性...", expanded=True) as status:
                    try:
                        st.write(f"🌐 测试端点: {test_endpoint}")
                        st.write(f"🤖 测试模型: {test_model}")
                        
                        # 创建临时客户端
                        st.write("🔧 创建测试客户端...")
                        test_client = OpenAI(base_url=test_endpoint, api_key=test_api_key)
                        
                        # 发送测试消息
                        st.write("📝 准备测试消息...")
                        test_messages = [
                            {"role": "system", "content": "你是一个测试助手，只需要回复'测试成功！'即可"},
                            {"role": "user", "content": "测试消息：请回复'测试成功！'"}
                        ]
                        
                        # 调用模型
                        st.write("🚀 调用模型 API...")
                        response = test_client.chat.completions.create(
                            model=test_model,
                            messages=test_messages,
                            stream=False
                        )
                        
                        # 检查响应类型
                        st.write("📊 分析模型响应...")
                        if isinstance(response, str):
                            st.write(f"⚠️ 模型返回字符串格式: {response}")
                            status.update(label="模型测试成功", state="complete", expanded=False)
                            st.toast("✅ 模型连接成功！", icon="🧪")
                        else:
                            # 获取回复内容
                            if hasattr(response, 'choices') and len(response.choices) > 0:
                                if hasattr(response.choices[0], 'message') and hasattr(response.choices[0].message, 'content'):
                                    test_response = response.choices[0].message.content
                                    if test_response:
                                        st.write(f"✅ 模型测试成功！")
                                        st.write(f"回复内容：{test_response}")
                                        status.update(label="模型测试成功", state="complete", expanded=False)
                                        st.toast("✅ 模型测试成功！", icon="🧪")
                                    else:
                                        st.write("⚠️ 模型测试成功，但未返回内容")
                                        status.update(label="模型测试成功", state="complete", expanded=False)
                                        st.toast("⚠️ 模型测试成功，但未返回内容", icon="🧪")
                                else:
                                    st.write("✅ 模型连接成功！")
                                    st.write(f"响应结构: {response}")
                                    status.update(label="模型测试成功", state="complete", expanded=False)
                                    st.toast("✅ 模型连接成功！", icon="🧪")
                            else:
                                st.write("✅ 模型连接成功！")
                                st.write(f"响应结构: {response}")
                                status.update(label="模型测试成功", state="complete", expanded=False)
                                st.toast("✅ 模型连接成功！", icon="🧪")
                    except Exception as e:
                        status.update(label="模型测试失败", state="error", expanded=True)
                        st.error(f"❌ 模型测试失败: {e}")
                        # 添加更多调试信息
                        st.info(f"测试配置：\n端点: {test_endpoint}\n模型: {test_model}")
                        st.toast("❌ 模型测试失败", icon="⚠️")
        
        # 使用会话状态中的配置
        ai_endpoint = st.session_state['ai_config'].get('endpoint', DEFAULT_ENDPOINT)
        ai_api_key = st.session_state['ai_config'].get('api_key', DEFAULT_API_KEY)
        ai_model = st.session_state['ai_config'].get('model', DEFAULT_MODEL)

        if df_current.empty:
                st.error("当前筛选条件下无数据可供分析")
        elif not ai_api_key.strip():
            st.error("请先填写 API Key")
        else:
            # 生成简化表格（用于发送给 AI）
            markdown_table = generate_simple_markdown_table(df_current)
            # st.write("```" +markdown_table+ "```")
            # 拼接发送给 AI 的内容
            user_prompt_with_table = DEFAULT_USER_PROMPT + "\n\n" + markdown_table
            # user_prompt_with_table = "just for test you googit "  # 测试用
            # 估算 Token
            with st.spinner("正在估算 Token 数量..."):
                try:
                    system_tokens = estimate_tokens(DEFAULT_SYSTEM_PROMPT, ai_model)
                    user_tokens = estimate_tokens(user_prompt_with_table, ai_model)
                    total_tokens = system_tokens + user_tokens
                except Exception as e:
                    st.warning(f"Token 估算失败（使用默认模型估算）: {e}")
                    # fallback
                    total_tokens = estimate_tokens(
                        DEFAULT_SYSTEM_PROMPT + "\n\n" + user_prompt_with_table, 
                        "gpt-4o"
                    )
                # 显示 Token 信息（持久显示）
                st.session_state['token_count'] = total_tokens
                
                # 使用更友好的显示方式
                token_info_container = st.container(border=True)
                with token_info_container:
                    st.markdown("### 📊 Token 估算信息")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("系统提示词", f"{system_tokens:,}")
                    with col2:
                        st.metric("用户输入", f"{user_tokens:,}")
                    with col3:
                        st.metric("总计", f"{total_tokens:,}")
                    
                    # 显示 Token 使用情况的进度条
                    max_tokens = DEFAULT_MAX_TOKENS
                    progress = min(total_tokens / max_tokens, 1.0)
                    st.progress(progress)
                    
                    if total_tokens > max_tokens:
                        st.error(f"⚠️ 超过 {max_tokens:,} tokens 限制！可能影响分析效果。")
                    else:
                        remaining = max_tokens - total_tokens
                        st.success(f"✅ 剩余 Token: {remaining:,}")

                
        # 启动分析按钮
        if st.button("🚀 启动 AI 分析", type="primary"):
            if total_tokens > DEFAULT_MAX_TOKENS:
                st.warning(f"⚠️ 超过 {DEFAULT_MAX_TOKENS} tokens 限制！可能影响分析效果。")
                if st.button("❗ 确认继续分析", type="secondary", key="confirm_overlimit"):
                    with st.status("正在启动 AI 分析...", expanded=True) as status:
                        try:
                            st.write("🔧 初始化 AI 客户端...")
                            client = OpenAI(base_url=ai_endpoint, api_key=ai_api_key)
                            st.session_state['ai_client'] = client
                            
                            st.write("📝 准备分析数据...")
                            # 发送给 AI 的消息
                            st.session_state['ai_messages'] = [
                                {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
                                {"role": "user", "content": user_prompt_with_table} # 包含表格
                            ]
                            
                            st.write("🚀 启动分析流程...")
                            st.session_state['ai_active'] = True
                            
                            status.update(label="AI 分析已启动", state="complete", expanded=False)
                            st.toast("✅ AI 分析已启动！", icon="🚀")
                            st.rerun()
                        except Exception as e:
                            status.update(label="AI 分析启动失败", state="error", expanded=True)
                            st.error(f"初始化 AI 客户端失败: {e}")
                            st.toast("❌ AI 分析启动失败", icon="⚠️")
            else:
                # 未超限，直接启动
                with st.status("正在启动 AI 分析...", expanded=True) as status:
                    try:
                        st.write("🔧 初始化 AI 客户端...")
                        client = OpenAI(base_url=ai_endpoint, api_key=ai_api_key)
                        st.session_state['ai_client'] = client
                        
                        st.write("📝 准备分析数据...")
                        # 发送给 AI 的消息
                        st.session_state['ai_messages'] = [
                            {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt_with_table} # 包含表格
                        ]
                        
                        st.write("🚀 启动分析流程...")
                        st.session_state['ai_active'] = True
                        
                        status.update(label="AI 分析已启动", state="complete", expanded=False)
                        st.toast("✅ AI 分析已启动！", icon="🚀")
                        st.rerun()
                    except Exception as e:
                        status.update(label="AI 分析启动失败", state="error", expanded=True)
                        st.error(f"初始化 AI 客户端失败: {e}")
                        st.toast("❌ AI 分析启动失败", icon="⚠️")

        # --- AI 对话区域 ---
        if st.session_state.get('ai_active', False) and st.session_state.get('ai_client', None):
            # 手动添加一点间距
            st.divider()
            st.subheader("💬 AI 对话")

            # 显示已有完整对话
            messages = st.session_state.get('ai_messages', [])
            print(f"DEBUG: 消息历史长度: {len(messages)}")
            
            for msg in messages:
                if msg["role"] == "user":
                    # 检查是否是初始消息（包含表格的消息）
                    if DEFAULT_TABLE_CONTENT_PLACEHOLDER in msg['content'] or "news_title | source" in msg['content']:
                        # 初始消息只显示提示词部分，不显示表格
                        st.markdown(f"🧑‍💻 **You** {DEFAULT_USER_PROMPT}")
                    else:
                        # 后续消息显示实际用户输入
                        st.markdown(f"🧑‍💻 **You:** {msg['content']}")
                elif msg["role"] == "assistant":
                    st.markdown(f"👾 **AI:** {msg['content']}")

            # 检查是否有待处理的 AI 回复（即最后一条是用户消息，但没有对应的 AI 回复）
            last_user_message_idx = -1
            for i in range(len(messages) - 1, -1, -1):
                if messages[i]["role"] == "user":
                    last_user_message_idx = i
                    break

            last_ai_message_idx = -1
            for i in range(len(messages) - 1, -1, -1):
                if messages[i]["role"] == "assistant":
                    last_ai_message_idx = i
                    break

            print(f"DEBUG: 最后用户消息索引: {last_user_message_idx}")
            print(f"DEBUG: 最后AI消息索引: {last_ai_message_idx}")
            print(f"DEBUG: 消息历史内容: {messages}")

            # 继续对话输入
            user_input = st.chat_input("继续与 AI 讨论这些热点...")
            if user_input:
                st.session_state['ai_messages'].append({"role": "user", "content": user_input})
                # 重新运行以触发AI回复生成逻辑
                st.rerun()

            # 如果最后一条是用户消息，且没有 AI 回复，或者最后一条 AI 回复为空，则正在生成
            if last_user_message_idx > last_ai_message_idx or (last_ai_message_idx > -1 and messages[last_ai_message_idx]['content'] == ''):
                # 如果最后一条 AI 回复为空，先删除它
                if last_ai_message_idx > -1 and messages[last_ai_message_idx]['content'] == '':
                    st.session_state['ai_messages'].pop(last_ai_message_idx)
                    print("DEBUG: 删除空的 AI 回复")
                    # 重新获取消息列表和索引
                    messages = st.session_state.get('ai_messages', [])
                    last_ai_message_idx = -1
                
                with st.status("AI 正在分析数据...", expanded=True) as status:
                    try:
                        st.write("🧠 正在处理您的请求...")
                        # 检查 AI 客户端是否存在
                        if not st.session_state['ai_client']:
                            status.update(label="AI 分析失败", state="error", expanded=True)
                            st.error("AI 客户端未初始化")
                            st.toast("❌ AI 分析失败", icon="⚠️")
                        else:
                            st.write("🚀 调用 AI 模型进行分析...")
                            print("DEBUG: 调用 chat.completions.create()")
                            stream = st.session_state['ai_client'].chat.completions.create(
                                model=ai_model,
                                messages=messages, # 包含完整历史（包含表格）
                                stream=True,
                            )
                            
                            st.write("📊 正在接收分析结果...")
                            print("DEBUG: 成功获取流式响应")
                            full_response = ""
                            # 创建一个占位符用于流式显示 AI 回复
                            ai_response_placeholder = st.empty()
                            ai_response_placeholder.markdown("🤖 **AI:** 生成中...")
                            
                            print("DEBUG: 开始接收流式数据")
                            for chunk in stream:
                                print(f"DEBUG: 接收到 chunk: {chunk}")
                                if chunk.choices[0].delta.content is not None:
                                    chunk_content = chunk.choices[0].delta.content
                                    print(f"DEBUG: 接收到内容: '{chunk_content}'")
                                    full_response += chunk_content
                                    print(f"DEBUG: 当前 full_response: '{full_response}'")
                                    # 实时更新占位符
                                    ai_response_placeholder.markdown(f"🤖 **AI:** {full_response}")
                            
                            print(f"DEBUG: 流式结束，最终 full_response: '{full_response}'")
                            print(f"DEBUG: full_response 长度: {len(full_response)}")
                            
                            # 循环结束后，保存完整的 AI 回复
                            st.session_state['ai_messages'].append({"role": "assistant", "content": full_response})
                            print(f"DEBUG: 会话状态消息长度: {len(st.session_state['ai_messages'])}")
                            print(f"DEBUG: 最后一条消息: {st.session_state['ai_messages'][-1]}")
                            
                            status.update(label="AI 分析完成", state="complete", expanded=False)
                            st.toast("✅ AI 分析完成！", icon="📊")
                            # 移除占位符
                            ai_response_placeholder.empty()
                            print("DEBUG: 显示最终回复完成")
                            # 重新运行以刷新界面，显示新消息
                            st.rerun()
                    except Exception as e:
                        print(f"DEBUG: 异常发生: {e}")
                        status.update(label="AI 分析失败", state="error", expanded=True)
                        st.error(f"AI 调用失败: {e}")
                        st.toast("❌ AI 分析失败", icon="⚠️")
                        # 可以选择移除待处理的消息，或保留以便重试
                        # st.session_state['ai_messages'].pop() # 移除最后的用户消息
            # 如果有 AI 回复，但未显示（比如刚从流式结束），则显示它
            elif last_ai_message_idx == len(messages) - 1:
                # 最后一条是 AI 消息，但上面的循环已经显示过了，无需重复
                # 这个分支主要是为了逻辑完整性
                pass

else:
    st.info("在所选日期范围内未找到任何数据或相关文件。")

# 可选：提供一个手动刷新按钮
# if st.button("Refresh Data"):
#     start_date = (datetime.now().date() - timedelta(days=7)) # 或根据当前选择的范围
#     end_date = datetime.now().date()
#     st.session_state['data'] = load_data_by_date_range(start_date, end_date)
#     st.rerun()