#!/usr/bin/env python3
"""
脚本用于执行数据抓取操作，支持按指定国家抓取数据
"""

import logging
import sys
import argparse

# 设置日志级别
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')
logger = logging.getLogger(__name__)

def parse_arguments():
    """
    解析命令行参数
    
    Returns:
        argparse.Namespace: 包含解析后的参数的命名空间
    """
    parser = argparse.ArgumentParser(description='Google Trends 数据抓取脚本')
    parser.add_argument(
        '--countries', '-c', 
        nargs='+', 
        help='要抓取数据的国家名称列表，如：--countries India "United Kingdom"',
        default=None
    )
    parser.add_argument(
        '--all', '-a', 
        action='store_true', 
        help='抓取所有国家的数据（默认）',
        default=True
    )
    return parser.parse_args()

try:
    # 导入数据抓取模块
    from data_fetcher import fetch_all_regions, load_existing_data, merge_and_deduplicate, remove_unnecessary_fields, save_trends_data
    from config import REGIONS, current_config
    
    # 解析命令行参数
    args = parse_arguments()
    
    # 确定要抓取的国家列表
    if args.countries:
        countries_to_fetch = args.countries
        args.all = False
    else:
        countries_to_fetch = list(REGIONS.keys())
    
    logger.info("开始执行数据抓取操作...")
    logger.info(f"将抓取以下国家的数据: {', '.join(countries_to_fetch)}")
    
    # 创建要抓取的国家配置
    regions_config = {}
    for country_name in countries_to_fetch:
        if country_name in REGIONS:
            regions_config[country_name] = REGIONS[country_name]
        else:
            logger.warning(f"国家 {country_name} 不在配置中，将跳过")
    
    if not regions_config:
        logger.error("没有有效的国家配置可抓取")
        sys.exit(1)
    
    # 执行数据抓取
    results = fetch_all_regions(regions_config)
    
    logger.info(f"数据抓取完成! 总共获取了 {len(results)} 条新数据")
    
    # 检查JSON文件是否被正确创建
    logger.info("检查生成的JSON文件:")
    for country_name in regions_config.keys():
        country_dir = os.path.join(current_config.OUTPUT_DIR, country_name)
        if os.path.exists(country_dir):
            files = os.listdir(country_dir)
            logger.info(f"  {country_name}: {len(files)} 个文件")
            for file in files:
                logger.info(f"    - {file}")
        else:
            logger.warning(f"  {country_name}: 目录不存在")
    
    sys.exit(0)
    
except ImportError as e:
    logger.error(f"导入错误: {e}")
    sys.exit(1)
except Exception as e:
    logger.error(f"数据抓取过程中发生错误: {e}")
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1)
