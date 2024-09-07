import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import os
import itertools

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 或者使用 'Heiti TC'
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

def calculate_cost(params, decisions):
    total_cost = 0
    
    # 零配件成本
    for i, (defect_rate, price, inspect_cost, inspect) in enumerate(zip(
        params['component_defect_rates'], 
        params['component_prices'], 
        params['component_inspect_costs'],
        decisions['component_inspections']
    )):
        total_cost += price
        if inspect:
            total_cost += inspect_cost
        else:
            total_cost += defect_rate * price  # 不检测的话，需要多买一些来补充次品

    # 半成品和成品成本
    for i, (defect_rate, assembly_cost, inspect_cost, disassemble_cost, inspect, disassemble) in enumerate(zip(
        params['product_defect_rates'],
        params['assembly_costs'],
        params['product_inspect_costs'],
        params['disassemble_costs'],
        decisions['product_inspections'],
        decisions['product_disassembles']
    )):
        total_cost += assembly_cost
        if inspect:
            total_cost += inspect_cost
        if disassemble:
            total_cost += defect_rate * disassemble_cost
        else:
            # 如果不拆解，损失所有投入的成本
            total_cost += defect_rate * (assembly_cost + sum(params['component_prices']))

    # 成品市场损失
    if not decisions['product_inspections'][-1]:  # 如果最后一道工序不检测
        total_cost += params['product_defect_rates'][-1] * params['market_price']

    return total_cost

def optimize_decisions(params):
    best_cost = float('inf')
    best_decisions = None
    
    for decisions in itertools.product(
        itertools.product([True, False], repeat=len(params['component_defect_rates'])),
        itertools.product([True, False], repeat=len(params['product_defect_rates'])),
        itertools.product([True, False], repeat=len(params['product_defect_rates']))
    ):
        current_decisions = {
            'component_inspections': decisions[0],
            'product_inspections': decisions[1],
            'product_disassembles': decisions[2]
        }
        cost = calculate_cost(params, current_decisions)
        if cost < best_cost:
            best_cost = cost
            best_decisions = current_decisions
    
    return best_decisions, best_cost

# 参数设置
params = {
    'component_defect_rates': [0.1] * 8,
    'component_prices': [2, 8, 12, 2, 8, 12, 8, 12],
    'component_inspect_costs': [1, 1, 2, 1, 1, 2, 1, 2],
    'product_defect_rates': [0.1, 0.1, 0.1],
    'assembly_costs': [8, 8, 8],
    'product_inspect_costs': [4, 4, 6],
    'disassemble_costs': [6, 6, 10],
    'market_price': 200
}

best_decisions, best_cost = optimize_decisions(params)

print("最优决策:")
print("零配件检测:", best_decisions['component_inspections'])
print("半成品/成品检测:", best_decisions['product_inspections'])
print("半成品/成品拆解:", best_decisions['product_disassembles'])
print("最低成本:", best_cost)


def plot_component_decisions(best_decisions):
    """绘制零配件检测决策图"""
    decisions = best_decisions['component_inspections']
    component_names = [f'零件{i+1}' for i in range(len(decisions))]
    
    plt.figure(figsize=(12, 6))
    plt.bar(component_names, decisions)
    plt.title('零配件检测决策')
    plt.xlabel('零配件')
    plt.ylabel('是否检测')
    plt.yticks([0, 1], ['否', '是'])
    plt.savefig('./3/component_decisions.png', dpi=300)
    plt.close()

def plot_product_decisions(best_decisions):
    """绘制半成品/成品检测和拆解决策图"""
    inspections = best_decisions['product_inspections']
    disassembles = best_decisions['product_disassembles']
    stages = ['半成品1', '半成品2', '成品']
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    ax1.bar(stages, inspections)
    ax1.set_title('半成品/成品检测决策')
    ax1.set_ylabel('是否检测')
    ax1.set_yticks([0, 1])
    ax1.set_yticklabels(['否', '是'])
    
    ax2.bar(stages, disassembles)
    ax2.set_title('半成品/成品拆解决策')
    ax2.set_ylabel('是否拆解')
    ax2.set_yticks([0, 1])
    ax2.set_yticklabels(['否', '是'])
    
    plt.tight_layout()
    plt.savefig('./3/product_decisions.png', dpi=300)
    plt.close()
import matplotlib.pyplot as plt

def plot_cost_breakdown(params, best_decisions):
    """绘制成本构成图"""
    costs = {
        '零配件成本': 0,
        '检测成本': 0,
        '装配成本': sum(params['assembly_costs']),
        '拆解成本': 0,
        '市场损失': 0
    }

    # 计算各项成本
    for i, (price, inspect, inspect_cost) in enumerate(zip(
            params['component_prices'],
            best_decisions['component_inspections'],
            params['component_inspect_costs']
    )):
        costs['零配件成本'] += price
        if inspect:
            costs['检测成本'] += inspect_cost

    for i, (inspect, disassemble, inspect_cost, disassemble_cost, defect_rate) in enumerate(zip(
            best_decisions['product_inspections'],
            best_decisions['product_disassembles'],
            params['product_inspect_costs'],
            params['disassemble_costs'],
            params['product_defect_rates']
    )):
        if inspect:
            costs['检测成本'] += inspect_cost
        if disassemble:
            costs['拆解成本'] += defect_rate * disassemble_cost

    if not best_decisions['product_inspections'][-1]:
        costs['市场损失'] = params['product_defect_rates'][-1] * params['market_price']

    plt.figure(figsize=(10, 6))
    # 增大字体大小
    plt.pie(costs.values(), labels=costs.keys(), autopct='%1.1f%%', textprops={'fontsize': 18})
    plt.title('成本构成', fontsize=18)
    plt.savefig('./3/cost_breakdown.png', dpi=300)
    plt.close()

# 主程序
if __name__ == "__main__":
    # 创建保存图片的文件夹
    os.makedirs('./3', exist_ok=True)
    
    best_decisions, best_cost = optimize_decisions(params)

    print("最优决策:")
    print("零配件检测:", best_decisions['component_inspections'])
    print("半成品/成品检测:", best_decisions['product_inspections'])
    print("半成品/成品拆解:", best_decisions['product_disassembles'])
    print("最低成本:", best_cost)

    # 生成可视化图表
    plot_component_decisions(best_decisions)
    plot_product_decisions(best_decisions)
    plot_cost_breakdown(params, best_decisions)