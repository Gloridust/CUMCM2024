import itertools
import numpy as np

def calculate_cost(params, decisions):
    """计算给定决策下的总成本"""
    total_cost = 0
    
    # 零配件成本
    for i, (defect_rate, price, inspect_cost, inspect) in enumerate(zip(
        params['component_defect_rates'], 
        params['component_prices'], 
        params['component_inspect_costs'],
        decisions['component_inspections']
    )):
        if inspect:
            total_cost += price + inspect_cost
        else:
            total_cost += price * (1 + defect_rate)
    
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
        total_cost += params['product_defect_rates'][-1] * params['replacement_cost']
    
    return total_cost

def optimize_decisions(params):
    """找出最优决策"""
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

# 问题3的参数
params = {
    'component_defect_rates': [0.10] * 8,
    'component_prices': [2, 8, 12, 2, 8, 12, 8, 12],
    'component_inspect_costs': [1, 1, 2, 1, 1, 2, 1, 2],
    'product_defect_rates': [0.10, 0.10, 0.10],
    'assembly_costs': [8, 8, 8],
    'product_inspect_costs': [4, 4, 6],
    'disassemble_costs': [6, 6, 10],
    'replacement_cost': 40,
    'market_price': 200
}

# 运行优化
optimal_decisions, optimal_cost = optimize_decisions(params)

print("脚本找到的最优决策:")
print(f"零配件检测: {optimal_decisions['component_inspections']}")
print(f"半成品/成品检测: {optimal_decisions['product_inspections']}")
print(f"半成品/成品拆解: {optimal_decisions['product_disassembles']}")
print(f"最低成本: {optimal_cost:.2f}")

# 验证给定的决策
given_decisions = {
    'component_inspections': (False, False, False, False, False, False, False, False),
    'product_inspections': (False, False, True),
    'product_disassembles': (True, True, True)
}
given_cost = calculate_cost(params, given_decisions)

print("\n给定决策的成本:")
print(f"成本: {given_cost:.2f}")

# 比较结果
print("\n验证结果:")
if abs(given_cost - optimal_cost) < 0.01:  # 允许小的浮点数误差
    print("验证通过：给定的决策是最优的")
elif given_cost < optimal_cost:
    print("验证失败：给定的决策比脚本找到的决策更优")
    print(f"给定决策比脚本找到的决策节省: {optimal_cost - given_cost:.2f}")
else:
    print("验证失败：脚本找到了更优的决策")
    print(f"脚本找到的决策比给定决策节省: {given_cost - optimal_cost:.2f}")

# 敏感性分析
print("\n敏感性分析:")
for param in ['component_defect_rates', 'component_prices', 'product_defect_rates', 'assembly_costs', 'replacement_cost']:
    if isinstance(params[param], list):
        for i in range(len(params[param])):
            original_value = params[param][i]
            params[param][i] *= 1.1  # 增加10%
            new_decisions, new_cost = optimize_decisions(params)
            print(f"{param}[{i}] 增加10%后的最优成本: {new_cost:.2f}")
            params[param][i] = original_value  # 恢复原值
    else:
        original_value = params[param]
        params[param] *= 1.1  # 增加10%
        new_decisions, new_cost = optimize_decisions(params)
        print(f"{param} 增加10%后的最优成本: {new_cost:.2f}")
        params[param] = original_value  # 恢复原值