# Manus AI Backend

基于 Python + FastAPI + DeepSeek + Tavily 的后端服务。

## 功能

- **Planner 智能体**：用户消息进入后，自动拆分为子任务
- **Executor 智能体**：接收子任务，决策工具与参数并执行
- **汇总答案生成**：Executor 完成后，将所有结果输入模型生成回复草稿
- **Verify 智能体**：校验并优化汇总草稿，输出最终回答
- **SSE 流式接口**：前端实时展示 Todo 清单与打勾进度
- **工具注册表**：维护模型可调用的工具列表
- **搜索工具**：基于 Tavily API 的联网搜索（已注册，后续可执行）

## 目录结构

```
backend/
├── main.py                 # API 入口
├── planner_service.py      # Planner 智能体逻辑
├── executor_service.py     # Executor 智能体逻辑
├── synthesizer_service.py  # 汇总答案生成逻辑
├── verify_service.py       # Verify 智能体逻辑
├── deepseek_service.py     # DeepSeek 模型调用
├── config_loader.py        # 配置加载
├── prompts/
│   ├── planner.py          # Planner 提示词（维护在此）
│   ├── executor.py         # Executor 提示词（维护在此）
│   ├── synthesizer.py      # 汇总答案提示词（维护在此）
│   └── verify.py           # Verify 提示词（维护在此）
└── tools/
    ├── registry.py         # 工具列表注册表（维护在此）
    └── search_tool.py      # Tavily 搜索工具实现
```

## 配置

编辑 `config.yaml`：

```yaml
deepseek:
  api_key: "sk-xxxxxxxx"
  model: "deepseek-reasoner"

tavily:
  api_key: "tvly-xxxxxxxx"
  search_depth: "basic"
  max_results: 5
```

- DeepSeek Key：https://platform.deepseek.com/api_keys
- Tavily Key：https://app.tavily.com

## 启动

```bash
cd backend
py -m pip install -r requirements.txt
py -m uvicorn main:app --reload --port 8000
```

## 新增工具

1. 在 `tools/` 下实现工具逻辑
2. 在 `tools/registry.py` 的 `TOOL_REGISTRY` 中注册

## 修改 Planner 提示词

编辑 `prompts/planner.py` 中的 `PLANNER_SYSTEM_PROMPT` 和 `build_planner_user_prompt()`。

## 修改 Verify 提示词

编辑 `prompts/verify.py` 中的 `VERIFY_SYSTEM_PROMPT` 和 `build_verify_user_prompt()`。

## 后端日志（Executor 完成后）

- `[汇总答案 模型输入]` — 汇总模型的 system / user 完整输入（含 Executor 结果）
- `[Verify 输出]` — Verify 智能体校验后的 JSON 输出

## 接口

- `POST /api/message/stream` — SSE 流式（Planner → Executor → Todo 进度）
- `POST /api/message` — 同步兼容接口
