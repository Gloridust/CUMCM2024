import numpy as np

def calculate_cost(params, decisions):
    total_cost = 0
    if decisions['inspect_part1']:
        total_cost += params['part1_cost'] + params['part1_inspect_cost']
    else:
        total_cost += params['part1_cost']
    if decisions['inspect_part2']:
        total_cost += params['part2_cost'] + params['part2_inspect_cost']
    else:
        total_cost += params['part2_cost']
    total_cost += params['assembly_cost']
    if decisions['inspect_product']:
        total_cost += params['product_inspect_cost']
    defect_rate = params['product_defect_rate']
    if decisions['disassemble_defects']:
        total_cost += defect_rate * params['disassemble_cost']
    else:
        total_cost += defect_rate * (params['part1_cost'] + params['part2_cost'] + params['assembly_cost'])
    if not decisions['inspect_product']:
        total_cost += defect_rate * params['replacement_cost']
    return total_cost

def optimize_decisions(params):
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
    params = situation
    best_decisions, best_cost = optimize_decisions(params)
    return best_decisions, best_cost

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

if __name__ == "__main__":
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