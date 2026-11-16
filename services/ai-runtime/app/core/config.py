
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Cortex AI Runtime"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-3.8-flash"
    GROQ_API_KEY: str
    PRIMARY_LLM_PROVIDER: str = "groq"
    GROQ_MODEL: str = "openai/gpt-oss-120b"

    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "openrouter/free"

    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-2"
    EMBEDDING_DIMENSIONS: int = 768
    DATABASE_URL: str
    DOCUMENT_STORAGE_DIR: str = "storage/documents"
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/connectors/gmail/callback"
    GOOGLE_TOKEN_ENCRYPTION_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
