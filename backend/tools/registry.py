"""
工具注册表

本文件维护模型可调用的全部工具定义。
新增工具时在此文件的 TOOL_REGISTRY 中注册，并在 tools/ 目录下实现对应执行逻辑。
"""

from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: Optional[Callable[..., dict[str, Any]]] = None


def _get_search_handler():
    from tools.search_tool import execute_web_search
    return execute_web_search


TOOL_REGISTRY: list[ToolDefinition] = [
    ToolDefinition(
        name="web_search",
        description="联网搜索工具。用于查询实时信息、新闻、资料、数据等需要最新或外部信息的场景。",
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词或问题",
                },
            },
            "required": ["query"],
        },
        handler=None,
    ),
]


def get_tool_registry() -> list[ToolDefinition]:
    """返回已绑定 handler 的工具列表。"""
    registry = []
    for tool in TOOL_REGISTRY:
        handler = tool.handler
        if tool.name == "web_search" and handler is None:
            handler = _get_search_handler()
        registry.append(
            ToolDefinition(
                name=tool.name,
                description=tool.description,
                parameters=tool.parameters,
                handler=handler,
            )
        )
    return registry


def get_tools_for_planner() -> str:
    """生成供 Planner 阅读的 tools 描述文本。"""
    lines = []
    for tool in get_tool_registry():
        params = ", ".join(tool.parameters.get("required", []))
        lines.append(f"- **{tool.name}**: {tool.description}")
        if params:
            lines.append(f"  参数: {params}")
    return "\n".join(lines)


def get_tool_by_name(name: str) -> Optional[ToolDefinition]:
    for tool in get_tool_registry():
        if tool.name == name:
            return tool
    return None
