import math
import scipy.stats as stats

def calculate_sample_size(confidence_level, defect_rate, precision):
    """
    计算所需的样本量
    :param confidence_level: 置信水平
    :param defect_rate: 预期的次品率
    :param precision: 允许的误差范围
    :return: 所需的样本量
    """
    z_score = stats.norm.ppf((1 + confidence_level) / 2)
    sample_size = math.ceil((z_score**2 * defect_rate * (1 - defect_rate)) / (precision**2))
    return sample_size

def binomial_test(n, x, p, alternative='greater'):
    """
    进行二项分布检验
    :param n: 样本量
    :param x: 不合格品数量
    :param p: 标称次品率
    :param alternative: 替代假设类型 ('greater', 'less', 'two-sided')
    :return: p值
    """
    result = stats.binomtest(x, n, p, alternative=alternative)
    return result.pvalue

def design_sampling_plan(nominal_defect_rate, confidence_level_reject=0.95, confidence_level_accept=0.90):
    """
    设计抽样检测方案
    :param nominal_defect_rate: 标称次品率
    :param confidence_level_reject: 拒收的置信水平
    :param confidence_level_accept: 接收的置信水平
    :return: 抽样方案
    """
    # 计算拒收所需的最小样本量
    sample_size_reject = calculate_sample_size(confidence_level_reject, nominal_defect_rate, 0.05)
    
    # 计算接收所需的最小样本量
    sample_size_accept = calculate_sample_size(confidence_level_accept, nominal_defect_rate, 0.05)
    
    # 取较大的样本量
    sample_size = max(sample_size_reject, sample_size_accept)
    
    # 计算拒收界限
    reject_limit = math.ceil(nominal_defect_rate * sample_size)
    
    return {
        "sample_size": sample_size,
        "reject_limit": reject_limit,
        "nominal_defect_rate": nominal_defect_rate,
        "confidence_level_reject": confidence_level_reject,
        "confidence_level_accept": confidence_level_accept
    }

def execute_sampling_plan(plan, actual_defects):
    """
    执行抽样检测方案
    :param plan: 抽样方案
    :param actual_defects: 实际检测到的不合格品数量
    :return: 检测结果
    """
    p_value = binomial_test(plan["sample_size"], actual_defects, plan["nominal_defect_rate"])
    
    if actual_defects > plan["reject_limit"]:
        decision = "拒收"
    else:
        decision = "接收"
    
    return {
        "decision": decision,
        "p_value": p_value,
        "actual_defects": actual_defects
    }

# 示例使用
if __name__ == "__main__":
    nominal_defect_rate = 0.10  # 10%的标称次品率
    plan = design_sampling_plan(nominal_defect_rate)
    print("抽样检测方案:", plan)
    
    # 模拟检测结果
    actual_defects = 12  # 假设在抽样中发现12个不合格品
    result = execute_sampling_plan(plan, actual_defects)
    print("检测结果:", result)