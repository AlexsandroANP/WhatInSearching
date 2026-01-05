import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import json
import os
import logging
import random
import time
from email.utils import parsedate_to_datetime

# 导入配置
from config import current_config

# 配置日志
logger = logging.getLogger(__name__)

# Google Trends 命名空间
HT_NS = 'https://trends.google.com/trending/rss'

def get_output_filename(country_name: str = None):
    """
    生成当天的输出文件名，格式为 OUTPUT_DIR/[country_name]/OUTPUT_FILE_PREFIX_YYYY-MM-DD.OUTPUT_FILE_EXTENSION
    
    Args:
        country_name (str, optional): 国家名称，如果为None则保存在根目录
    
    Returns:
        str: 输出文件的完整路径
    """
    ## 确保输出目录存在
    output_dir = current_config.OUTPUT_DIR
    if country_name:
        output_dir = os.path.join(output_dir, country_name)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    return os.path.join(
        output_dir, 
        f"{current_config.OUTPUT_FILE_PREFIX}{today_str}{current_config.OUTPUT_FILE_EXTENSION}"
    )

def parse_xml_to_dict(xml_content: str, region_name: str, country_name: str = None) -> list:
    """
    解析 XML 内容并返回一个包含趋势数据的字典列表。
    每个字典代表一个趋势项，包含标题、热度、时间、区域、国家等信息。
    
    Args:
        xml_content (str): XML格式的趋势数据
        region_name (str): 数据所属的区域名称
        country_name (str, optional): 数据所属的国家名称
    
    Returns:
        list: 包含趋势数据的字典列表
    """
    trends = []
    try:
        root = ET.fromstring(xml_content)
        channel = root.find('channel')
        if channel is None:
            logger.warning(f"在 {region_name} 的数据中未找到 channel 元素")
            return trends

        items = channel.findall('item')
        for item in items:
            title_elem = item.find('title')
            title = title_elem.text.strip() if title_elem is not None and title_elem.text else '无标题'

            pub_date_elem = item.find('pubDate')
            pub_date_str = pub_date_elem.text if pub_date_elem is not None and pub_date_elem.text else datetime.now(timezone.utc).isoformat()
            
            # 尝试解析 RSS 格式的日期 (e.g., "Mon, 13 Oct 2025 01:40:00 -0700")
            try:
                # parsedate_to_datetime 可以处理 RFC 2822 格式
                pub_date = parsedate_to_datetime(pub_date_str)
                if pub_date.tzinfo is None:
                    # 如果解析出的时间没有时区信息，假设为 UTC
                    pub_date = pub_date.replace(tzinfo=timezone.utc)
            except (ValueError, TypeError) as e:
                logger.warning(f"无法解析 {region_name} - {title} 的日期: {pub_date_str} ({e}), 使用当前时间")
                pub_date = datetime.now(timezone.utc)

            traffic_elem = item.find(f'{{{HT_NS}}}approx_traffic')
            traffic_str = traffic_elem.text if traffic_elem is not None and traffic_elem.text else '0'
            # 移除流量字符串中的逗号和加号，然后转换为整数
            traffic_num = int(traffic_str.replace(',', '').replace('+', '')) if traffic_str.replace(',', '').replace('+', '').isdigit() else 0

            picture_elem = item.find(f'{{{HT_NS}}}picture')
            picture = picture_elem.text if picture_elem is not None and picture_elem.text else ''

            # 解析相关新闻
            news_items = item.findall(f'{{{HT_NS}}}news_item')
            news_list = []
            for news_item in news_items:
                title_elem = news_item.find(f'{{{HT_NS}}}news_item_title')
                url_elem = news_item.find(f'{{{HT_NS}}}news_item_url')
                source_elem = news_item.find(f'{{{HT_NS}}}news_item_source')
                pic_elem = news_item.find(f'{{{HT_NS}}}news_item_picture')

                news_list.append({
                    'title': title_elem.text if title_elem is not None and title_elem.text else '',
                    'url': url_elem.text if url_elem is not None and url_elem.text else '',
                    'source': source_elem.text if source_elem is not None and source_elem.text else '未知来源',
                    'picture': pic_elem.text if pic_elem is not None and pic_elem.text else ''
                })

            trends.append({
                'title': title,
                'traffic_str': traffic_str,  # 保留原始格式，用于后续处理
                'traffic_num': traffic_num,  # 用于比较和排序的数值
                'pub_date_str': pub_date_str, # 保留原始格式，用于后续处理
                'pub_date': pub_date.isoformat(), # 保存为 ISO 格式字符串
                'picture': picture,
                'news': news_list,
                'regions': [region_name], # 初始化区域列表
                'country': country_name if country_name else None # 添加国家信息
            })
    except ET.ParseError as e:
        logger.error(f"解析 {region_name} 的 XML 数据时出错: {e}")
        return [] # 解析失败返回空列表
    except Exception as e:
        logger.error(f"处理 {region_name} 的 XML 数据时发生未知错误: {e}")
        return [] # 处理失败返回空列表
    return trends

def fetch_single_region_with_session(session: requests.Session, region: dict, country_name: str = None, max_retries: int = None) -> list:
    """
    使用同一个 session 拉取单个区域的 RSS 数据，并实现重试逻辑。
    
    Args:
        session (requests.Session): 用于请求的会话对象
        region (dict): 包含区域信息的字典，需包含 'code' 和 'name' 键
        country_name (str, optional): 数据所属的国家名称
        max_retries (int, optional): 最大重试次数，如果为 None 则使用配置中的值
        
    Returns:
        list: 包含趋势数据的字典列表
    """
    # 使用配置的URL模板
    url = current_config.GOOGLE_TRENDS_RSS_URL.format(code=region['code'])
    
    # 如果没有提供重试次数，使用配置中的值
    if max_retries is None:
        max_retries = current_config.REQUEST_MAX_RETRIES
    
    for attempt in range(max_retries):
        try:
            logger.info(f"正在拉取 {region['name']} ({region['code']}) 的数据... (尝试 {attempt + 1}/{max_retries})")
            
            response = session.get(url, timeout=current_config.REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                logger.debug(f"{region['name']} 数据拉取成功，长度: {len(response.text)}")
                return parse_xml_to_dict(response.text, region['name'], country_name)
            elif response.status_code == 429:
                logger.warning(f"收到 429 错误，为 {region['name']} 等待更长时间后重试...")
                # 429 错误后等待 5-8 秒
                wait_time = 5 + random.uniform(1, 3)
                time.sleep(wait_time)
                continue # 立即进入下一次重试循环
            elif response.status_code >= 500:
                logger.warning(f"收到服务器错误 {response.status_code}，为 {region['name']} 等待后重试...")
                # 5xx 错误后等待 2-4 秒
                wait_time = 2 + random.uniform(0, 2)
                time.sleep(wait_time)
            else:
                logger.warning(f"拉取 {region['name']} 数据失败，状态码: {response.status_code}")
                # 非 429/5xx 错误，也等待一下再重试
                time.sleep(1 + random.uniform(0, 1))
        except requests.exceptions.Timeout:
            logger.warning(f"拉取 {region['name']} 数据超时 (尝试 {attempt + 1}/{max_retries})")
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"拉取 {region['name']} 数据连接错误: {e} (尝试 {attempt + 1}/{max_retries})")
        except Exception as e:
            logger.error(f"拉取 {region['name']} 数据时发生未知错误: {e} (尝试 {attempt + 1}/{max_retries})")

        if attempt < max_retries - 1:
            # 指数退避，但最大不超过 10 秒
            sleep_time = min(10, 1 * (2 ** attempt))
            logger.info(f"等待 {sleep_time:.2f} 秒后重试...")
            time.sleep(sleep_time)

    logger.error(f"拉取 {region['name']} 数据失败 (已重试 {max_retries} 次)")
    return [] # 返回空列表表示失败

def merge_and_deduplicate(new_trends: list, existing_trends: list) -> list:
    """
    将新拉取的数据与现有数据合并并去重。
    如果标题相同，则更新区域列表、热度和时间。
    
    Args:
        new_trends (list): 新拉取的趋势数据列表
        existing_trends (list): 现有的趋势数据列表
        
    Returns:
        list: 合并并去重后的趋势数据列表
    """
    existing_map = {item['title']: item for item in existing_trends}
    updated_titles = set()

    for new_item in new_trends:
        title = new_item['title']
        if title in existing_map:
            existing_item = existing_map[title]
            # 更新区域（合并集合）
            existing_item['regions'] = list(set(existing_item['regions'] + new_item['regions']))
            # 更新国家信息（合并国家集合）
            if existing_item.get('country') and new_item.get('country'):
                # 如果两者都有国家信息，合并为集合
                if isinstance(existing_item['country'], str):
                    existing_item['country'] = {existing_item['country']}
                if isinstance(new_item['country'], str):
                    new_item['country'] = {new_item['country']}
                existing_item['country'] = existing_item['country'].union(new_item['country'])
            elif new_item.get('country'):
                # 如果旧项没有国家信息，使用新项的
                existing_item['country'] = new_item['country']
            # 更新热度（保留较高的）
            if new_item['traffic_num'] > existing_item['traffic_num']:
                existing_item['traffic_str'] = new_item['traffic_str']
                existing_item['traffic_num'] = new_item['traffic_num']
            # 更新时间（保留较新的）
            if new_item['pub_date'] > existing_item['pub_date']:
                existing_item['pub_date_str'] = new_item['pub_date_str']
                existing_item['pub_date'] = new_item['pub_date']
            # 更新图片（如果新项有图片且旧项没有）
            if not existing_item.get('picture') and new_item.get('picture'):
                existing_item['picture'] = new_item['picture']
            # 更新新闻（简单合并，可根据需要调整策略）
            existing_item['news'].extend(new_item['news'])
            # 防止重复添加
            updated_titles.add(title)
        else:
            # 如果是新标题，直接添加
            existing_trends.append(new_item)

    # 去除新闻列表中的重复项（基于标题和来源）
    for item in existing_trends:
        seen_news = set()
        unique_news = []
        for news in item['news']:
            # 创建一个用于判断重复性的键
            news_key = (news.get('title', ''), news.get('source', ''))
            if news_key not in seen_news:
                seen_news.add(news_key)
                unique_news.append(news)
        item['news'] = unique_news

    return existing_trends

def fetch_all_regions(regions_config: dict) -> list:
    """
    拉取所有指定国家和区域的趋势数据
    
    Args:
        regions_config (dict): 包含国家和区域信息的字典结构，格式为：
            {
                "Country1": {
                    "name": "Country1",
                    "regions": [{"code": "REG1", "name": "Region1"}, ...]
                },
                ...
            }
        
    Returns:
        list: 所有国家和区域的趋势数据列表
    """
    # 配置 requests session 以实现重试策略和连接池
    session = requests.Session()
    retry_strategy = Retry(
        total=current_config.REQUEST_MAX_RETRIES,
        backoff_factor=1, # 重试间隔的乘数因子
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    # 设置 User-Agent
    session.headers.update({
        'User-Agent': current_config.REQUEST_USER_AGENT
    })
    
    # 配置代理
    if current_config.USE_PROXY:
        proxy_url = f"http://{current_config.HTTP_PROXY_HOST}:{current_config.HTTP_PROXY_PORT}"
        session.proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
        logger.info(f"已启用代理: {proxy_url}")

    all_new_trends = []
    # 遍历所有国家
    for country_name, country_data in regions_config.items():
        logger.info(f"开始拉取 {country_name} 的数据...")
        country_trends = []
        
        # 遍历该国家的所有区域
        for region in country_data['regions']:
            trends_data = fetch_single_region_with_session(session, region, country_name)
            country_trends.extend(trends_data)
            
            # 每拉取完一个区域后，等待指定时间，避免过于频繁的请求
            delay_min, delay_max = current_config.REQUEST_DELAY_BETWEEN_REGIONS
            time.sleep(delay_min + random.uniform(0, delay_max - delay_min))
        
        # 保存该国家的数据
        save_trends_data(country_trends, get_output_filename(country_name))
        all_new_trends.extend(country_trends)

    # 关闭 session
    session.close()

    logger.info(f"总共拉取到 {len(all_new_trends)} 个新条目")
    return all_new_trends

def save_trends_data(trends_data: list, output_filename: str = None, country_name: str = None) -> bool:
    """
    将趋势数据保存到 JSON 文件
    
    Args:
        trends_data (list): 包含趋势数据的字典列表
        output_filename (str, optional): 输出文件路径，如果为 None 则自动生成
        country_name (str, optional): 国家名称，用于生成文件路径
        
    Returns:
        bool: 保存是否成功
    """
    if output_filename is None:
        output_filename = get_output_filename(country_name)
    
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(trends_data, f, ensure_ascii=False, indent=2)
        logger.info(f"数据已保存到 {output_filename}，共 {len(trends_data)} 个条目")
        return True
    except Exception as e:
        logger.error(f"保存数据到文件 {output_filename} 时出错: {e}")
        return False

def load_existing_data(filename: str = None, country_name: str = None) -> list:
    """
    从文件加载现有的趋势数据
    
    Args:
        filename (str, optional): 输入文件路径，如果为 None 则自动生成
        country_name (str, optional): 国家名称，用于生成文件路径
        
    Returns:
        list: 包含现有趋势数据的字典列表
    """
    if filename is None:
        filename = get_output_filename(country_name)
    
    existing_data = []
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            logger.info(f"已加载现有数据文件: {filename}, 包含 {len(existing_data)} 个条目")
        except json.JSONDecodeError:
            logger.warning(f"现有数据文件 {filename} 格式错误，将从空数据开始。")
            existing_data = []
        except Exception as e:
            logger.error(f"加载现有数据文件 {filename} 时出错: {e}")
            existing_data = []
    
    return existing_data

def remove_unnecessary_fields(trends_data: list) -> list:
    """
    移除趋势数据中不需要的字段
    
    Args:
        trends_data (list): 包含趋势数据的字典列表
        
    Returns:
        list: 移除不需要字段后的趋势数据列表
    """
    for item in trends_data:
        item.pop('traffic_str', None) # 移除 'traffic_str' 字段
        item.pop('pub_date_str', None) # 移除 'pub_date_str' 字段
    return trends_data
