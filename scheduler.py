import time
import logging
import pytz
from datetime import datetime
import schedule

# 导入配置和数据获取模块
from config import current_config
from data_fetcher import fetch_all_regions

# 配置日志
logging.basicConfig(
    level=current_config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 目标抓取时间点（基于目标国家的本地时间）
TARGET_FETCH_TIMES = [
    "11:00",  # 上午 11 点
    "11:30",  # 上午 11 点 30 分
    "17:00",  # 下午 5 点
    "17:30",  # 下午 5 点 30 分
    "23:00",  # 晚上 11 点
    "23:30"   # 晚上 11 点 30 分
]

def fetch_data_for_country(country_name, country_config):
    """
    为指定国家抓取数据
    
    Args:
        country_name (str): 国家名称
        country_config (dict): 国家配置信息
    """
    try:
        logger.info(f"开始为 {country_name} 抓取数据...")
        
        # 构建该国家的配置
        country_regions_config = {
            country_name: country_config
        }
        
        # 调用数据获取函数
        trends_data = fetch_all_regions(country_regions_config)
        
        logger.info(f"为 {country_name} 抓取数据完成，共获取 {len(trends_data)} 条记录")
        return True
    except Exception as e:
        logger.error(f"为 {country_name} 抓取数据时出错: {e}")
        return False

def check_and_fetch():
    """
    检查所有国家的时区时间，在指定时间点执行抓取
    """
    logger.debug("执行定时检查...")
    
    # 遍历所有国家
    for country_name, country_config in current_config.REGIONS.items():
        try:
            # 获取国家时区
            timezone_str = country_config.get('timezone')
            if not timezone_str:
                logger.warning(f"国家 {country_name} 未配置时区信息，跳过")
                continue
            
            # 创建时区对象
            tz = pytz.timezone(timezone_str)
            
            # 获取该时区的当前时间
            now = datetime.now(tz)
            current_time_str = now.strftime("%H:%M")
            
            # 检查是否到达目标抓取时间
            if current_time_str in TARGET_FETCH_TIMES:
                logger.info(f"[{country_name}] 到达抓取时间 {current_time_str}，开始执行数据抓取")
                fetch_data_for_country(country_name, country_config)
        except Exception as e:
            logger.error(f"处理国家 {country_name} 时出错: {e}")

def main():
    """
    主函数，启动调度器
    """
    logger.info("启动基于时区的定时任务调度器")
    logger.info(f"目标抓取时间点: {TARGET_FETCH_TIMES}")
    
    # 每分钟检查一次
    schedule.every(1).minutes.do(check_and_fetch)
    
    # 立即执行一次检查
    check_and_fetch()
    
    # 主循环
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            logger.info("接收到中断信号，正在退出...")
            break
        except Exception as e:
            logger.error(f"调度器运行时出错: {e}")
            time.sleep(60)  # 出错后暂停 60 秒再继续

if __name__ == "__main__":
    main()
