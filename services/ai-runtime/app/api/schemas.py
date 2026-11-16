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
    execution_trace: dict | None = Field(
        default=None,
        description="Safe execution trace for agent workflows"
    )

class DocumentSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)


class RetrievedChunk(BaseModel):
    document_id: str
    chunk_index: int
    content: str
    similarity: float


class DocumentSearchResponse(BaseModel):
    query: str
    results: list[RetrievedChunk]
    total_results: int


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=10000)
    top_k: int = Field(default=3, ge=1, le=10)


class AskSource(BaseModel):
    document_id: str
    chunk_index: int
    similarity: float | None = None
    hybrid_score: float

class AskResponse(BaseModel):
    answer: str
    sources: list[AskSource]
