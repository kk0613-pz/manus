import os
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

CONFIG_PATH = Path(__file__).parent / "config.yaml"
EXAMPLE_CONFIG_PATH = Path(__file__).parent / "config.example.yaml"


class DeepSeekConfig(BaseModel):
    api_key: str = Field(default="", description="DeepSeek API Key")
    base_url: str = Field(default="https://api.deepseek.com")
    model: str = Field(default="deepseek-reasoner")
    reasoning_effort: str = Field(default="high")


class AppConfig(BaseModel):
    deepseek: DeepSeekConfig = Field(default_factory=DeepSeekConfig)


def load_config() -> AppConfig:
    config_path = CONFIG_PATH if CONFIG_PATH.exists() else EXAMPLE_CONFIG_PATH

    if not config_path.exists():
        return AppConfig()

    with config_path.open(encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    config = AppConfig.model_validate(raw)

    env_api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if env_api_key:
        config.deepseek.api_key = env_api_key

    return config
