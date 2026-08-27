from openai import OpenAI

from config_loader import AppConfig


class DeepSeekService:
    def __init__(self, config: AppConfig):
        self._config = config.deepseek
        self._client = OpenAI(
            api_key=self._config.api_key,
            base_url=self._config.base_url,
        )

    @property
    def is_configured(self) -> bool:
        key = self._config.api_key.strip()
        return bool(key) and key != "your-deepseek-api-key"

    def chat(self, user_message: str) -> dict[str, str]:
        return self.chat_with_messages(
            system_prompt="你是 Manus AI 助手，请用简洁清晰的中文回答用户问题。",
            user_message=user_message,
        )

    def chat_with_messages(self, system_prompt: str, user_message: str) -> dict[str, str]:
        if not self.is_configured:
            raise ValueError(
                "DeepSeek API Key 未配置，请在 backend/config.yaml 中设置 deepseek.api_key"
            )

        model = self._config.model
        request_kwargs: dict = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "stream": False,
        }

        # deepseek-reasoner 为思考模式；V4 模型需显式开启 thinking
        if model.startswith("deepseek-v4"):
            request_kwargs["reasoning_effort"] = self._config.reasoning_effort
            request_kwargs["extra_body"] = {"thinking": {"type": "enabled"}}
        elif self._config.reasoning_effort:
            request_kwargs["reasoning_effort"] = self._config.reasoning_effort

        response = self._client.chat.completions.create(**request_kwargs)
        message = response.choices[0].message

        reasoning = getattr(message, "reasoning_content", None) or ""
        content = message.content or ""

        if not content.strip():
            raise ValueError("DeepSeek 返回内容为空")

        return {
            "content": content.strip(),
            "reasoning_content": reasoning.strip(),
        }
