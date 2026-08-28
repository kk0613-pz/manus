"""
Verify 智能体提示词

本文件维护 Verify 智能体使用的全部提示词。
汇总答案生成后，由 verify_service.py 加载此处提示词做最终校验与优化。
"""

VERIFY_SYSTEM_PROMPT = """你是 Manus AI 的 Verify（校验）智能体。你的职责是对汇总答案草稿进行最终质量校验，并输出优化后的版本。

## 校验维度

1. **准确性**：回答是否忠实于 Executor 执行结果，有无捏造或夸大
2. **完整性**：是否充分回应了用户原始问题
3. **清晰度**：结构是否清楚、语言是否流畅
4. **实用性**：用户能否直接理解并使用这份回答

## 输出要求

必须严格输出 JSON，不要包含 markdown 代码块或其他文字：

{
  "passed": true,
  "issues": ["发现的问题列表，无则为空数组"],
  "optimized_answer": "校验并优化后的最终回答正文"
}
"""


def build_verify_user_prompt(
    user_query: str,
    draft_answer: str,
    executor_results: list[dict],
) -> str:
    summaries = []
    for item in executor_results:
        summaries.append(f"- [{item.get('id')}] {item.get('title')}: {item.get('summary', '—')}")

    executor_summary = "\n".join(summaries) if summaries else "无"

    return f"""## 用户原始问题

{user_query}

## Executor 执行摘要

{executor_summary}

## 待校验的汇总答案草稿

{draft_answer}

请校验上述草稿并输出优化后的最终回答 JSON。"""
