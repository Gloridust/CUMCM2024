import numpy as np
import matplotlib.pyplot as plt
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 或者使用 'Heiti TC'
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

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


def plot_optimal_decisions(situations, results):
    """
    绘制各情况下的最优决策比较图
    """
    decisions = ['inspect_part1', 'inspect_part2', 'inspect_product', 'disassemble_defects']
    decision_labels = ['检测零件1', '检测零件2', '检测成品', '拆解不合格品']
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for i, (situation, result) in enumerate(zip(situations, results)):
        y_pos = [i] * len(decisions)
        colors = ['green' if result['best_decisions'][d] else 'red' for d in decisions]
        ax.scatter(y_pos, decisions, c=colors, s=100)
    
    ax.set_yticks(range(len(decisions)))
    ax.set_yticklabels(decision_labels)
    ax.set_xticks(range(len(situations)))
    ax.set_xticklabels([f'情况{i+1}' for i in range(len(situations))])
    ax.set_xlabel('不同情况')
    ax.set_title('各情况下的最优决策比较')
    
    # 添加图例
    ax.scatter([], [], c='green', label='是', s=100)
    ax.scatter([], [], c='red', label='否', s=100)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig('./2/optimal_decisions.png', dpi=300)
    plt.close()

def plot_minimum_costs(situations, results):
    """
    绘制各情况下的最低成本比较图
    """
    costs = [result['best_cost'] for result in results]
    
    plt.figure(figsize=(10, 6))
    plt.bar(range(1, len(situations) + 1), costs)
    plt.xlabel('情况')
    plt.ylabel('最低成本')
    plt.title('各情况下的最低成本比较')
    plt.xticks(range(1, len(situations) + 1))
    
    for i, cost in enumerate(costs):
        plt.text(i + 1, cost, f'{cost:.2f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('./2/minimum_costs.png', dpi=300)
    plt.close()

def plot_sensitivity_analysis(situation, param_name, param_range):
    """
    绘制参数敏感性分析图
    """
    costs = []
    for value in param_range:
        temp_situation = situation.copy()
        temp_situation[param_name] = value
        _, cost = analyze_situation(temp_situation)
        costs.append(cost)
    
    plt.figure(figsize=(10, 6))
    plt.plot(param_range, costs, marker='o')
    plt.xlabel(param_name)
    plt.ylabel('成本')
    plt.title(f'{param_name} 对成本的影响')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(f'./2/sensitivity_{param_name}.png', dpi=300)
    plt.close()

# 主程序
if __name__ == "__main__":
    # 创建保存图片的文件夹
    os.makedirs('./2', exist_ok=True)
    
    results = []
    for i, situation in enumerate(situations, 1):
        best_decisions, best_cost = analyze_situation(situation)
        results.append({
            'best_decisions': best_decisions,
            'best_cost': best_cost
        })
        print(f"\n情况 {i}:")
        print(f"最优决策: {best_decisions}")
        print(f"最低成本: {best_cost:.2f}")
        print("决策依据:")
        print(f"  - {'检测' if best_decisions['inspect_part1'] else '不检测'}零配件1")
        print(f"  - {'检测' if best_decisions['inspect_part2'] else '不检测'}零配件2")
        print(f"  - {'检测' if best_decisions['inspect_product'] else '不检测'}成品")
        print(f"  - {'拆解' if best_decisions['disassemble_defects'] else '不拆解'}不合格成品")
    
    # 绘制可视化图表
    plot_optimal_decisions(situations, results)
    plot_minimum_costs(situations, results)
    
    # 对第一种情况进行敏感性分析
    base_situation = situations[0]
    plot_sensitivity_analysis(base_situation, 'part1_defect_rate', np.linspace(0, 0.3, 30))
    plot_sensitivity_analysis(base_situation, 'part2_defect_rate', np.linspace(0, 0.3, 30))
    plot_sensitivity_analysis(base_situation, 'product_defect_rate', np.linspace(0, 0.3, 30))
    plot_sensitivity_analysis(base_situation, 'replacement_cost', np.linspace(0, 20, 30))