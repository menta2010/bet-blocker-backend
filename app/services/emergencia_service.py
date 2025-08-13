from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from app.models import Usuario, EmergenciaContato
from app.services.email_service import send_email_emergencia

async def lidar_emergencia(
    db: Session,
    usuario: Usuario,
    background_tasks: BackgroundTasks | None = None,
) -> dict:
    emails: List[str] = [
        c.email
        for c in db.query(EmergenciaContato)
                   .filter(EmergenciaContato.usuario_id == usuario.id)
                   .all()
    ]

    if not emails:
        return {
            "mensagem": "Nenhum contato emergencial cadastrado.",
            "enviado_para": [],
            "data_hora": datetime.utcnow(),
        }

    if background_tasks:
        background_tasks.add_task(send_email_emergencia, emails, usuario.nome)
    else:
        await send_email_emergencia(emails, usuario.nome)

    return {
        "mensagem": "Alerta enviado com sucesso.",
        "enviado_para": emails,
        "data_hora": datetime.utcnow(),
    }
