import asyncio
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

conf = ConnectionConfig(
    MAIL_USERNAME="a0a63750c5a665",
    MAIL_PASSWORD="c40b7654879be2",
    MAIL_FROM="admin@exemplo.com",
    MAIL_FROM_NAME="Bet Blocker",
    MAIL_PORT=2525,
    MAIL_SERVER="smtp.mailtrap.io",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)

async def send_test_email():
    message = MessageSchema(
        subject="🚨 Teste de Alerta",
        recipients=["seuemail@exemplo.com"],  # Use seu email real no Mailtrap!
        body="Funcionou!",
        subtype="plain"
    )
    fm = FastMail(conf)
    await fm.send_message(message)

asyncio.run(send_test_email())