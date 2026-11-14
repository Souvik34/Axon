from fastapi import FastAPI

from app.core.config import settings
from app.api.chat import router as chat_router
from app.api.documents import router as documents_router

app = FastAPI(
    title=settings.APP_NAME,
    description="Agentic AI runtime for Cortex",
    version=settings.APP_VERSION
)

app.include_router(chat_router)
app.include_router(documents_router)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "cortex-ai-runtime",
        "environment": settings.ENVIRONMENT
    }