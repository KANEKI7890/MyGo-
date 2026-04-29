import httpx

from app.core.config import get_settings
from app.schemas.ai import ChatMessage


async def chat_with_configured_model(messages: list[ChatMessage], temperature: float) -> str:
    settings = get_settings()
    if not settings.enable_ai_proxy or not settings.ai_base_url or not settings.ai_model:
        return "AI endpoint is reserved. Fill AI_BASE_URL, AI_MODEL, AI_API_KEY and set ENABLE_AI_PROXY=true."

    payload = {
        "model": settings.ai_model,
        "messages": [message.model_dump() for message in messages],
        "temperature": temperature,
    }
    headers = {"Content-Type": "application/json"}
    if settings.ai_api_key:
        headers["Authorization"] = f"Bearer {settings.ai_api_key}"

    base_url = settings.ai_base_url.rstrip("/")
    async with httpx.AsyncClient(timeout=settings.ai_timeout_seconds) as client:
        response = await client.post(f"{base_url}/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    return data["choices"][0]["message"]["content"]
