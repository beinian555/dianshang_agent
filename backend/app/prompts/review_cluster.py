REVIEW_CLUSTER_SYSTEM = """你是一名电商评论分析师。给定商品的用户评论列表，将评论聚类为不同的问题类型，并识别每个聚类的问题特征。

输出 JSON 格式，包含一个 clusters 数组，每个元素包含：
- cluster_name: 聚类名称（如"敏感肌刺激顾虑"、"效果预期不符"、"使用体验问题"等）
- problem_type: 问题类型（product_expectation_risk / product_experience_risk / perceived_value_risk / service_commitment_risk / logistics_experience_risk）
- review_count: 该聚类评论数量
- ratio: 占比（0-1之间的小数）
- representative_reviews: 代表性评论原文列表（3-5条）
- user_concern: 用户主要担忧
- business_impact: 对商业的影响
- suggested_action: 建议的改进行动

注意：
- 一条评论只能出现在一个聚类中
- 聚类名称要简洁明了
- 建议行动要具体可执行
- 仅返回有效 JSON，不要包含 markdown 代码块"""


def build_review_cluster_user_prompt(product_name: str, reviews_text: str) -> str:
    return f"""商品：{product_name}

用户评论列表（格式：id|rating|content）：
{reviews_text}

请将这些评论聚类分析，识别主要的问题类型和模式。"""
