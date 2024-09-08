import math
import numpy as np
import scipy.stats as stats

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

if __name__ == "__main__":
    nominal_defect_rate = 0.10
    plan = design_sampling_plan(nominal_defect_rate)
    print("抽样检测方案:")
    print(f"样本量: {plan['sample_size']}")
    print(f"拒收界限 (95% 信度): {plan['reject_limit']}")
    print(f"接收界限 (90% 信度): {plan['accept_limit']}")
    print(f"标称次品率: {plan['nominal_defect_rate']:.2%}")
    
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