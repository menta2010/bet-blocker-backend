from app.models import Usuario
from fastapi_mail import MessageSchema, FastMail
from app.core.security import get_mail_config
from sqlalchemy.orm import Session
from app.config import settings

APP_BASE_URL = getattr(settings, "APP_BASE_URL", "http://127.0.0.1:8000")

async def send_email_alert(db: Session, tentativa):
    usuario = db.query(Usuario).filter(Usuario.id == tentativa.usuario_id).first()
    if not usuario:
        print("Usuário não encontrado para envio de e-mail.")
        return

    email_destino = usuario.email

    assunto = "Tentativa de acesso bloqueada"
    corpo = f"""
    Olá {usuario.nome},

    Foi detectada uma tentativa de acesso ao site com ID {tentativa.site_id} no seu dispositivo.

    Se você não reconhece essa tentativa, recomendamos verificar suas configurações de segurança.

    Data/Hora: {tentativa.data_hora}
    """

    mail_config = get_mail_config()

    message = MessageSchema(
        subject=assunto,
        recipients=[email_destino],
        body=corpo,
        subtype="plain"
    )

    fastmail = FastMail(mail_config)
    await fastmail.send_message(message)

async def send_email_notificacao(email: str, nome: str, mensagem: str):
    assunto = "Notificação da sua conta"
    corpo = f"""
    Olá {nome},

    {mensagem}

    Se não foi você, entre em contato com o suporte.
    """

    mail_config = get_mail_config()

    message = MessageSchema(
        subject=assunto,
        recipients=[email],
        body=corpo,
        subtype="plain"
    )

    fastmail = FastMail(mail_config)
    await fastmail.send_message(message)

async def send_email_emergencia(nomes_email: list[str], nome_usuario: str):
    assunto = "Emergência - Ajuda solicitada"
    corpo = f"""
    Olá,

    {nome_usuario} solicitou ajuda emergencial pelo aplicativo.

    Recomendamos entrar em contato imediatamente para oferecer apoio.

    Esta é uma mensagem automática.
    """

    mail_config = get_mail_config()
    message = MessageSchema(
        subject=assunto,
        recipients=nomes_email,
        body=corpo,
        subtype="plain"
    )

    fastmail = FastMail(mail_config)
    await fastmail.send_message(message)

async def send_email_verification_code(email: str, nome: str, code: str, minutes_valid: int = 15):
    assunto = "Código de verificação de e-mail"
    corpo = f"""
    Olá {nome},

    Seu código de verificação é: {code}
    Ele expira em {minutes_valid} minutos.

    Se não foi você, ignore este e-mail.
    """
    mail_config = get_mail_config()
    message = MessageSchema(subject=assunto, recipients=[email], body=corpo, subtype="plain")
    fastmail = FastMail(mail_config)
    await fastmail.send_message(message)

async def send_password_reset_code(email: str, nome: str, code: str, minutes_valid: int = 15):
    assunto = "Código para redefinição de senha"
    corpo = f"""
    Olá {nome},

    Seu código para redefinição de senha é: {code}
    Ele expira em {minutes_valid} minutos.

    Se não foi você, ignore este e-mail.
    """
    mail_config = get_mail_config()
    message = MessageSchema(subject=assunto, recipients=[email], body=corpo, subtype="plain")
    fastmail = FastMail(mail_config)
    await fastmail.send_message(message)