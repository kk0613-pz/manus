from config_loader import AppConfig
from deepseek_service import DeepSeekService
from prompts.synthesizer import SYNTHESIZER_SYSTEM_PROMPT, build_synthesizer_user_prompt


class SynthesizerService:
    def __init__(self, config: AppConfig, deepseek: DeepSeekService):
        self._config = config
        self._deepseek = deepseek

    def generate(
        self,
        user_query: str,
        plan: dict,
        executor_results: list[dict],
    ) -> dict:
        user_prompt = build_synthesizer_user_prompt(user_query, plan, executor_results)

        print("[汇总答案 模型输入]")
        print(f"--- system ---\n{SYNTHESIZER_SYSTEM_PROMPT}\n")
        print(f"--- user ---\n{user_prompt}\n")

        result = self._deepseek.chat_with_messages(
            system_prompt=SYNTHESIZER_SYSTEM_PROMPT,
            user_message=user_prompt,
        )

        return {
            "draft_answer": result["content"],
            "model_input": {
                "system": SYNTHESIZER_SYSTEM_PROMPT,
                "user": user_prompt,
            },
        }
