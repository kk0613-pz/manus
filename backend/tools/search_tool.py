"""Tavily 联网搜索工具实现。"""

import httpx

from config_loader import AppConfig

TAVILY_SEARCH_URL = "https://api.tavily.com/search"


def execute_web_search(query: str, config: AppConfig | None = None) -> dict:
    if config is None:
        from config_loader import load_config
        config = load_config()

    api_key = config.tavily.api_key.strip()
    if not api_key or api_key == "your-tavily-api-key":
        raise ValueError("Tavily API Key 未配置，请在 backend/config.yaml 中设置 tavily.api_key")

    payload = {
        "query": query,
        "search_depth": config.tavily.search_depth,
        "max_results": config.tavily.max_results,
        "include_answer": True,
    }

    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            TAVILY_SEARCH_URL,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
        response.raise_for_status()
        data = response.json()

    results = []
    for item in data.get("results", []):
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "content": item.get("content", ""),
        })

    return {
        "query": query,
        "answer": data.get("answer", ""),
        "results": results,
    }
