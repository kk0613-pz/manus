"""
汇总答案生成提示词

Executor 全部执行完成后，由 synthesizer_service.py 加载此处提示词，
将 Executor 产出结果汇总为用户可见的最终回复草稿。
"""

SYNTHESIZER_SYSTEM_PROMPT = """你是 Manus AI 的回答生成助手。你的职责是根据 Planner 规划与 Executor 执行结果，为用户生成一份完整、清晰、可直接阅读的最终回复。

## 要求

1. 严格基于 Executor 的执行结果作答，不要编造未出现在执行结果中的信息
2. 整合各子任务结论，形成连贯、自然的回答
3. 使用中文，语气专业友好
4. 若执行结果不足以回答用户问题，应如实说明缺失之处
5. 不要输出 JSON，直接输出给用户看的正文内容
"""


def build_synthesizer_user_prompt(
    user_query: str,
    plan: dict,
    executor_results: list[dict],
) -> str:
    result_lines = []
    for item in executor_results:
        result_lines.append(f"### 子任务 {item.get('id')}: {item.get('title')}")
        result_lines.append(f"描述: {item.get('description', '—')}")
        result_lines.append(f"工具: {item.get('tool') or '无'}")
        if item.get("parameters"):
            result_lines.append(f"参数: {item.get('parameters')}")
        result_lines.append(f"执行摘要: {item.get('summary', '—')}")
        if item.get("raw_result"):
            result_lines.append(f"原始结果: {item.get('raw_result')}")
        result_lines.append("")

    results_text = "\n".join(result_lines).strip() or "无执行结果"

    return f"""## 用户原始问题

{user_query}

## Planner 分析

{plan.get('analysis', '—')}

## Executor 执行结果

{results_text}

请基于以上信息，生成给用户看的最终回复草稿。"""
