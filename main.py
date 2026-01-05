"""
Google Trends 数据收集应用程序

此应用程序用于定期从 Google Trends RSS 源收集印度各地区的趋势数据，并将其保存到 JSON 文件中。
"""

import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

# 导入自定义模块
from config import Config, get_config
from data_fetcher import (
    fetch_all_regions,
    merge_and_deduplicate,
    load_existing_data,
    save_trends_data,
    remove_unnecessary_fields
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('google_trends_fetcher.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 获取当前配置
config = get_config()

def fetch_country_regions_and_save(country_name):
    """
    按国家拉取所有区域数据，合并去重，保存到 JSON 文件。
    
    Args:
        country_name (str): 要抓取数据的国家名称
    """
    try:
        logger.info(f"开始抓取国家: {country_name} 的数据")
        
        # 获取该国家的配置
        country_config = config.REGIONS.get(country_name)
        if not country_config:
            logger.error(f"未找到国家 {country_name} 的配置")
            return
        
        # 创建仅包含当前国家的配置
        country_regions = {country_name: country_config}
        
        # 加载该国家的现有数据
        existing_data = load_existing_data(country_name)

        # 拉取该国家所有区域的数据
        country_new_trends = fetch_all_regions(country_regions)

        # 合并和去重
        final_data = merge_and_deduplicate(country_new_trends, existing_data)

        # 移除不需要的字段
        final_data = remove_unnecessary_fields(final_data)

        # 保存到文件
        save_trends_data(final_data, country_name=country_name)
        
        logger.info(f"国家 {country_name} 的数据抓取和保存完成")
    except Exception as e:
        logger.error(f"抓取国家 {country_name} 的数据时发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())

def fetch_all_regions_and_save():
    """
    主函数：拉取所有国家所有区域数据，合并去重，保存到 JSON 文件。
    """
    logger.info("开始抓取所有国家的数据")
    
    for country_name in config.REGIONS.keys():
        fetch_country_regions_and_save(country_name)
    
    logger.info("所有国家的数据抓取完成")

# --- APScheduler 配置和主执行块 ---
if __name__ == "__main__":
    # 立即执行一次所有国家的数据收集
    fetch_all_regions_and_save()

    # 配置调度器
    scheduler = BlockingScheduler()

    # 为每个国家创建独立的调度任务
    logger.info(f"开始为 {len(config.REGIONS)} 个国家创建调度任务...")
    
    for country_name, country_config in config.REGIONS.items():
        try:
            # 获取国家的时区
            country_timezone = country_config.get('timezone', 'UTC')
            
            # 为该国家创建时区感知的Cron触发器
            trigger = CronTrigger.from_crontab(
                config.SCHEDULER_CRON_EXPRESSION,
                timezone=country_timezone
            )
            
            # 生成唯一的任务ID
            job_id = f'fetch_trends_{country_name.lower().replace(" ", "_")}_job'
            
            # 添加调度任务
            scheduler.add_job(
                func=fetch_country_regions_and_save,
                trigger=trigger,
                args=[country_name],
                id=job_id,
                name=f'Fetch Google Trends Data - {country_name}',
                replace_existing=True
            )
            
            logger.info(f"为国家 {country_name} 创建了调度任务，时区: {country_timezone}")
        except Exception as e:
            logger.error(f"为国家 {country_name} 创建调度任务时发生错误: {e}")
    
    logger.info("所有国家的调度任务已安排完成。")
    logger.info("按 Ctrl+C 停止调度器...")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("接收到中断信号，正在关闭 APScheduler...")
        scheduler.shutdown()
        print("调度器已关闭。")