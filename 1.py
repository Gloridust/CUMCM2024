import pandas as pd
import numpy as np

# 读取附件数据
df1_1 = pd.read_csv('./attachment/附件1-1.csv')
df1_2 = pd.read_csv('./attachment/附件1-2.csv')
df2_1 = pd.read_csv('./attachment/附件2-1.csv')
df2_2 = pd.read_csv('./attachment/附件2-2.csv')

# 检查 df2_1 是否有 '地块类型' 列
if '地块类型' not in df2_1.columns:
    # 根据种植地块关联 df1_1 获取地块类型
    df2_1 = df2_1.merge(df1_1[['地块名称', '地块类型']], on='种植地块')

# 合并相关数据
df = pd.merge(df2_1, df2_2, on=['作物编号', '作物名称', '种植季次'])

# 定义函数计算收益
def calculate_profit(row, case):
    if case == 1:  # 情况 1：超过部分滞销，造成浪费
        if row['总产量'] <= row['预期销售量']:
            profit = (row['销售单价'] - row['种植成本']) * row['种植面积']
        else:
            profit = (row['销售单价'] - row['种植成本']) * row['预期销售量'] - row['种植成本'] * (row['总产量'] - row['预期销售量'])
    elif case == 2:  # 情况 2：超过部分按 2023 年销售价格的 50%降价出售
        profit = (row['销售单价'] - row['种植成本']) * row['种植面积']
        if row['总产量'] > row['预期销售量']:
            profit += 0.5 * row['销售单价'] * (row['总产量'] - row['预期销售量']) - row['种植成本'] * (row['总产量'] - row['预期销售量'])
    return profit

# 情况 1
result1_1 = []
for year in range(2024, 2031):
    for plot in df1_1['地块名称'].unique():
        for crop in df1_2['作物编号'].unique():
            # 筛选出符合条件的种植记录
            sub_df = df[(df['种植地块'] == plot) & (df['作物编号'] == crop)]
            if not sub_df.empty:
                # 计算总产量
                total_yield = sub_df['亩产量'] * sub_df['种植面积'].sum()
                # 计算预期销售量
                expected_sales = sub_df['预期销售量'].sum()
                # 计算收益
                profit = calculate_profit(sub_df.iloc[0], 1)
                result1_1.append([year, plot, crop, sub_df['作物名称'].iloc[0], sub_df['作物类型'].iloc[0], sub_df['种植面积'].sum(), sub_df['种植季次'].iloc[0], total_yield, expected_sales, profit])
result1_1_df = pd.DataFrame(result1_1, columns=['年份', '地块名称', '作物编号', '作物名称', '作物类型', '种植面积', '种植季次', '总产量', '预期销售量', '收益'])

# 情况 2
result1_2 = []
for year in range(2024, 2031):
    for plot in df1_1['地块名称'].unique():
        for crop in df1_2['作物编号'].unique():
            # 筛选出符合条件的种植记录
            sub_df = df[(df['种植地块'] == plot) & (df['作物编号'] == crop)]
            if not sub_df.empty:
                # 计算总产量
                total_yield = sub_df['亩产量'] * sub_df['种植面积'].sum()
                # 计算预期销售量
                expected_sales = sub_df['预期销售量'].sum()
                # 计算收益
                profit = calculate_profit(sub_df.iloc[0], 2)
                result1_2.append([year, plot, crop, sub_df['作物名称'].iloc[0], sub_df['作物类型'].iloc[0], sub_df['种植面积'].sum(), sub_df['种植季次'].iloc[0], total_yield, expected_sales, profit])
result1_2_df = pd.DataFrame(result1_2, columns=['年份', '地块名称', '作物编号', '作物名称', '作物类型', '种植面积', '种植季次', '总产量', '预期销售量', '收益'])

# 将结果保存到 Excel 文件中
result1_1_df.to_excel('result1_1.xlsx', index=False)
result1_2_df.to_excel('result1_2.xlsx', index=False)