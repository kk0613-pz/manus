import json
import re

from config_loader import AppConfig
from deepseek_service import DeepSeekService
from prompts.verify import VERIFY_SYSTEM_PROMPT, build_verify_user_prompt


class VerifyService:
    def __init__(self, config: AppConfig, deepseek: DeepSeekService):
        self._config = config
        self._deepseek = deepseek

    def verify_and_optimize(
        self,
        user_query: str,
        draft_answer: str,
        executor_results: list[dict],
    ) -> dict:
        user_prompt = build_verify_user_prompt(user_query, draft_answer, executor_results)

        result = self._deepseek.chat_with_messages(
            system_prompt=VERIFY_SYSTEM_PROMPT,
            user_message=user_prompt,
        )

        parsed = self._parse_verify_result(result["content"])

        print("[Verify 输出]")
        print(json.dumps(parsed, ensure_ascii=False, indent=2))
        print()

        return parsed

    def _parse_verify_result(self, content: str) -> dict:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            return {
                "passed": True,
                "issues": [],
                "optimized_answer": cleaned,
            }

        optimized = data.get("optimized_answer", "").strip()
        if not optimized:
            raise ValueError("Verify 返回缺少 optimized_answer 字段")

        return {
            "passed": bool(data.get("passed", True)),
            "issues": data.get("issues") or [],
            "optimized_answer": optimized,
        }
