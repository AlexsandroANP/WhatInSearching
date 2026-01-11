import pandas as pd

# 测试数据
TEST_DATA = [
    {
        "搜索词": "Python",
        "标题": "Python 3.12 发布",
        "信源": "Python.org",
        "流量": 10000,
        "发布日期": "2024-01-01",
        "地区": "全球",
        "国家": "美国"
    },
    {
        "搜索词": "JavaScript",
        "标题": "JavaScript 新特性",
        "信源": "MDN",
        "流量": 8000,
        "发布日期": "2024-01-02",
        "地区": "全球",
        "国家": "美国"
    }
]

# 创建 DataFrame
df = pd.DataFrame(TEST_DATA)

# 生成 ISON 格式的函数
def generate_ison_content(df_filtered, max_rows=100000):
    """
    生成 ISON 格式的内容
    """
    if df_filtered.empty:
        return "table.empty"

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

    # 生成 ISON 格式
    ison_lines = []
    ison_lines.append("table.trends")
    ison_lines.append("news_title source title traffic_num:int pub_date regions country")

    for _, row in df_simple.iterrows():
        # 处理可能包含空格的字段，使用引号包围
        news_title = f'"{row["news_title"]}"' if ' ' in str(row["news_title"]) else str(row["news_title"])
        source = f'"{row["source"]}"' if ' ' in str(row["source"]) else str(row["source"])
        title = f'"{row["title"]}"' if ' ' in str(row["title"]) else str(row["title"])
        traffic_num = int(row["traffic_num"])
        pub_date = str(row["pub_date"])
        regions = f'"{row["regions"]}"' if ' ' in str(row["regions"]) else str(row["regions"])
        country = f'"{row["country"]}"' if ' ' in str(row["country"]) else str(row["country"])
        
        line = f"{news_title} {source} {title} {traffic_num} {pub_date} {regions} {country}"
        ison_lines.append(line)

    return "\n".join(ison_lines)

# 生成 Markdown 格式的函数
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

# 测试 ISON 格式
print("测试 ISON 格式:")
print("=" * 50)
ison_content = generate_ison_content(df)
print(ison_content)
print("\n" + "=" * 50)

# 测试 Markdown 格式
print("\n测试 Markdown 格式:")
print("=" * 50)
markdown_content = generate_simple_markdown_table(df)
print(markdown_content)
print("\n" + "=" * 50)

print("\n测试完成！")
