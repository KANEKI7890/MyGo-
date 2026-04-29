from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.models.user import User
from app.schemas.ai import ChatRequest, ChatResponse
from app.services.ai_client import chat_with_configured_model

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    _: Annotated[User, Depends(get_current_user)],
) -> ChatResponse:
    settings = get_settings()
    configured = bool(settings.enable_ai_proxy and settings.ai_base_url and settings.ai_model)
    try:
        reply = await chat_with_configured_model(payload.messages, payload.temperature)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI provider request failed: {exc}",
        ) from exc

    return ChatResponse(configured=configured, model=settings.ai_model or None, reply=reply)
