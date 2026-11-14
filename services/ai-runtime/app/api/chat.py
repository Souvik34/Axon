
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import ChatRequest, ChatResponse
from app.core.database import get_db
from app.models import Conversation, Message

router = APIRouter(prefix="/api/v1", tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    # 1. Find or create a conversation
    if request.conversation_id:
        conversation = db.get(Conversation, request.conversation_id)

        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )
    else:
        conversation = Conversation(
            title=request.message[:255]
        )

        db.add(conversation)
        db.flush()

    # 2. Save the user's message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )

    db.add(user_message)

    # 3. Generate the temporary assistant response
    reply = "Cortex AI runtime is not connected to an LLM yet."

    # 4. Save the assistant's response
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=reply
    )

    db.add(assistant_message)

    # 5. Commit both messages
    db.commit()
    db.refresh(assistant_message)

    return ChatResponse(
        conversation_id=conversation.id,
        message_id=assistant_message.id,
        reply=reply
    )
