from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GITHUB_APP_ID: str = ""
    GITHUB_WEBHOOK_SECRET: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    APP_SECRET_KEY: str = ""
    APP_URL: str = ""
    WEB_URL: str = ""
    CANARY_GITHUB_TOKEN: str = ""
    CANARY_AWS_ACCESS_KEY: str = ""
    ENABLE_RUNTIME_SANDBOX: bool = False
    ENABLE_PREMIUM_FEATURES: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
