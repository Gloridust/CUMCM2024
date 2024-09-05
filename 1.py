import pandas as pd
import numpy as np
from pyomo.environ import *
from pyomo.opt import SolverFactory

# 读取数据
crops_data = pd.read_csv('./attachment/附件2.csv')
land_data = pd.read_csv('./attachment/附件1.csv')

# 预处理数据
crops_data['平均亩产量'] = crops_data['亩产量/斤']
crops_data['平均销售单价'] = (crops_data['销售单价/(元/斤)'].str.split('-').apply(lambda x: (float(x[0]) + float(x[1])) / 2))
crops_data['平均利润'] = crops_data['平均亩产量'] * crops_data['平均销售单价'] - crops_data['种植成本/(元/亩)']

# 创建作物字典
crops = {}
for _, row in crops_data.iterrows():
    key = (row['作物编号'], row['作物名称'], row['地块类型'], row['种植季次'])
    crops[key] = {
        'yield': row['平均亩产量'],
        'price': row['平均销售单价'],
        'cost': row['种植成本/(元/亩)'],
        'profit': row['平均利润']
    }

# 创建地块字典
land_types = {
    '平旱地': 1201 * 0.3,
    '梯田': 1201 * 0.3,
    '山坡地': 1201 * 0.3,
    '水浇地': 1201 * 0.1,
    '普通大棚': 16 * 0.6,
    '智慧大棚': 4 * 0.6
}

# 定义模型
model = ConcreteModel()

# 定义集合
model.YEARS = RangeSet(2024, 2030)
model.LANDS = Set(initialize=land_types.keys())
model.CROPS = RangeSet(1, 41)
model.SEASONS = Set(initialize=['单季', '第一季', '第二季'])

# 定义决策变量
model.x = Var(model.LANDS, model.CROPS, model.SEASONS, model.YEARS, domain=NonNegativeReals)
model.y = Var(model.CROPS, model.YEARS, domain=NonNegativeReals)  # 实际销售量

# 非线性收益函数
def revenue_rule(model, c, t):
    expected_sales = 0.8 * max(crops.get((c, crops_data.loc[crops_data['作物编号'] == c, '作物名称'].values[0], l, s), {}).get('yield', 0) 
                               for l in model.LANDS for s in model.SEASONS)
    price = crops.get((c, crops_data.loc[crops_data['作物编号'] == c, '作物名称'].values[0], list(model.LANDS)[0], list(model.SEASONS)[0]), {}).get('price', 0)
    
    if model.y[c, t] <= expected_sales:
        return price * model.y[c, t]
    else:
        return price * expected_sales + 0.5 * price * (model.y[c, t] - expected_sales)

model.revenue = Expression(model.CROPS, model.YEARS, rule=revenue_rule)

# 目标函数
def obj_rule(model):
    return sum(model.revenue[c, t] for c in model.CROPS for t in model.YEARS) - \
           sum(crops.get((c, crops_data.loc[crops_data['作物编号'] == c, '作物名称'].values[0], l, s), {}).get('cost', 0) * model.x[l, c, s, t]
               for l in model.LANDS for c in model.CROPS for s in model.SEASONS for t in model.YEARS)

model.obj = Objective(rule=obj_rule, sense=maximize)

# 约束条件
# 1. 土地面积约束
def land_constraint(model, l, t):
    if l in ['平旱地', '梯田', '山坡地', '水浇地']:
        return sum(model.x[l, c, '单季', t] for c in model.CROPS) <= land_types[l]
    elif l == '普通大棚':
        return (sum(model.x[l, c, '第一季', t] for c in model.CROPS) <= land_types[l]) and \
               (sum(model.x[l, c, '第二季', t] for c in model.CROPS) <= land_types[l])
    elif l == '智慧大棚':
        return (sum(model.x[l, c, '第一季', t] for c in model.CROPS) <= land_types[l]) and \
               (sum(model.x[l, c, '第二季', t] for c in model.CROPS) <= land_types[l])

model.land_constraint = Constraint(model.LANDS, model.YEARS, rule=land_constraint)

# 2. 作物轮作约束
def crop_rotation(model, l, t):
    return sum(model.x[l, c, s, t] for c in [1,2,3,4,5,17,18,19] for s in model.SEASONS) >= 0.1 * land_types[l]

model.crop_rotation = Constraint(model.LANDS, model.YEARS, rule=crop_rotation)

# 3. 产量平衡约束
def yield_balance(model, c, t):
    return model.y[c, t] == sum(crops.get((c, crops_data.loc[crops_data['作物编号'] == c, '作物名称'].values[0], l, s), {}).get('yield', 0) * model.x[l, c, s, t]
                                for l in model.LANDS for s in model.SEASONS)

model.yield_balance = Constraint(model.CROPS, model.YEARS, rule=yield_balance)

# 4. 连续种植限制
def continuous_planting(model, l, c, t):
    if t > 2024:
        return model.x[l, c, '单季', t] + sum(model.x[l, c, s, t] for s in ['第一季', '第二季']) <= \
               land_types[l] - (model.x[l, c, '单季', t-1] + sum(model.x[l, c, s, t-1] for s in ['第一季', '第二季']))
    else:
        return Constraint.Skip

model.continuous_planting = Constraint(model.LANDS, model.CROPS, model.YEARS, rule=continuous_planting)

# 5. 种植季节限制
def season_constraint(model, l, c, s, t):
    if (l in ['平旱地', '梯田', '山坡地'] and s != '单季') or \
       (l == '水浇地' and s == '单季' and c != 16) or \
       (l == '普通大棚' and s == '单季') or \
       (l == '智慧大棚' and s == '单季') or \
       (l == '普通大棚' and s == '第二季' and c not in [38, 39, 40, 41]) or \
       (c in [35, 36, 37] and (l != '水浇地' or s != '第二季')):
        return model.x[l, c, s, t] == 0
    else:
        return Constraint.Skip

model.season_constraint = Constraint(model.LANDS, model.CROPS, model.SEASONS, model.YEARS, rule=season_constraint)

# 求解模型
solver = SolverFactory('ipopt')
results = solver.solve(model, tee=True)

# 检查求解状态
if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
    print("Optimal solution found.")
else:
    print("Solver did not find an optimal solution.")

# 输出结果
print("Optimal Profit:", value(model.obj))

# 将结果保存到Excel文件
results = []
for l in model.LANDS:
    for c in model.CROPS:
        for s in model.SEASONS:
            for t in model.YEARS:
                if value(model.x[l, c, s, t]) > 0.01:  # 只保存大于0.01的结果，避免舍入误差
                    results.append({
                        '年份': t,
                        '地块类型': l,
                        '作物编号': c,
                        '作物名称': crops_data.loc[crops_data['作物编号'] == c, '作物名称'].values[0],
                        '种植季次': s,
                        '种植面积': value(model.x[l, c, s, t])
                    })

results_df = pd.DataFrame(results)
results_df.to_excel('result1_2.xlsx', index=False)