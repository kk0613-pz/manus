from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config_loader import load_config
from deepseek_service import DeepSeekService
from planner_service import PlannerService
from tools.registry import get_tool_registry

app = FastAPI(title="Manus AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = load_config()
deepseek_service = DeepSeekService(config)
planner_service = PlannerService(config, deepseek_service)


class MessageRequest(BaseModel):
    content: str = Field(..., min_length=1, description="用户发送的消息内容")


class MessageResponse(BaseModel):
    content: str
    role: str = "assistant"


@app.get("/")
def root():
    tools = [{"name": t.name, "description": t.description} for t in get_tool_registry()]
    return {
        "status": "ok",
        "message": "Manus AI Backend is running",
        "model": config.deepseek.model,
        "deepseek_configured": deepseek_service.is_configured,
        "tools": tools,
    }


@app.post("/api/message", response_model=MessageResponse)
def receive_message(payload: MessageRequest):
    try:
        plan = planner_service.plan(payload.content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        print(f"[Planner 调用失败] {exc}")
        raise HTTPException(status_code=502, detail="Planner 智能体调用失败，请稍后重试") from exc

    if plan.get("reasoning_content"):
        print(f"[Planner 推理过程]\n{plan['reasoning_content']}\n")

    print("[Planner 任务拆分]")
    print(f"  分析: {plan.get('analysis', '—')}")
    for task in plan.get("subtasks", []):
        tool = task.get("tool") or "无"
        print(f"  [{task.get('id')}] {task.get('title')} | 工具: {tool}")
        print(f"      {task.get('description')}")
    print()

    reply = PlannerService.format_plan_for_user(plan)
    return MessageResponse(content=reply)
