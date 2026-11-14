
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import ChatRequest, ChatResponse
from app.core.database import get_db
from app.models import Conversation, Message
from app.services.llm.provider import generate_response

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

    conversation_id = conversation.id

    # 2. Save the user's message
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=request.message
    )

    db.add(user_message)
    db.commit()

    # 3. Retrieve the complete conversation history
    history = db.scalars(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc(), Message.id.asc())
    ).all()

    # 4. Build structured conversation history
    messages = [
        {
            "role": message.role,
            "content": message.content
        }
        for message in history
    ]

    # 5. Generate a response using the provider manager
    try:
        reply = generate_response(messages)

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc)
        ) from exc

    # 6. Save the assistant's response
    assistant_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=reply
    )

    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    # 7. Return the response
    return ChatResponse(
        conversation_id=conversation_id,
        message_id=assistant_message.id,
        reply=reply
    )
