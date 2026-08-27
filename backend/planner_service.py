import json
import re

from config_loader import AppConfig
from deepseek_service import DeepSeekService
from prompts.planner import PLANNER_SYSTEM_PROMPT, build_planner_user_prompt
from tools.registry import get_tools_for_planner


class PlannerService:
    def __init__(self, config: AppConfig, deepseek: DeepSeekService):
        self._config = config
        self._deepseek = deepseek

    def plan(self, user_query: str) -> dict:
        tools_description = get_tools_for_planner()
        user_prompt = build_planner_user_prompt(user_query, tools_description)

        result = self._deepseek.chat_with_messages(
            system_prompt=PLANNER_SYSTEM_PROMPT,
            user_message=user_prompt,
        )

        plan = self._parse_plan(result["content"])
        plan["reasoning_content"] = result.get("reasoning_content", "")
        return plan

    def _parse_plan(self, content: str) -> dict:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Planner 返回格式无效: {exc}") from exc

        if "subtasks" not in data or not isinstance(data["subtasks"], list):
            raise ValueError("Planner 返回缺少 subtasks 字段")

        return data

    @staticmethod
    def format_plan_for_user(plan: dict) -> str:
        lines = ["## 任务规划\n"]
        lines.append(f"**分析：** {plan.get('analysis', '—')}\n")
        lines.append("**子任务：**\n")

        for task in plan["subtasks"]:
            tool = task.get("tool")
            tool_label = tool if tool else "无需工具"
            lines.append(f"{task.get('id', '?')}. **{task.get('title', '未命名')}**")
            lines.append(f"   - 描述：{task.get('description', '—')}")
            lines.append(f"   - 工具：{tool_label}\n")

        return "\n".join(lines).strip()
