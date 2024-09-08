import numpy as np
import itertools

def calculate_cost(params, decisions):
    total_cost = 0
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
            total_cost += defect_rate * price
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
            total_cost += defect_rate * (assembly_cost + sum(params['component_prices']))
    if not decisions['product_inspections'][-1]:
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

if __name__ == "__main__":
    best_decisions, best_cost = optimize_decisions(params)
    print("最优决策:")
    print("零配件检测:", best_decisions['component_inspections'])
    print("半成品/成品检测:", best_decisions['product_inspections'])
    print("半成品/成品拆解:", best_decisions['product_disassembles'])
    print("最低成本:", best_cost)