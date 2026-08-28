import json
from typing import Iterator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from config_loader import load_config
from deepseek_service import DeepSeekService
from executor_service import ExecutorService
from planner_service import PlannerService
from synthesizer_service import SynthesizerService
from tools.registry import get_tool_registry
from verify_service import VerifyService

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
executor_service = ExecutorService(config, deepseek_service)
synthesizer_service = SynthesizerService(config, deepseek_service)
verify_service = VerifyService(config, deepseek_service)


class MessageRequest(BaseModel):
    content: str = Field(..., min_length=1, description="用户发送的消息内容")


class MessageResponse(BaseModel):
    content: str
    role: str = "assistant"


def _sse_event(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _log_planner_output(plan: dict) -> None:
    if plan.get("reasoning_content"):
        print(f"[Planner 推理过程]\n{plan['reasoning_content']}\n")

    print("[Planner 任务拆分]")
    print(f"  分析: {plan.get('analysis', '—')}")
    for task in plan.get("subtasks", []):
        tool = task.get("tool") or "无"
        print(f"  [{task.get('id')}] {task.get('title')} | 工具: {tool}")
        print(f"      {task.get('description')}")
    print()


def _stream_pipeline(user_content: str) -> Iterator[str]:
    try:
        yield _sse_event({"type": "planning"})

        plan = planner_service.plan(user_content)
        _log_planner_output(plan)

        todos = [
            {
                "id": task.get("id"),
                "title": task.get("title"),
                "description": task.get("description"),
                "status": "pending",
            }
            for task in plan.get("subtasks", [])
        ]

        yield _sse_event({
            "type": "todos",
            "analysis": plan.get("analysis", ""),
            "todos": todos,
        })

        results = []
        print("[Executor 执行开始]")

        for subtask in plan.get("subtasks", []):
            yield _sse_event({"type": "todo_start", "id": subtask.get("id")})

            result = executor_service.execute_subtask(subtask, user_content, results)
            results.append(result)
            ExecutorService.log_execution(result)

            yield _sse_event({
                "type": "todo_done",
                "id": subtask.get("id"),
                "summary": result.get("summary", ""),
            })

        print("[Executor 执行完成]\n")

        yield _sse_event({"type": "synthesizing"})

        synthesis = synthesizer_service.generate(user_content, plan, results)
        draft_answer = synthesis["draft_answer"]

        yield _sse_event({"type": "verifying"})

        verify_result = verify_service.verify_and_optimize(
            user_content, draft_answer, results
        )
        final_answer = verify_result["optimized_answer"]

        yield _sse_event({"type": "complete", "content": final_answer})

    except ValueError as exc:
        print(f"[流程错误] {exc}")
        yield _sse_event({"type": "error", "message": str(exc)})
    except Exception as exc:
        print(f"[流程异常] {exc}")
        yield _sse_event({"type": "error", "message": "处理失败，请稍后重试"})


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


@app.post("/api/message/stream")
def receive_message_stream(payload: MessageRequest):
    return StreamingResponse(
        _stream_pipeline(payload.content),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/message", response_model=MessageResponse)
def receive_message(payload: MessageRequest):
    """兼容旧接口：同步返回完整结果。"""
    content_parts = []
    error_message = None

    for chunk in _stream_pipeline(payload.content):
        if not chunk.startswith("data: "):
            continue
        data = json.loads(chunk[6:].strip())
        event_type = data.get("type")

        if event_type == "complete":
            content_parts.append(data.get("content", ""))
        elif event_type == "error":
            error_message = data.get("message", "处理失败")

    if error_message:
        raise HTTPException(status_code=502, detail=error_message)

    return MessageResponse(content=content_parts[-1] if content_parts else "")
