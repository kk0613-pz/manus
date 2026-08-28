import json
import re

from config_loader import AppConfig
from deepseek_service import DeepSeekService
from prompts.executor import (
    EXECUTOR_SUMMARY_PROMPT,
    EXECUTOR_SYSTEM_PROMPT,
    build_executor_summary_prompt,
    build_executor_user_prompt,
)
from tools.registry import get_tool_by_name, get_tools_for_executor


class ExecutorService:
    def __init__(self, config: AppConfig, deepseek: DeepSeekService):
        self._config = config
        self._deepseek = deepseek

    def execute_subtask(
        self,
        subtask: dict,
        user_query: str,
        previous_results: list[dict],
    ) -> dict:
        decision = self._decide_tool(subtask, user_query, previous_results)
        execution = self._run_decision(subtask, decision, previous_results)

        return {
            "id": subtask.get("id"),
            "title": subtask.get("title"),
            "description": subtask.get("description"),
            "decision": decision,
            "tool": decision.get("tool"),
            "parameters": decision.get("parameters", {}),
            "reasoning": decision.get("reasoning", ""),
            "summary": execution.get("summary", ""),
            "raw_result": execution.get("raw_result"),
        }

    def _decide_tool(
        self,
        subtask: dict,
        user_query: str,
        previous_results: list[dict],
    ) -> dict:
        tools_description = get_tools_for_executor()
        user_prompt = build_executor_user_prompt(
            subtask, user_query, tools_description, previous_results
        )

        result = self._deepseek.chat_with_messages(
            system_prompt=EXECUTOR_SYSTEM_PROMPT,
            user_message=user_prompt,
        )

        return self._parse_decision(result["content"])

    def _run_decision(
        self,
        subtask: dict,
        decision: dict,
        previous_results: list[dict],
    ) -> dict:
        tool_name = decision.get("tool")
        parameters = decision.get("parameters") or {}

        raw_result = None
        if tool_name:
            tool = get_tool_by_name(tool_name)
            if not tool or not tool.handler:
                raise ValueError(f"未知工具: {tool_name}")

            if tool_name == "web_search":
                query = parameters.get("query", "").strip()
                if not query:
                    raise ValueError("web_search 缺少 query 参数")
                raw_result = tool.handler(query=query, config=self._config)
            else:
                raw_result = tool.handler(**parameters, config=self._config)

        if raw_result:
            summary_input = json.dumps(raw_result, ensure_ascii=False, indent=2)
            summary_prompt = build_executor_summary_prompt(subtask, summary_input)
        else:
            summary_prompt = build_executor_summary_prompt(subtask, None)

        summary = self._deepseek.chat_with_messages(
            system_prompt=EXECUTOR_SUMMARY_PROMPT,
            user_message=summary_prompt,
        )["content"]

        return {"summary": summary, "raw_result": raw_result}

    def _parse_decision(self, content: str) -> dict:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Executor 返回格式无效: {exc}") from exc

        tool = data.get("tool")
        if tool in ("null", "None", ""):
            tool = None
        data["tool"] = tool
        data.setdefault("parameters", {})
        data.setdefault("reasoning", "")
        return data

    @staticmethod
    def format_final_summary(plan: dict, results: list[dict]) -> str:
        lines = ["## 执行完成\n"]
        lines.append(f"**规划分析：** {plan.get('analysis', '—')}\n")

        for item in results:
            tool_label = item.get("tool") or "无需工具"
            lines.append(f"### {item.get('id')}. {item.get('title')}")
            lines.append(f"- 工具：{tool_label}")
            if item.get("parameters"):
                lines.append(f"- 参数：{json.dumps(item['parameters'], ensure_ascii=False)}")
            lines.append(f"- 结果：{item.get('summary', '—')}\n")

        return "\n".join(lines).strip()

    @staticmethod
    def log_execution(result: dict) -> None:
        print(f"  [Executor 子任务 {result.get('id')}] {result.get('title')}")
        print(f"    工具: {result.get('tool') or '无'}")
        if result.get("parameters"):
            print(f"    参数: {json.dumps(result['parameters'], ensure_ascii=False)}")
        print(f"    推理: {result.get('reasoning', '—')}")
        print(f"    结果: {result.get('summary', '—')}")
        print()
