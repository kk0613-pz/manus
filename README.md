# Manus AI

Manus AI 是一款多智能体协作的 AI 助手应用，参考 Manus 产品形态构建。用户通过聊天界面提交任务，系统自动完成规划、执行、汇总与校验，并以流式方式在前端展示进度与最终回答。

## 功能特性

- **三栏式界面**：左侧任务列表、中间聊天区、右侧文件预览面板
- **多智能体流水线**：Planner → Executor → Synthesizer → Verify
- **实时 Todo 进度**：规划阶段显示「规划中...」，执行阶段逐项打勾
- **工具调用**：已集成 Tavily 联网搜索（`web_search`）
- **SSE 流式响应**：前后端实时同步任务状态

## 系统架构

```
用户输入
   │
   ▼
┌──────────┐    拆分子任务     ┌──────────┐    决策工具+参数    ┌──────────┐
│ Planner  │ ───────────────► │ Executor │ ─────────────────► │  工具层   │
└──────────┘                  └──────────┘                    └──────────┘
                                   │                                │
                                   └──────── 执行结果汇总 ────────────┘
                                              │
                                              ▼
                                    ┌──────────────┐    校验优化    ┌────────┐
                                    │ Synthesizer  │ ────────────► │ Verify │
                                    └──────────────┘               └────────┘
                                              │
                                              ▼
                                         前端展示
```

### 智能体说明

| 智能体 | 职责 | 提示词文件 |
|--------|------|------------|
| Planner | 分析用户请求，拆分为可执行子任务 | `backend/prompts/planner.py` |
| Executor | 针对每个子任务，决策调用工具及参数 | `backend/prompts/executor.py` |
| Synthesizer | 汇总 Executor 全部结果，生成回答草稿 | `backend/prompts/synthesizer.py` |
| Verify | 校验草稿准确性，输出优化后的最终回答 | `backend/prompts/verify.py` |

### 工具注册

工具定义维护在 `backend/tools/registry.py`，当前已注册：

- **web_search** — 基于 Tavily API 的联网搜索（实现见 `backend/tools/search_tool.py`）

## 项目结构

```
manus/
├── README.md                 # 项目说明（本文件）
├── frontend/                 # Vue 3 + Vite 前端
│   ├── src/
│   │   ├── App.vue
│   │   └── components/       # 聊天、Todo、任务侧栏等组件
│   └── vite.config.js
└── backend/                  # Python + FastAPI 后端
    ├── main.py               # API 入口 & SSE 流水线
    ├── planner_service.py
    ├── executor_service.py
    ├── synthesizer_service.py
    ├── verify_service.py
    ├── prompts/              # 各智能体提示词
    ├── tools/                  # 工具注册与实现
    ├── config.example.yaml   # 配置模板（可提交）
    └── config.yaml           # 本地配置（含 API Key，不提交）
```

## 快速开始

### 环境要求

- Node.js 18+
- Python 3.10+
- DeepSeek API Key（[申请地址](https://platform.deepseek.com/api_keys)）
- Tavily API Key（[申请地址](https://app.tavily.com)，使用搜索工具时需要）

### 1. 克隆仓库

```bash
git clone https://github.com/kk0613-pz/manus.git
cd manus
```

### 2. 配置 API Key

```bash
cp backend/config.example.yaml backend/config.yaml
```

编辑 `backend/config.yaml`，填入你的密钥：

```yaml
deepseek:
  api_key: "sk-你的DeepSeek密钥"
  model: "deepseek-reasoner"

tavily:
  api_key: "tvly-你的Tavily密钥"
```

也可通过环境变量覆盖（优先级高于配置文件）：

```bash
set DEEPSEEK_API_KEY=sk-xxx
set TAVILY_API_KEY=tvly-xxx
```

### 3. 启动后端

```bash
cd backend
py -m pip install -r requirements.txt
py -m uvicorn main:app --reload --port 8000
```

API 文档：http://localhost:8000/docs

### 4. 启动前端

```bash
cd frontend
npm install
npm run dev
```

浏览器访问：http://localhost:5173

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 服务状态与已注册工具列表 |
| POST | `/api/message/stream` | SSE 流式接口（推荐） |
| POST | `/api/message` | 同步接口（兼容） |

### SSE 事件类型

| 事件 | 说明 |
|------|------|
| `planning` | Planner 规划中 |
| `todos` | 子任务清单就绪 |
| `todo_start` | 某个子任务开始执行 |
| `todo_done` | 某个子任务执行完成 |
| `synthesizing` | 汇总答案生成中 |
| `verifying` | Verify 校验中 |
| `complete` | 最终回答就绪 |
| `error` | 错误 |

## 安全说明

以下内容**不会**被 Git 追踪，已在 `.gitignore` 中排除：

| 文件 | 说明 |
|------|------|
| `backend/config.yaml` | 本地 API Key 配置文件 |
| `.env` / `*.env` | 环境变量文件 |

仓库中仅包含 `backend/config.example.yaml` 配置模板（占位符，无真实密钥）。  
克隆项目后请自行复制模板并填入密钥，**切勿将含真实 Key 的 `config.yaml` 提交到 Git**。

## 分支说明

| 分支 | 说明 |
|------|------|
| `main` | 初始版本 |
| `Tavily_web_search` | Planner + Tavily 搜索工具 |
| `verify` | 完整多智能体流水线（当前最新） |

## 技术栈

**前端：** Vue 3 · Vite · 原生 CSS

**后端：** Python · FastAPI · DeepSeek API · Tavily API · SSE

## License

MIT
