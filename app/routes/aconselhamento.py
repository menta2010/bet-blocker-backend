from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import AconselhamentoRequest, AconselhamentoResponse
from app.dependencies.auth import get_current_user
from app.models import Usuario
from app.utils.ai_utils import gerar_aconselhamento_ia

router = APIRouter(prefix="/aconselhamento", tags=["aconselhamento"])

@router.post("/", response_model=AconselhamentoResponse)
def obter_aconselhamento(
    payload: AconselhamentoRequest,
    usuario: Usuario = Depends(get_current_user)
):
    try:
        resposta = gerar_aconselhamento_ia(payload.mensagem)
        return AconselhamentoResponse(resposta=resposta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar aconselhamento: {str(e)}")
