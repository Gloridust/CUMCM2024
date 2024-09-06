import numpy as np
from scipy import stats

def calculate_sample_size(confidence_level, defect_rate, precision):
    """计算所需的样本量"""
    z_score = stats.norm.ppf((1 + confidence_level) / 2)
    sample_size = int(np.ceil((z_score**2 * defect_rate * (1 - defect_rate)) / (precision**2)))
    return sample_size

def binomial_test(n, x, p, alternative='greater'):
    """进行二项分布检验"""
    return stats.binomtest(x, n, p, alternative=alternative).pvalue

def simulate_sampling_plan(true_defect_rate, nominal_defect_rate, sample_size, num_simulations=10000):
    """模拟抽样检测方案"""
    reject_count = 0
    accept_count = 0
    
    for _ in range(num_simulations):
        sample = np.random.binomial(sample_size, true_defect_rate)
        p_value = binomial_test(sample_size, sample, nominal_defect_rate)
        
        if p_value < 0.05:  # 95% 置信水平
            reject_count += 1
        if p_value > 0.10:  # 90% 置信水平
            accept_count += 1
    
    reject_rate = reject_count / num_simulations
    accept_rate = accept_count / num_simulations
    
    return reject_rate, accept_rate

# 验证参数
nominal_defect_rate = 0.10  # 标称次品率
confidence_level_reject = 0.95  # 拒收的置信水平
confidence_level_accept = 0.90  # 接收的置信水平
precision = 0.05  # 允许的误差范围

# 计算样本量
sample_size = calculate_sample_size(confidence_level_reject, nominal_defect_rate, precision)
print(f"计算的样本量: {sample_size}")

# 验证不同真实次品率下的方案表现
true_defect_rates = [0.08, 0.09, 0.10, 0.11, 0.12]

for true_rate in true_defect_rates:
    reject_rate, accept_rate = simulate_sampling_plan(true_rate, nominal_defect_rate, sample_size)
    print(f"\n真实次品率: {true_rate:.2f}")
    print(f"拒收率 (应 > 0.95 当真实率 > 标称率): {reject_rate:.4f}")
    print(f"接收率 (应 > 0.90 当真实率 < 标称率): {accept_rate:.4f}")

# 验证方案是否满足要求
print("\n验证结果:")
if simulate_sampling_plan(0.11, nominal_defect_rate, sample_size)[0] > 0.95:
    print("通过: 95%置信度下正确拒收次品率超过标称值的情况")
else:
    print("未通过: 95%置信度下正确拒收次品率超过标称值的情况")

if simulate_sampling_plan(0.09, nominal_defect_rate, sample_size)[1] > 0.90:
    print("通过: 90%置信度下正确接收次品率不超过标称值的情况")
else:
    print("未通过: 90%置信度下正确接收次品率不超过标称值的情况")