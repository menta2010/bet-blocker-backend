from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ADMIN_EMAIL: str = "seuemail@exemplo.com"
    SMTP_HOST: str = "smtp.seuprovedor.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "usuario_smtp"
    SMTP_PASSWORD: str = "senha_smtp"

settings = Settings()
