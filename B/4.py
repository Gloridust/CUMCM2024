import numpy as np
from scipy import stats
import itertools
import matplotlib.pyplot as plt
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 或者使用 'Heiti TC'
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

def calculate_sample_size(confidence_level, defect_rate, precision):
    z_score = stats.norm.ppf((1 + confidence_level) / 2)
    sample_size = int(np.ceil((z_score**2 * defect_rate * (1 - defect_rate)) / (precision**2)))
    return sample_size

def estimate_defect_rate(sample_size, defects, confidence_level):
    defect_rate = defects / sample_size
    margin_of_error = stats.norm.ppf((1 + confidence_level) / 2) * np.sqrt(defect_rate * (1 - defect_rate) / sample_size)
    return defect_rate, (defect_rate - margin_of_error, defect_rate + margin_of_error)

def calculate_cost(params, decisions, estimated_rates):
    total_cost = 0
    
    # 零配件成本
    for i, (price, inspect, est_rate) in enumerate(zip(params['component_prices'], 
                                                       decisions['component_inspections'],
                                                       estimated_rates['components'])):
        if inspect:
            total_cost += price + params['component_inspect_costs'][i]
        else:
            total_cost += price * (1 + est_rate)
    
    # 装配和检测成本
    for i, (assembly_cost, inspect, est_rate) in enumerate(zip(params['assembly_costs'],
                                                               decisions['product_inspections'],
                                                               estimated_rates['products'])):
        total_cost += assembly_cost
        if inspect:
            total_cost += params['product_inspect_costs'][i]
        
    # 不合格品处理成本
    for i, (disassemble, est_rate) in enumerate(zip(decisions['product_disassembles'],
                                                    estimated_rates['products'])):
        if disassemble:
            total_cost += est_rate * params['disassemble_costs'][i]
        else:
            total_cost += est_rate * (sum(params['component_prices']) + params['assembly_costs'][i])
    
    # 市场调换损失
    if not decisions['product_inspections'][-1]:
        total_cost += estimated_rates['products'][-1] * params['replacement_cost']
    
    return total_cost

def optimize_decisions(params, estimated_rates):
    best_cost = float('inf')
    best_decisions = None
    
    for component_inspections in itertools.product([True, False], repeat=len(params['component_prices'])):
        for product_inspections in itertools.product([True, False], repeat=len(params['assembly_costs'])):
            for product_disassembles in itertools.product([True, False], repeat=len(params['assembly_costs'])):
                decisions = {
                    'component_inspections': component_inspections,
                    'product_inspections': product_inspections,
                    'product_disassembles': product_disassembles
                }
                cost = calculate_cost(params, decisions, estimated_rates)
                if cost < best_cost:
                    best_cost = cost
                    best_decisions = decisions
    
    return best_decisions, best_cost

# 模拟抽样检测
def simulate_sampling(true_rate, sample_size, num_simulations=1000):
    results = []
    for _ in range(num_simulations):
        sample = np.random.binomial(sample_size, true_rate)
        est_rate, _ = estimate_defect_rate(sample_size, sample, 0.95)
        results.append(est_rate)
    return np.mean(results), np.std(results)

# 问题2的参数
params_2 = {
    'component_prices': [4, 18],
    'component_inspect_costs': [2, 3],
    'assembly_costs': [6],
    'product_inspect_costs': [3],
    'disassemble_costs': [5],
    'replacement_cost': 6,
    'market_price': 56
}

# 问题3的参数
params_3 = {
    'component_prices': [2, 8, 12, 2, 8, 12, 8, 12],
    'component_inspect_costs': [1, 1, 2, 1, 1, 2, 1, 2],
    'assembly_costs': [8, 8, 8],
    'product_inspect_costs': [4, 4, 6],
    'disassemble_costs': [6, 6, 10],
    'replacement_cost': 40,
    'market_price': 200
}

# 模拟抽样检测并优化决策
def analyze_with_sampling(params, true_rates, sample_sizes):
    estimated_rates = {
        'components': [],
        'products': []
    }
    
    for rate, size in zip(true_rates['components'], sample_sizes['components']):
        est_mean, est_std = simulate_sampling(rate, size)
        estimated_rates['components'].append(est_mean)
    
    for rate, size in zip(true_rates['products'], sample_sizes['products']):
        est_mean, est_std = simulate_sampling(rate, size)
        estimated_rates['products'].append(est_mean)
    
    best_decisions, best_cost = optimize_decisions(params, estimated_rates)
    
    return best_decisions, best_cost, estimated_rates

# 分析问题2
true_rates_2 = {
    'components': [0.1, 0.1],
    'products': [0.1]
}
sample_sizes_2 = {
    'components': [100, 100],
    'products': [100]
}

results_2 = analyze_with_sampling(params_2, true_rates_2, sample_sizes_2)

# 分析问题3
true_rates_3 = {
    'components': [0.1] * 8,
    'products': [0.1, 0.1, 0.1]
}
sample_sizes_3 = {
    'components': [100] * 8,
    'products': [100, 100, 100]
}

results_3 = analyze_with_sampling(params_3, true_rates_3, sample_sizes_3)

print("问题2结果:")
print("最优决策:", results_2[0])
print("估计成本:", results_2[1])
print("估计次品率:", results_2[2])

print("\n问题3结果:")
print("最优决策:", results_3[0])
print("估计成本:", results_3[1])
print("估计次品率:", results_3[2])

def plot_defect_rate_comparison(true_rates, estimated_rates, problem_num):
    """绘制估计次品率与真实次品率的比较图"""
    components = [f'零件{i+1}' for i in range(len(true_rates['components']))]
    products = [f'产品{i+1}' for i in range(len(true_rates['products']))]
    labels = components + products
    true_values = true_rates['components'] + true_rates['products']
    estimated_values = estimated_rates['components'] + estimated_rates['products']

    plt.figure(figsize=(12, 6))
    x = range(len(labels))
    plt.bar([i-0.2 for i in x], true_values, width=0.4, label='真实次品率', alpha=0.8)
    plt.bar([i+0.2 for i in x], estimated_values, width=0.4, label='估计次品率', alpha=0.8)
    plt.xlabel('零件/产品')
    plt.ylabel('次品率')
    plt.title(f'问题{problem_num}：抽样检测的准确性评估')
    plt.xticks(x, labels, rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'./4/defect_rate_accuracy_{problem_num}.png', dpi=300)
    plt.close()

def plot_decision_stability(decisions_list, problem_num):
    """绘制最优决策的稳定性分析图"""
    decision_types = ['component_inspections', 'product_inspections', 'product_disassembles']
    decision_names = ['零件检测', '产品检测', '产品拆解']

    fig, axes = plt.subplots(len(decision_types), 1, figsize=(12, 4*len(decision_types)))
    fig.suptitle(f'问题{problem_num}：决策稳定性分析', fontsize=16)

    for i, (decision_type, ax) in enumerate(zip(decision_types, axes)):
        decisions = [d[decision_type] for d in decisions_list]
        stability = np.mean(decisions, axis=0)
        x = range(len(stability))
        ax.bar(x, stability)
        ax.set_title(decision_names[i])
        ax.set_ylim(0, 1)
        ax.set_ylabel('决策概率')
        ax.set_xticks(x)
        ax.set_xticklabels([f'{i+1}' for i in x], rotation=45)

    plt.tight_layout()
    plt.savefig(f'./4/decision_robustness_{problem_num}.png', dpi=300)
    plt.close()

def plot_cost_distribution(costs, problem_num):
    """绘制成本分布图"""
    plt.figure(figsize=(10, 6))
    plt.hist(costs, bins=30, edgecolor='black')
    plt.xlabel('成本', fontsize=21)
    plt.ylabel('频率', fontsize=21)
    plt.title(f'问题{problem_num}：成本分布分析', fontsize=21)
    plt.savefig(f'./4/cost_variability_{problem_num}.png', dpi=300)
    plt.close()

def plot_sensitivity_analysis(params, true_rates, sample_sizes, param_name, param_range, problem_num):
    """绘制敏感性分析图"""
    costs = []
    for value in param_range:
        temp_params = params.copy()
        temp_params[param_name] = [value] * len(temp_params[param_name])
        _, cost, _ = analyze_with_sampling(temp_params, true_rates, sample_sizes)
        costs.append(cost)

    plt.figure(figsize=(10, 6))
    plt.plot(param_range, costs, marker='o')
    
    # 参数名称中文映射
    param_names_chinese = {
        'component_inspect_costs': '零件检测成本',
        'product_inspect_costs': '产品检测成本',
        'disassemble_costs': '拆解成本',
        'replacement_cost': '替换成本'
        # 可以根据需要添加更多参数
    }
    
    param_name_chinese = param_names_chinese.get(param_name, param_name)
    
    plt.xlabel(param_name_chinese)
    plt.ylabel('总成本')
    plt.title(f'问题{problem_num}：参数敏感性分析 - {param_name_chinese}的影响')
    plt.grid(True)
    plt.savefig(f'./4/parameter_sensitivity_{param_name}_{problem_num}.png', dpi=300)
    plt.close()

# 主程序
if __name__ == "__main__":
    # 创建保存图片的文件夹
    os.makedirs('./4', exist_ok=True)

    # 多次运行模拟以获得稳定性分析数据
    num_simulations = 100
    decisions_list_2 = []
    costs_2 = []
    decisions_list_3 = []
    costs_3 = []

    for _ in range(num_simulations):
        decisions_2, cost_2, rates_2 = analyze_with_sampling(params_2, true_rates_2, sample_sizes_2)
        decisions_list_2.append(decisions_2)
        costs_2.append(cost_2)

        decisions_3, cost_3, rates_3 = analyze_with_sampling(params_3, true_rates_3, sample_sizes_3)
        decisions_list_3.append(decisions_3)
        costs_3.append(cost_3)

    # 绘制可视化图表
    plot_defect_rate_comparison(true_rates_2, rates_2, 2)
    plot_defect_rate_comparison(true_rates_3, rates_3, 3)

    plot_decision_stability(decisions_list_2, 2)
    plot_decision_stability(decisions_list_3, 3)

    plot_cost_distribution(costs_2, 2)
    plot_cost_distribution(costs_3, 3)

    plot_sensitivity_analysis(params_2, true_rates_2, sample_sizes_2, 'component_inspect_costs', np.linspace(1, 5, 20), 2)
    plot_sensitivity_analysis(params_3, true_rates_3, sample_sizes_3, 'component_inspect_costs', np.linspace(1, 5, 20), 3)

    print("问题2结果:")
    print("最优决策:", decisions_list_2[-1])
    print("估计成本:", costs_2[-1])
    print("估计次品率:", rates_2)

    print("\n问题3结果:")
    print("最优决策:", decisions_list_3[-1])
    print("估计成本:", costs_3[-1])
    print("估计次品率:", rates_3)
