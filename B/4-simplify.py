import numpy as np
from scipy import stats
import itertools

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
    for i, (price, inspect, est_rate) in enumerate(zip(params['component_prices'], decisions['component_inspections'], estimated_rates['components'])):
        if inspect:
            total_cost += price + params['component_inspect_costs'][i]
        else:
            total_cost += price * (1 + est_rate)
    for i, (assembly_cost, inspect, est_rate) in enumerate(zip(params['assembly_costs'], decisions['product_inspections'], estimated_rates['products'])):
        total_cost += assembly_cost
        if inspect:
            total_cost += params['product_inspect_costs'][i]
    for i, (disassemble, est_rate) in enumerate(zip(decisions['product_disassembles'], estimated_rates['products'])):
        if disassemble:
            total_cost += est_rate * params['disassemble_costs'][i]
        else:
            total_cost += est_rate * (sum(params['component_prices']) + params['assembly_costs'][i])
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

def simulate_sampling(true_rate, sample_size, num_simulations=1000):
    results = []
    for _ in range(num_simulations):
        sample = np.random.binomial(sample_size, true_rate)
        est_rate, _ = estimate_defect_rate(sample_size, sample, 0.95)
        results.append(est_rate)
    return np.mean(results), np.std(results)

def analyze_with_sampling(params, true_rates, sample_sizes):
    estimated_rates = {'components': [], 'products': []}
    for rate, size in zip(true_rates['components'], sample_sizes['components']):
        est_mean, est_std = simulate_sampling(rate, size)
        estimated_rates['components'].append(est_mean)
    for rate, size in zip(true_rates['products'], sample_sizes['products']):
        est_mean, est_std = simulate_sampling(rate, size)
        estimated_rates['products'].append(est_mean)
    best_decisions, best_cost = optimize_decisions(params, estimated_rates)
    return best_decisions, best_cost, estimated_rates

params_2 = {
    'component_prices': [4, 18],
    'component_inspect_costs': [2, 3],
    'assembly_costs': [6],
    'product_inspect_costs': [3],
    'disassemble_costs': [5],
    'replacement_cost': 6,
    'market_price': 56
}

params_3 = {
    'component_prices': [2, 8, 12, 2, 8, 12, 8, 12],
    'component_inspect_costs': [1, 1, 2, 1, 1, 2, 1, 2],
    'assembly_costs': [8, 8, 8],
    'product_inspect_costs': [4, 4, 6],
    'disassemble_costs': [6, 6, 10],
    'replacement_cost': 40,
    'market_price': 200
}

true_rates_2 = {'components': [0.1, 0.1], 'products': [0.1]}
sample_sizes_2 = {'components': [100, 100], 'products': [100]}

true_rates_3 = {'components': [0.1] * 8, 'products': [0.1, 0.1, 0.1]}
sample_sizes_3 = {'components': [100] * 8, 'products': [100, 100, 100]}

if __name__ == "__main__":
    num_simulations = 100
    decisions_list_2, costs_2, rates_2 = [], [], None
    decisions_list_3, costs_3, rates_3 = [], [], None

    for _ in range(num_simulations):
        decisions_2, cost_2, rates_2 = analyze_with_sampling(params_2, true_rates_2, sample_sizes_2)
        decisions_list_2.append(decisions_2)
        costs_2.append(cost_2)

        decisions_3, cost_3, rates_3 = analyze_with_sampling(params_3, true_rates_3, sample_sizes_3)
        decisions_list_3.append(decisions_3)
        costs_3.append(cost_3)

    print("问题2结果:")
    print("最优决策:", decisions_list_2[-1])
    print("估计成本:", costs_2[-1])
    print("估计次品率:", rates_2)

    print("\n问题3结果:")
    print("最优决策:", decisions_list_3[-1])
    print("估计成本:", costs_3[-1])
    print("估计次品率:", rates_3)