from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    message: str = Field(
        ...,
        min_length=1,
        max_length=20000,
        description="User's message"
    )

    conversation_id: UUID | None = Field(
        default=None,
        description="Existing conversation ID. Null starts a new conversation."
    )


class ChatResponse(BaseModel):
    conversation_id: UUID
    message_id: UUID

    reply: str = Field(
        ...,
        description="Cortex's response"
    )