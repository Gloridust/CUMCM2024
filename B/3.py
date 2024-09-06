import itertools
import numpy as np

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