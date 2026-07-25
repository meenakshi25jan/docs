from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.llm import LLMError, chat_completion
from app.models import GenerateRequest, GenerateResponse
from app.orchestration import build_messages

router = APIRouter(prefix="/api", tags=["generate"])


@router.post("/generate", response_model=GenerateResponse)
async def generate_prompt(request: GenerateRequest) -> GenerateResponse:
    settings = get_settings()
    messages, mode = build_messages(settings, request)

    try:
        output, usage = await chat_completion(settings, messages)
    except LLMError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return GenerateResponse(
        output=output,
        mode_used=mode.value,
        model=settings.openai_model,
        usage=usage,
    )
