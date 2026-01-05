import json
import os
import sys
from datetime import datetime, timedelta

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入streamlit_AI中的函数
from streamlit_AI import parse_pub_date, load_data_by_date_range

class ComprehensiveTestSuite:
    """全面的测试套件，整合所有必要的测试功能"""
    
    def __init__(self):
        self.json_folder = "JSONs"
        self.passed_tests = 0
        self.failed_tests = 0
    
    def run_test(self, test_name, test_function):
        """运行单个测试并记录结果"""
        print(f"\n=== {test_name} ===")
        try:
            test_function()
            print(f"✅ {test_name} 通过")
            self.passed_tests += 1
            return True
        except Exception as e:
            print(f"❌ {test_name} 失败: {e}")
            import traceback
            traceback.print_exc()
            self.failed_tests += 1
            return False
    
    def test_date_parsing(self):
        """测试日期解析功能"""
        print("测试各种日期格式的解析...")
        
        test_cases = [
            ("2025-12-30", True, 2025, 12, 30),  # 简单日期格式
            ("2025-10-21T17:20:00-07:00", True, 2025, 10, 21),  # 带时区的完整格式
            ("2025-11-15T10:30:00+05:30", True, 2025, 11, 15),  # 不同时区
            ("2025-09-05T08:00:00Z", True, 2025, 9, 5),  # UTC时间格式
            (None, False, None, None, None),  # 空值
            ("invalid_date", False, None, None, None),  # 无效日期
        ]
        
        for date_str, should_succeed, expected_year, expected_month, expected_day in test_cases:
            result = parse_pub_date(date_str)
            print(f"  '{date_str}' -> {result}")
            
            if should_succeed:
                assert result is not None, f"日期 '{date_str}' 解析失败"
                assert result.year == expected_year, f"年份不正确: {result.year} != {expected_year}"
                assert result.month == expected_month, f"月份不正确: {result.month} != {expected_month}"
                assert result.day == expected_day, f"日期不正确: {result.day} != {expected_day}"
            else:
                assert result is None, f"无效日期 '{date_str}' 应该解析失败，但得到了 {result}"
    
    def test_data_loading(self):
        """测试数据加载功能"""
        print("测试数据加载功能...")
        
        # 加载最近2天的数据（考虑到数据可能是昨天的）
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=1)
        
        print(f"  加载日期范围: {start_date} 到 {end_date}")
        data = load_data_by_date_range(start_date, end_date)
        
        print(f"  加载的总记录数: {len(data)}")
        assert len(data) > 0, "没有加载到任何数据"
        
        # 按国家统计记录数
        country_counts = {}
        for item in data:
            country = item.get('Country')
            if country:
                country_counts[country] = country_counts.get(country, 0) + 1
        
        print(f"  按国家统计: {country_counts}")
        assert len(country_counts) > 0, "没有加载到任何国家的数据"
        print(f"  成功加载了来自 {len(country_counts)} 个国家的数据")
    
    def test_json_file_structure(self):
        """测试JSON文件结构"""
        print("测试JSON文件结构...")
        
        # 获取所有国家子文件夹
        countries = [d for d in os.listdir(self.json_folder) if os.path.isdir(os.path.join(self.json_folder, d))]
        print(f"  JSONs文件夹下的国家子文件夹: {countries}")
        
        assert len(countries) > 0, "JSONs文件夹下没有国家子文件夹"
        
        # 检查每个国家文件夹中的JSON文件
        for country in countries:
            country_dir = os.path.join(self.json_folder, country)
            files = os.listdir(country_dir)
            print(f"  {country} 文件夹下的文件: {files}")
            
            # 检查是否有JSON文件
            json_files = [f for f in files if f.endswith('.json')]
            assert len(json_files) > 0, f"{country} 文件夹下没有JSON文件"
            
            # 检查最新的JSON文件
            latest_file = max(json_files, key=lambda x: os.path.getmtime(os.path.join(country_dir, x)))
            file_path = os.path.join(country_dir, latest_file)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"  {latest_file}: {len(data)} 条记录")
            assert len(data) > 0, f"{latest_file} 中的数据为空"
            
            # 检查数据结构
            if data:
                first_item = data[0]
                required_fields = ['title', 'country', 'pub_date', 'regions', 'traffic_num']
                for field in required_fields:
                    assert field in first_item, f"记录缺少必要字段: {field}"
    
    def test_file_search_logic(self):
        """测试文件搜索逻辑"""
        print("测试文件搜索逻辑...")
        
        # 检查JSON文件命名模式
        target_date = datetime.now().date()
        filename_pattern = "trends_{}.json".format(target_date.strftime('%Y-%m-%d'))
        
        print(f"  搜索文件名模式: {filename_pattern}")
        
        # 搜索所有国家子文件夹中的JSON文件
        found_files = []
        
        for country in os.listdir(self.json_folder):
            country_path = os.path.join(self.json_folder, country)
            if os.path.isdir(country_path):
                # 查找匹配的JSON文件
                for file in os.listdir(country_path):
                    if file.startswith("trends_") and file.endswith(".json"):
                        found_files.append(os.path.join(country_path, file))
        
        print(f"  找到的JSON文件: {found_files}")
        assert len(found_files) > 0, "没有找到任何JSON文件"
    
    def extract_country_from_path(self, search_path):
        """从文件夹路径提取国家信息的函数"""
        folder_country = None
        # 检查search_path是否是self.json_folder的子目录
        if search_path != self.json_folder:
            # 获取search_path相对于self.json_folder的路径
            relative_path = os.path.relpath(search_path, self.json_folder)
            # 获取相对路径的第一部分，即国家名称
            folder_country = relative_path.split(os.sep)[0]
            # 验证这个国家名称是否真的存在
            if not os.path.isdir(os.path.join(self.json_folder, folder_country)):
                folder_country = None
        return folder_country
    
    def test_country_extraction(self):
        """测试从文件夹路径提取国家信息的功能"""
        print("测试国家信息提取功能...")
        
        # 测试不同的路径
        test_paths = [
            os.path.join(self.json_folder, 'India'),
            os.path.join(self.json_folder, 'United Kingdom'),
            self.json_folder,
            os.path.join(self.json_folder, 'USA', 'trends_2025-12-30.json')
        ]
        
        for path in test_paths:
            country = self.extract_country_from_path(path)
            print(f"  路径: {path} -> 国家: {country}")
        
        # 验证已知的国家文件夹
        known_countries = ['India', 'United Kingdom', 'Australia', 'United States', 'France', 'Malaysia', 'Thailand', 'Vietnam']
        
        for country in known_countries:
            country_path = os.path.join(self.json_folder, country)
            if os.path.exists(country_path):
                extracted_country = self.extract_country_from_path(country_path)
                assert extracted_country == country, f"国家提取失败: {country_path} -> {extracted_country}"
                print(f"  ✅ 国家 {country} 提取成功")
            else:
                print(f"  ⚠️  国家 {country} 文件夹不存在")
    
    def test_data_processing(self):
        """测试数据处理功能"""
        print("测试数据处理功能...")
        
        # 测试最近2天的数据处理
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=1)
        
        print(f"  测试日期范围: {start_date} 到 {end_date}")
        
        # 模拟数据处理流程
        processed_items = []
        
        # 遍历所有国家文件夹
        for country in os.listdir(self.json_folder):
            country_path = os.path.join(self.json_folder, country)
            if os.path.isdir(country_path):
                # 查找匹配的JSON文件
                for file in os.listdir(country_path):
                    if file.startswith("trends_") and file.endswith(".json"):
                        # 解析文件名中的日期
                        try:
                            file_date_str = file.split('_')[1].split('.')[0]
                            file_date = datetime.strptime(file_date_str, '%Y-%m-%d').date()
                            
                            # 只处理指定日期范围内的文件
                            if start_date <= file_date <= end_date:
                                file_path = os.path.join(country_path, file)
                                print(f"  处理文件: {file_path}")
                                
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                
                                # 验证数据结构和流量筛选
                                for item in data:
                                    # 应用流量筛选条件
                                    if item.get('traffic_num', 0) < 0:
                                        continue
                                    
                                    # 验证pub_date格式
                                    pub_date_str = item.get('pub_date')
                                    if pub_date_str:
                                        item_date = parse_pub_date(pub_date_str)
                                        if item_date and start_date <= item_date <= end_date:
                                            # 验证新闻列表
                                            news_list = item.get('news', [])
                                            if news_list:
                                                processed_items.append(item)
                                                
                                                # 只处理前几个条目进行测试
                                                if len(processed_items) >= 5:
                                                    break
                                
                                if len(processed_items) >= 5:
                                    break
                        except Exception as e:
                            print(f"  处理文件 {file} 时出错: {e}")
                            continue
                
                if len(processed_items) >= 5:
                    break
        
        print(f"  成功处理了 {len(processed_items)} 个条目")
        assert len(processed_items) > 0, "没有处理到任何有效数据"
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 50)
        print("开始综合测试套件")
        print(f"测试运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # 运行所有测试
        self.run_test("日期解析功能", self.test_date_parsing)
        self.run_test("数据加载功能", self.test_data_loading)
        self.run_test("JSON文件结构", self.test_json_file_structure)
        self.run_test("文件搜索逻辑", self.test_file_search_logic)
        self.run_test("国家信息提取功能", self.test_country_extraction)
        self.run_test("数据处理功能", self.test_data_processing)
        
        # 打印测试总结
        print("\n" + "=" * 50)
        print("测试总结")
        print("=" * 50)
        print(f"总测试数: {self.passed_tests + self.failed_tests}")
        print(f"通过测试: {self.passed_tests}")
        print(f"失败测试: {self.failed_tests}")
        
        if self.failed_tests == 0:
            print("🎉 所有测试通过！")
            return True
        else:
            print("❌ 部分测试失败！")
            return False

# 主函数
if __name__ == "__main__":
    test_suite = ComprehensiveTestSuite()
    test_suite.run_all_tests()
