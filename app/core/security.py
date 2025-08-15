from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from fastapi_mail import ConnectionConfig
from app.config import settings
import secrets
# Configurações do token
SECRET_KEY = "seu_segredo_super_seguro"  # depois vamos mover isso pro .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_mail_config():
    print("🚨 DEBUG:", settings.SMTP_HOST)
    return ConnectionConfig(
        MAIL_USERNAME=settings.SMTP_USER,
        MAIL_PASSWORD=settings.SMTP_PASSWORD,
        MAIL_FROM=settings.ADMIN_EMAIL,
        MAIL_FROM_NAME="Bet Blocker",
        MAIL_PORT=settings.SMTP_PORT,
        MAIL_SERVER=settings.SMTP_HOST,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
    )

get_password_hash = hash_password


def generate_secure_token(nbytes: int = 32) -> str:
    return secrets.token_urlsafe(nbytes)

def minutes_from_now(mins: int) -> datetime:
    return datetime.utcnow() + timedelta(minutes=mins)
