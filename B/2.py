import numpy as np

def calculate_costs(params, decisions):
    """
    计算给定决策下的总成本
    
    params: 包含所有参数的字典
    decisions: 包含所有决策的字典
    """
    total_cost = 0
    revenue = 0
    
    # 零配件成本
    for i in [1, 2]:
        component_cost = params[f'component_{i}_price'] * (1 + params[f'component_{i}_defect_rate'])
        if decisions[f'inspect_component_{i}']:
            component_cost += params[f'component_{i}_inspect_cost']
        total_cost += component_cost

    # 装配成本
    total_cost += params['assembly_cost']

    # 成品检测成本
    if decisions['inspect_product']:
        total_cost += params['product_inspect_cost']

    # 计算成品的有效率
    effective_rate = 1
    for i in [1, 2]:
        if not decisions[f'inspect_component_{i}']:
            effective_rate *= (1 - params[f'component_{i}_defect_rate'])
    effective_rate *= (1 - params['product_defect_rate'])

    if decisions['inspect_product']:
        passed_rate = effective_rate
    else:
        passed_rate = 1

    # 收入和调换损失
    revenue = params['product_price'] * passed_rate
    exchange_loss = params['product_price'] * (1 - effective_rate) * params['exchange_loss_rate']

    # 拆解决策
    if decisions['disassemble_defective']:
        disassemble_cost = (1 - effective_rate) * params['disassemble_cost']
        recycle_gain = (1 - effective_rate) * (params['component_1_price'] * (1 - params['component_1_defect_rate']) +
                                               params['component_2_price'] * (1 - params['component_2_defect_rate']))
        total_cost += disassemble_cost - recycle_gain
    else:
        total_cost += (1 - effective_rate) * (params['component_1_price'] + params['component_2_price'])

    net_profit = revenue - total_cost - exchange_loss
    return net_profit, total_cost, revenue, exchange_loss

def optimize_decisions(params):
    """
    优化决策以最大化净利润
    
    params: 包含所有参数的字典
    """
    best_profit = -np.inf
    best_decisions = {}
    
    for inspect_1 in [True, False]:
        for inspect_2 in [True, False]:
            for inspect_product in [True, False]:
                for disassemble in [True, False]:
                    decisions = {
                        'inspect_component_1': inspect_1,
                        'inspect_component_2': inspect_2,
                        'inspect_product': inspect_product,
                        'disassemble_defective': disassemble
                    }
                    profit, cost, revenue, exchange_loss = calculate_costs(params, decisions)
                    if profit > best_profit:
                        best_profit = profit
                        best_decisions = decisions.copy()
                        best_metrics = {
                            'profit': profit,
                            'cost': cost,
                            'revenue': revenue,
                            'exchange_loss': exchange_loss
                        }
    
    return best_decisions, best_metrics

# 主程序
if __name__ == "__main__":
    scenarios = [
    {
        'component_1_defect_rate': 0.10, 'component_1_price': 4, 'component_1_inspect_cost': 2,
        'component_2_defect_rate': 0.10, 'component_2_price': 18, 'component_2_inspect_cost': 3,
        'product_defect_rate': 0.10, 'assembly_cost': 6, 'product_inspect_cost': 3,
        'product_price': 56, 'exchange_loss_rate': 6/56, 'disassemble_cost': 5
    },
    {
        'component_1_defect_rate': 0.20, 'component_1_price': 4, 'component_1_inspect_cost': 2,
        'component_2_defect_rate': 0.20, 'component_2_price': 18, 'component_2_inspect_cost': 3,
        'product_defect_rate': 0.20, 'assembly_cost': 6, 'product_inspect_cost': 3,
        'product_price': 56, 'exchange_loss_rate': 6/56, 'disassemble_cost': 5
    },
    {
        'component_1_defect_rate': 0.10, 'component_1_price': 4, 'component_1_inspect_cost': 2,
        'component_2_defect_rate': 0.10, 'component_2_price': 18, 'component_2_inspect_cost': 3,
        'product_defect_rate': 0.10, 'assembly_cost': 6, 'product_inspect_cost': 3,
        'product_price': 56, 'exchange_loss_rate': 30/56, 'disassemble_cost': 5
    },
    {
        'component_1_defect_rate': 0.20, 'component_1_price': 4, 'component_1_inspect_cost': 1,
        'component_2_defect_rate': 0.20, 'component_2_price': 18, 'component_2_inspect_cost': 1,
        'product_defect_rate': 0.20, 'assembly_cost': 6, 'product_inspect_cost': 2,
        'product_price': 56, 'exchange_loss_rate': 30/56, 'disassemble_cost': 5
    },
    {
        'component_1_defect_rate': 0.10, 'component_1_price': 4, 'component_1_inspect_cost': 8,
        'component_2_defect_rate': 0.20, 'component_2_price': 18, 'component_2_inspect_cost': 1,
        'product_defect_rate': 0.10, 'assembly_cost': 6, 'product_inspect_cost': 2,
        'product_price': 56, 'exchange_loss_rate': 10/56, 'disassemble_cost': 5
    },
    {
        'component_1_defect_rate': 0.05, 'component_1_price': 4, 'component_1_inspect_cost': 2,
        'component_2_defect_rate': 0.05, 'component_2_price': 18, 'component_2_inspect_cost': 3,
        'product_defect_rate': 0.05, 'assembly_cost': 6, 'product_inspect_cost': 2,
        'product_price': 56, 'exchange_loss_rate': 10/56, 'disassemble_cost': 40
    }
]

    for i, params in enumerate(scenarios, 1):
        print(f"\n情况 {i}:")
        best_decisions, best_metrics = optimize_decisions(params)
        
        print("最优决策:")
        for key, value in best_decisions.items():
            print(f"  {key}: {'是' if value else '否'}")
        
        print("决策结果:")
        for key, value in best_metrics.items():
            print(f"  {key}: {value:.2f}")
