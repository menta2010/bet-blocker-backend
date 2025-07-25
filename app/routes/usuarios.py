from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.models import Usuario
from app.services.email_service import send_email_notificacao
from app.schemas import TrocaSenha, UserOut
from app.core.security import verify_password, get_password_hash

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

class TrocaEmailRequest(BaseModel):
    novo_email: EmailStr

@router.patch("/{usuario_id}/email", status_code=200)
async def trocar_email(
    usuario_id: int,
    payload: TrocaEmailRequest,
    db: Session = Depends(get_db),
):
    novo_email = payload.novo_email

    usuario_existente = db.query(Usuario).filter(Usuario.email == novo_email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este e-mail já está em uso."
        )

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    email_antigo = usuario.email
    nome_antigo = usuario.nome

    usuario.email = novo_email
    db.commit()

    try:
        await send_email_notificacao(
            email=email_antigo,
            nome=nome_antigo,
            mensagem="Seu e-mail foi alterado com sucesso para outro endereço."
        )
    except Exception as e:
        print("Erro ao enviar e-mail para o endereço antigo:", str(e))

    return {"mensagem": "E-mail atualizado com sucesso"}


@router.patch("/{usuario_id}/senha", response_model=UserOut)
async def trocar_senha(
    usuario_id: int,
    senha_data: TrocaSenha,
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if not verify_password(senha_data.senha_atual, usuario.senha):
        raise HTTPException(status_code=403, detail="Senha atual incorreta")

    usuario.senha = get_password_hash(senha_data.nova_senha)
    db.commit()
    db.refresh(usuario)

    try:
        await send_email_notificacao(
            email=usuario.email,
            nome=usuario.nome,
            mensagem="Sua senha foi alterada com sucesso. Se não foi você, entre em contato com o suporte."
        )
    except Exception as e:
        print("Erro ao enviar notificação de alteração de senha:", str(e))

    return usuario
