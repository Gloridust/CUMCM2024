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
    
    # 装配成本
    total_cost += params['assembly_cost']
    
    # 成品检测成本
    if decisions['product_inspection']:
        total_cost += params['product_inspect_cost']
    
    # 不合格品处理成本
    defect_rate = params['product_defect_rate']
    if decisions['product_disassemble']:
        total_cost += defect_rate * params['disassemble_cost']
    else:
        total_cost += defect_rate * (sum(params['component_prices']) + params['assembly_cost'])
    
    # 市场调换损失
    if not decisions['product_inspection']:
        total_cost += defect_rate * params['replacement_cost']
    
    return total_cost

def optimize_decisions(params):
    """找出最优决策"""
    best_cost = float('inf')
    best_decisions = None
    
    for decisions in itertools.product(
        itertools.product([True, False], repeat=len(params['component_defect_rates'])),
        [True, False],  # 产品检测
        [True, False]   # 产品拆解
    ):
        current_decisions = {
            'component_inspections': decisions[0],
            'product_inspection': decisions[1],
            'product_disassemble': decisions[2]
        }
        cost = calculate_cost(params, current_decisions)
        if cost < best_cost:
            best_cost = cost
            best_decisions = current_decisions
    
    return best_decisions, best_cost

# 问题2的参数
params = {
    'component_defect_rates': [0.10, 0.10],
    'component_prices': [4, 18],
    'component_inspect_costs': [2, 3],
    'assembly_cost': 6,
    'product_defect_rate': 0.10,
    'product_inspect_cost': 3,
    'disassemble_cost': 5,
    'replacement_cost': 6,
    'market_price': 56
}

# 运行优化
optimal_decisions, optimal_cost = optimize_decisions(params)

print("最优决策:")
print(f"零配件检测: {optimal_decisions['component_inspections']}")
print(f"产品检测: {optimal_decisions['product_inspection']}")
print(f"产品拆解: {optimal_decisions['product_disassemble']}")
print(f"最低成本: {optimal_cost:.2f}")

# 验证给定的决策
given_decisions = {
    'component_inspections': (False, False),
    'product_inspection': False,
    'product_disassemble': True
}
given_cost = calculate_cost(params, given_decisions)

print("\n给定决策的成本:")
print(f"成本: {given_cost:.2f}")

# 比较结果
print("\n验证结果:")
if abs(given_cost - optimal_cost) < 0.01:  # 允许小的浮点数误差
    print("验证通过：给定的决策是最优的")
else:
    print("验证失败：给定的决策不是最优的")
    print(f"最优成本与给定决策成本的差异: {optimal_cost - given_cost:.2f}")

# 敏感性分析
print("\n敏感性分析:")
for param in ['component_defect_rates', 'component_prices', 'component_inspect_costs', 'product_defect_rate', 'replacement_cost']:
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