import itertools
import numpy as np
from scipy import stats

def simulate_sampling(true_rate, sample_size, num_simulations=1000):
    """模拟抽样检测过程"""
    results = []
    for _ in range(num_simulations):
        sample = np.random.binomial(sample_size, true_rate)
        est_rate = (sample + 1) / (sample_size + 2)  # Beta分布后验均值
        results.append(est_rate)
    return np.mean(results), np.std(results)

def calculate_cost(params, decisions, estimated_rates):
    """计算给定决策和估计次品率下的总成本"""
    total_cost = 0
    
    # 零配件成本
    for i, (price, inspect, est_rate) in enumerate(zip(
        params['component_prices'], 
        decisions['component_inspections'],
        estimated_rates['components']
    )):
        if inspect:
            total_cost += price + params['component_inspect_costs'][i]
        else:
            total_cost += price * (1 + est_rate)
    
    # 半成品和成品成本
    for i, (assembly_cost, inspect, disassemble, est_rate) in enumerate(zip(
        params['assembly_costs'],
        decisions['product_inspections'],
        decisions['product_disassembles'],
        estimated_rates['products']
    )):
        total_cost += assembly_cost
        if inspect:
            total_cost += params['product_inspect_costs'][i]
        if disassemble:
            total_cost += est_rate * params['disassemble_costs'][i]
        else:
            total_cost += est_rate * (sum(params['component_prices']) + assembly_cost)
    
    # 市场调换损失
    if not decisions['product_inspections'][-1]:
        total_cost += estimated_rates['products'][-1] * params['replacement_cost']
    
    return total_cost

def optimize_decisions(params, estimated_rates):
    """找出最优决策"""
    best_cost = float('inf')
    best_decisions = None
    
    for decisions in itertools.product(
        itertools.product([True, False], repeat=len(params['component_prices'])),
        itertools.product([True, False], repeat=len(params['assembly_costs'])),
        itertools.product([True, False], repeat=len(params['assembly_costs']))
    ):
        current_decisions = {
            'component_inspections': decisions[0],
            'product_inspections': decisions[1],
            'product_disassembles': decisions[2]
        }
        cost = calculate_cost(params, current_decisions, estimated_rates)
        if cost < best_cost:
            best_cost = cost
            best_decisions = current_decisions
    
    return best_decisions, best_cost

def analyze_with_sampling(params, true_rates, sample_sizes, num_iterations=100):
    """进行多次抽样分析"""
    all_decisions = []
    all_costs = []
    all_estimated_rates = []
    
    for _ in range(num_iterations):
        estimated_rates = {
            'components': [],
            'products': []
        }
        
        for rate, size in zip(true_rates['components'], sample_sizes['components']):
            est_mean, _ = simulate_sampling(rate, size)
            estimated_rates['components'].append(est_mean)
        
        for rate, size in zip(true_rates['products'], sample_sizes['products']):
            est_mean, _ = simulate_sampling(rate, size)
            estimated_rates['products'].append(est_mean)
        
        best_decisions, best_cost = optimize_decisions(params, estimated_rates)
        all_decisions.append(best_decisions)
        all_costs.append(best_cost)
        all_estimated_rates.append(estimated_rates)
    
    return all_decisions, all_costs, all_estimated_rates

# 问题4的参数（基于问题3的数据）
params = {
    'component_prices': [2, 8, 12, 2, 8, 12, 8, 12],
    'component_inspect_costs': [1, 1, 2, 1, 1, 2, 1, 2],
    'assembly_costs': [8, 8, 8],
    'product_inspect_costs': [4, 4, 6],
    'disassemble_costs': [6, 6, 10],
    'replacement_cost': 40,
    'market_price': 200
}

true_rates = {
    'components': [0.10] * 8,
    'products': [0.10, 0.10, 0.10]
}

sample_sizes = {
    'components': [100] * 8,
    'products': [100, 100, 100]
}

# 运行多次分析
all_decisions, all_costs, all_estimated_rates = analyze_with_sampling(params, true_rates, sample_sizes)

# 分析结果
most_common_decision = max(set(tuple(d['component_inspections']) for d in all_decisions), key=lambda x: [d['component_inspections'] for d in all_decisions].count(x))
average_cost = np.mean(all_costs)
std_cost = np.std(all_costs)

print("基于抽样检测的分析结果:")
print(f"最常见的零配件检测决策: {most_common_decision}")
print(f"平均成本: {average_cost:.2f} ± {std_cost:.2f}")

# 验证给定的决策
given_decisions = {
    'component_inspections': (False, False, False, False, False, False, False, False),
    'product_inspections': (False, False, False),
    'product_disassembles': (True, True, True)
}

# 使用平均估计次品率计算给定决策的成本
average_estimated_rates = {
    'components': [np.mean([rates['components'][i] for rates in all_estimated_rates]) for i in range(8)],
    'products': [np.mean([rates['products'][i] for rates in all_estimated_rates]) for i in range(3)]
}
given_cost = calculate_cost(params, given_decisions, average_estimated_rates)

print("\n给定决策的成本:")
print(f"成本: {given_cost:.2f}")

# 比较结果
print("\n验证结果:")
if abs(given_cost - average_cost) < std_cost:
    print("验证通过：给定的决策在合理范围内")
else:
    print("验证失败：给定的决策可能不是最优的")
    print(f"与平均最优成本的差异: {given_cost - average_cost:.2f}")

# 敏感性分析
print("\n敏感性分析:")
for param in ['component_prices', 'assembly_costs', 'replacement_cost']:
    if isinstance(params[param], list):
        for i in range(len(params[param])):
            original_value = params[param][i]
            params[param][i] *= 1.1  # 增加10%
            _, new_costs, _ = analyze_with_sampling(params, true_rates, sample_sizes, num_iterations=20)
            print(f"{param}[{i}] 增加10%后的平均成本: {np.mean(new_costs):.2f}")
            params[param][i] = original_value  # 恢复原值
    else:
        original_value = params[param]
        params[param] *= 1.1  # 增加10%
        _, new_costs, _ = analyze_with_sampling(params, true_rates, sample_sizes, num_iterations=20)
        print(f"{param} 增加10%后的平均成本: {np.mean(new_costs):.2f}")
        params[param] = original_value  # 恢复原值