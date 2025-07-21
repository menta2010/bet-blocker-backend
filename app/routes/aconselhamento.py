from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import AconselhamentoRequest, AconselhamentoResponse, AconselhamentoOut
from app.dependencies.auth import get_current_user, get_db
from app.models import Usuario, Aconselhamento
from app.utils.ai_utils import gerar_aconselhamento_ia
from typing import List
from app.utils.model_utils import to_pydantic



router = APIRouter(prefix="/aconselhamento", tags=["aconselhamento"])

@router.post("/", response_model=AconselhamentoResponse)
def obter_aconselhamento(
    payload: AconselhamentoRequest,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        resposta = gerar_aconselhamento_ia(payload.mensagem)

        novo = Aconselhamento(
            mensagem=payload.mensagem,
            resposta=resposta,
            usuario_id=usuario.id
        )
        db.add(novo)
        db.commit()
        db.refresh(novo)

        return AconselhamentoResponse(resposta=resposta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar aconselhamento: {str(e)}")
    

@router.get("/", response_model=List[AconselhamentoOut])
def listar_aconselhamentos(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    registros = db.query(Aconselhamento).filter_by(usuario_id=usuario.id).order_by(Aconselhamento.data.desc()).all()
    return [to_pydantic(r, AconselhamentoOut) for r in registros]

