import aiosmtplib
from email.message import EmailMessage
from app.config import settings

async def send_email_alert(tentativa):
    message = EmailMessage()
    message["From"] = settings.SMTP_USER
    message["To"] = settings.ADMIN_EMAIL
    message["Subject"] = "Alerta: Tentativa de acesso bloqueada"
    message.set_content(f"O usuário {tentativa.usuario_id} tentou acessar {tentativa.url} em {tentativa.data_hora}")

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=True,
    )
