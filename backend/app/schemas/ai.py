from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(system|user|assistant)$")
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1)
    temperature: float = Field(default=0.7, ge=0, le=2)


class ChatResponse(BaseModel):
    configured: bool
    model: str | None = None
    reply: str
