from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config_loader import load_config
from deepseek_service import DeepSeekService

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


class MessageRequest(BaseModel):
    content: str = Field(..., min_length=1, description="用户发送的消息内容")


class MessageResponse(BaseModel):
    content: str
    role: str = "assistant"


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Manus AI Backend is running",
        "model": config.deepseek.model,
        "deepseek_configured": deepseek_service.is_configured,
    }


@app.post("/api/message", response_model=MessageResponse)
def receive_message(payload: MessageRequest):
    try:
        result = deepseek_service.chat(payload.content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        print(f"[DeepSeek 调用失败] {exc}")
        raise HTTPException(status_code=502, detail="DeepSeek 模型调用失败，请稍后重试") from exc

    if result.get("reasoning_content"):
        print(f"[DeepSeek 推理过程]\n{result['reasoning_content']}\n")

    print(f"[DeepSeek 回复]\n{result['content']}\n")

    return MessageResponse(content=result["content"])
