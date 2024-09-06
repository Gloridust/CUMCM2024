import numpy as np

def calculate_cost(params, decisions):
    """
    计算给定决策下的总成本
    
    params: 包含所有参数的字典
    decisions: 包含所有决策的字典
    """
    total_cost = 0
    
    # 零配件1成本
    if decisions['inspect_part1']:
        total_cost += params['part1_cost'] + params['part1_inspect_cost']
    else:
        total_cost += params['part1_cost']
    
    # 零配件2成本
    if decisions['inspect_part2']:
        total_cost += params['part2_cost'] + params['part2_inspect_cost']
    else:
        total_cost += params['part2_cost']
    
    # 装配成本
    total_cost += params['assembly_cost']
    
    # 成品检测成本
    if decisions['inspect_product']:
        total_cost += params['product_inspect_cost']
    
    # 不合格品处理成本
    defect_rate = params['product_defect_rate']
    if decisions['disassemble_defects']:
        total_cost += defect_rate * params['disassemble_cost']
    else:
        total_cost += defect_rate * (params['part1_cost'] + params['part2_cost'] + params['assembly_cost'])
    
    # 市场调换损失
    if not decisions['inspect_product']:
        total_cost += defect_rate * params['replacement_cost']
    
    return total_cost

def optimize_decisions(params):
    """
    优化决策，返回最优决策和对应的成本
    
    params: 包含所有参数的字典
    """
    best_cost = float('inf')
    best_decisions = {}
    
    for inspect_part1 in [True, False]:
        for inspect_part2 in [True, False]:
            for inspect_product in [True, False]:
                for disassemble_defects in [True, False]:
                    decisions = {
                        'inspect_part1': inspect_part1,
                        'inspect_part2': inspect_part2,
                        'inspect_product': inspect_product,
                        'disassemble_defects': disassemble_defects
                    }
                    cost = calculate_cost(params, decisions)
                    if cost < best_cost:
                        best_cost = cost
                        best_decisions = decisions
    
    return best_decisions, best_cost

def analyze_situation(situation):
    """
    分析给定情况并返回最优决策
    
    situation: 包含所有参数的字典
    """
    params = {
        'part1_defect_rate': situation['part1_defect_rate'],
        'part1_cost': situation['part1_cost'],
        'part1_inspect_cost': situation['part1_inspect_cost'],
        'part2_defect_rate': situation['part2_defect_rate'],
        'part2_cost': situation['part2_cost'],
        'part2_inspect_cost': situation['part2_inspect_cost'],
        'product_defect_rate': situation['product_defect_rate'],
        'assembly_cost': situation['assembly_cost'],
        'product_inspect_cost': situation['product_inspect_cost'],
        'market_price': situation['market_price'],
        'replacement_cost': situation['replacement_cost'],
        'disassemble_cost': situation['disassemble_cost']
    }
    
    best_decisions, best_cost = optimize_decisions(params)
    
    return best_decisions, best_cost

# 完整的六种情况数据
situations = [
    {
        'part1_defect_rate': 0.10, 'part1_cost': 4, 'part1_inspect_cost': 2,
        'part2_defect_rate': 0.10, 'part2_cost': 18, 'part2_inspect_cost': 3,
        'product_defect_rate': 0.10, 'assembly_cost': 6, 'product_inspect_cost': 3,
        'market_price': 56, 'replacement_cost': 6, 'disassemble_cost': 5
    },
    {
        'part1_defect_rate': 0.20, 'part1_cost': 4, 'part1_inspect_cost': 2,
        'part2_defect_rate': 0.20, 'part2_cost': 18, 'part2_inspect_cost': 3,
        'product_defect_rate': 0.20, 'assembly_cost': 6, 'product_inspect_cost': 3,
        'market_price': 56, 'replacement_cost': 6, 'disassemble_cost': 5
    },
    {
        'part1_defect_rate': 0.10, 'part1_cost': 4, 'part1_inspect_cost': 2,
        'part2_defect_rate': 0.10, 'part2_cost': 18, 'part2_inspect_cost': 3,
        'product_defect_rate': 0.10, 'assembly_cost': 6, 'product_inspect_cost': 3,
        'market_price': 56, 'replacement_cost': 30, 'disassemble_cost': 5
    },
    {
        'part1_defect_rate': 0.20, 'part1_cost': 4, 'part1_inspect_cost': 1,
        'part2_defect_rate': 0.20, 'part2_cost': 18, 'part2_inspect_cost': 1,
        'product_defect_rate': 0.20, 'assembly_cost': 6, 'product_inspect_cost': 2,
        'market_price': 56, 'replacement_cost': 30, 'disassemble_cost': 5
    },
    {
        'part1_defect_rate': 0.10, 'part1_cost': 4, 'part1_inspect_cost': 8,
        'part2_defect_rate': 0.20, 'part2_cost': 18, 'part2_inspect_cost': 1,
        'product_defect_rate': 0.10, 'assembly_cost': 6, 'product_inspect_cost': 2,
        'market_price': 56, 'replacement_cost': 10, 'disassemble_cost': 5
    },
    {
        'part1_defect_rate': 0.05, 'part1_cost': 4, 'part1_inspect_cost': 2,
        'part2_defect_rate': 0.05, 'part2_cost': 18, 'part2_inspect_cost': 3,
        'product_defect_rate': 0.05, 'assembly_cost': 6, 'product_inspect_cost': 2,
        'market_price': 56, 'replacement_cost': 10, 'disassemble_cost': 40
    }
]

for i, situation in enumerate(situations, 1):
    best_decisions, best_cost = analyze_situation(situation)
    print(f"\n情况 {i}:")
    print(f"最优决策: {best_decisions}")
    print(f"最低成本: {best_cost:.2f}")
    print("决策依据:")
    print(f"  - {'检测' if best_decisions['inspect_part1'] else '不检测'}零配件1")
    print(f"  - {'检测' if best_decisions['inspect_part2'] else '不检测'}零配件2")
    print(f"  - {'检测' if best_decisions['inspect_product'] else '不检测'}成品")
    print(f"  - {'拆解' if best_decisions['disassemble_defects'] else '不拆解'}不合格成品")