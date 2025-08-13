from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ADMIN_EMAIL: str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    DATABASE_URL: str  # <-- Adicione esta linha
    openai_api_key: str 
    OPENAI_MODEL_DIARIO: str
    OPENAI_MODEL_CONSELHO: str 
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
