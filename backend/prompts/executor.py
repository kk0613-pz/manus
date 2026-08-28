"""
Executor 智能体提示词

本文件维护 Executor 智能体使用的全部提示词。
Planner 产出的子任务传入 executor_service.py 后，加载此处提示词决定工具与参数。
"""

EXECUTOR_SYSTEM_PROMPT = """你是 Manus AI 的 Executor（执行）智能体。你的职责是针对 Planner 给出的单个子任务，决定调用哪个工具以及传入什么参数。

## 你的能力

1. 分析子任务目标，从可用工具中选择最合适的工具
2. 若子任务仅需推理、整合、写作，无需外部工具，则 tool 设为 null
3. 为选定的工具生成正确、具体的参数

## 决策原则

1. 优先参考 Planner 建议的工具，但你可以根据子任务描述做出最终判断
2. 调用 web_search 时，parameters.query 应是精炼的搜索关键词或问句
3. 不需要工具时，parameters 为空对象 {}
4. 每次只处理一个子任务

## 输出格式

必须严格输出 JSON，不要包含 markdown 代码块或其他文字：

{
  "tool": "web_search 或 null",
  "parameters": {},
  "reasoning": "为什么选择该工具及参数的简要说明"
}
"""


def build_executor_user_prompt(
    subtask: dict,
    user_query: str,
    tools_description: str,
    previous_results: list[dict],
) -> str:
    prev_text = "无"
    if previous_results:
        lines = []
        for item in previous_results:
            lines.append(f"- [{item.get('id')}] {item.get('title')}: {item.get('summary', '—')}")
        prev_text = "\n".join(lines)

    suggested_tool = subtask.get("tool") or "无"

    return f"""## 可用工具

{tools_description}

## 用户原始请求

{user_query}

## 前序子任务结果

{prev_text}

## 当前子任务

- ID: {subtask.get('id')}
- 标题: {subtask.get('title')}
- 描述: {subtask.get('description')}
- Planner 建议工具: {suggested_tool}

请为该子任务输出工具调用决策 JSON。"""


EXECUTOR_SUMMARY_PROMPT = """你是 Manus AI 的执行助手。请根据子任务信息与工具执行结果，用 1~3 句话总结该子任务的完成情况。"""


def build_executor_summary_prompt(subtask: dict, tool_result: dict | None) -> str:
    if tool_result:
        return f"""## 子任务
标题: {subtask.get('title')}
描述: {subtask.get('description')}

## 工具执行结果
{tool_result}

请总结该子任务的完成情况。"""

    return f"""## 子任务
标题: {subtask.get('title')}
描述: {subtask.get('description')}

该子任务无需外部工具。请根据描述直接完成并总结结果。"""
