import math
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 或者使用 'Heiti TC'
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

def calculate_sample_size(confidence_level, defect_rate, precision):
    z_score = stats.norm.ppf((1 + confidence_level) / 2)
    sample_size = math.ceil((z_score**2 * defect_rate * (1 - defect_rate)) / (precision**2))
    return sample_size

def binomial_test(n, x, p, alternative='greater'):
    result = stats.binomtest(x, n, p, alternative=alternative)
    return result.pvalue

def design_sampling_plan(nominal_defect_rate, confidence_level_reject=0.95, confidence_level_accept=0.90):
    sample_size_reject = calculate_sample_size(confidence_level_reject, nominal_defect_rate, 0.05)
    sample_size_accept = calculate_sample_size(confidence_level_accept, nominal_defect_rate, 0.05)
    sample_size = max(sample_size_reject, sample_size_accept)
    
    reject_limit = math.ceil(stats.binom.ppf(confidence_level_reject, sample_size, nominal_defect_rate))
    accept_limit = math.floor(stats.binom.ppf(1 - confidence_level_accept, sample_size, nominal_defect_rate))
    
    return {
        "sample_size": sample_size,
        "reject_limit": reject_limit,
        "accept_limit": accept_limit,
        "nominal_defect_rate": nominal_defect_rate,
        "confidence_level_reject": confidence_level_reject,
        "confidence_level_accept": confidence_level_accept
    }

def execute_sampling_plan(plan, actual_defects):
    p_value_reject = binomial_test(plan["sample_size"], actual_defects, plan["nominal_defect_rate"], alternative='greater')
    p_value_accept = binomial_test(plan["sample_size"], actual_defects, plan["nominal_defect_rate"], alternative='less')
    
    if actual_defects > plan["reject_limit"]:
        decision = "拒收"
    elif actual_defects <= plan["accept_limit"]:
        decision = "接收"
    else:
        decision = "需要进一步检验"
    
    return {
        "decision": decision,
        "p_value_reject": p_value_reject,
        "p_value_accept": p_value_accept,
        "actual_defects": actual_defects
    }

def plot_sample_size_vs_confidence(defect_rate, precision):
    confidence_levels = np.linspace(0.5, 0.99, 100)
    sample_sizes = [calculate_sample_size(cl, defect_rate, precision) for cl in confidence_levels]
    
    plt.figure(figsize=(10, 6))
    plt.plot(confidence_levels, sample_sizes)
    plt.title('样本量与置信水平的关系')
    plt.xlabel('置信水平')
    plt.ylabel('样本量')
    plt.grid(True)
    plt.savefig('./1/sample_size_vs_confidence.png')
    plt.close()

def plot_decision_boundaries(plan):
    x = np.arange(0, plan['sample_size'] + 1)
    y_reject = stats.binom.pmf(x, plan['sample_size'], plan['nominal_defect_rate'])
    
    plt.figure(figsize=(12, 6))
    plt.bar(x, y_reject, alpha=0.5, label='二项分布')
    plt.axvline(plan['reject_limit'], color='r', linestyle='--', label='拒收界限')
    plt.axvline(plan['accept_limit'], color='g', linestyle='--', label='接收界限')
    plt.title('拒收界限和接收界限的分布')
    plt.xlabel('不合格品数量')
    plt.ylabel('概率')
    
    # 调整x轴刻度
    max_x = min(plan['sample_size'], int(plan['nominal_defect_rate'] * plan['sample_size'] * 3))
    plt.xlim(0, max_x)
    
    # 设置x轴刻度间隔
    tick_interval = max(1, max_x // 10)  # 确保至少有10个刻度，但间隔不小于1
    plt.xticks(np.arange(0, max_x + 1, tick_interval))
    
    # 在图中标注重要的点
    plt.annotate(f'接收界限: {plan["accept_limit"]}', 
                 xy=(plan['accept_limit'], 0), 
                 xytext=(plan['accept_limit'], max(y_reject) / 2),
                 arrowprops=dict(facecolor='green', shrink=0.05))
    
    plt.annotate(f'拒收界限: {plan["reject_limit"]}', 
                 xy=(plan['reject_limit'], 0), 
                 xytext=(plan['reject_limit'], max(y_reject) / 2),
                 arrowprops=dict(facecolor='red', shrink=0.05))
    
    plt.legend()
    plt.tight_layout()
    plt.savefig('./1/decision_boundaries.png', dpi=300)
    plt.close()

def plot_decision_regions(plan):
    defect_rates = np.linspace(0, 0.3, 100)
    sample_sizes = np.arange(0, plan['sample_size'] + 1)
    
    decision_matrix = np.zeros((len(defect_rates), len(sample_sizes)))
    for i, rate in enumerate(defect_rates):
        for j, size in enumerate(sample_sizes):
            p_value = binomial_test(plan['sample_size'], size, rate)
            if size > plan['reject_limit']:
                decision_matrix[i, j] = 2  # 拒收
            elif size <= plan['accept_limit']:
                decision_matrix[i, j] = 0  # 接收
            else:
                decision_matrix[i, j] = 1  # 进一步检验
    
    plt.figure(figsize=(12, 8))
    plt.imshow(decision_matrix, aspect='auto', extent=[0, plan['sample_size'], 0.3, 0], cmap='RdYlGn')
    plt.colorbar(ticks=[0, 1, 2], label='决策 (0:接收, 1:进一步检验, 2:拒收)')
    plt.title('不同次品率下的决策区域')
    plt.xlabel('不合格品数量')
    plt.ylabel('实际次品率')
    plt.axhline(plan['nominal_defect_rate'], color='k', linestyle='--', label='标称次品率')
    plt.legend()
    plt.savefig('./1/decision_regions.png')
    plt.close()

# 主程序
if __name__ == "__main__":
    # 创建保存图片的文件夹
    os.makedirs('./1', exist_ok=True)

    nominal_defect_rate = 0.10  # 10%的标称次品率
    plan = design_sampling_plan(nominal_defect_rate)
    print("抽样检测方案:")
    print(f"样本量: {plan['sample_size']}")
    print(f"拒收界限 (95% 信度): {plan['reject_limit']}")
    print(f"接收界限 (90% 信度): {plan['accept_limit']}")
    print(f"标称次品率: {plan['nominal_defect_rate']:.2%}")
    
    # 生成可视化图表
    plot_sample_size_vs_confidence(nominal_defect_rate, 0.05)
    plot_decision_boundaries(plan)
    plot_decision_regions(plan)
    
    print("\n情况1: 95% 信度下拒收")
    actual_defects_reject = plan['reject_limit'] + 1
    result_reject = execute_sampling_plan(plan, actual_defects_reject)
    print(f"实际不合格品数: {result_reject['actual_defects']}")
    print(f"决策: {result_reject['decision']}")
    print(f"拒收 p 值: {result_reject['p_value_reject']:.4f}")
    
    print("\n情况2: 90% 信度下接收")
    actual_defects_accept = plan['accept_limit']
    result_accept = execute_sampling_plan(plan, actual_defects_accept)
    print(f"实际不合格品数: {result_accept['actual_defects']}")
    print(f"决策: {result_accept['decision']}")
    print(f"接收 p 值: {result_accept['p_value_accept']:.4f}")