from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="Agentic AI runtime for Cortex",
    version=settings.APP_VERSION
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "cortex-ai-runtime",
        "environment": settings.ENVIRONMENT
    }