from app.models import Usuario
from fastapi_mail import MessageSchema, FastMail
from app.core.security import get_mail_config
from sqlalchemy.orm import Session

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