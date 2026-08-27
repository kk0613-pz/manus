# Manus AI Backend

基于 Python + FastAPI + DeepSeek Reasoner 的后端服务。

## 功能

- 接收前端消息并调用 DeepSeek 模型（默认 `deepseek-reasoner`）
- 在后端控制台打印模型推理过程与最终回复（便于调试）
- 将模型回复返回前端作为 AI 消息展示

## 配置

1. 复制配置模板：

```bash
cp config.example.yaml config.yaml
```

2. 编辑 `config.yaml`，填入你的 DeepSeek API Key：

```yaml
deepseek:
  api_key: "sk-xxxxxxxx"
  base_url: "https://api.deepseek.com"
  model: "deepseek-reasoner"
  reasoning_effort: "high"
```

也可通过环境变量 `DEEPSEEK_API_KEY` 覆盖配置文件中的 key。

API Key 申请：https://platform.deepseek.com/api_keys

## 启动

```bash
cd backend
py -m pip install -r requirements.txt
py -m uvicorn main:app --reload --port 8000
```

API 文档：http://localhost:8000/docs

## 接口

### POST /api/message

请求体：

```json
{
  "content": "你好"
}
```

响应：

```json
{
  "content": "你好！有什么我可以帮你的？",
  "role": "assistant"
}
```

## DeepSeek 接口说明

- 官方文档：https://api-docs.deepseek.com
- 使用 OpenAI 兼容的 `POST /chat/completions` 接口
- `deepseek-reasoner` 为思考/推理模式，响应中可能包含 `reasoning_content`（推理链）和 `content`（最终回答）
- 前端展示的是 `content` 字段；后端控制台会同时打印推理过程与最终回复
