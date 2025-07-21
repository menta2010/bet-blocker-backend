from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import DiarioEmocional, Usuario
from app.schemas import DiarioCreate, DiarioOut
from app.services.diario_service import analisar_diario
from typing import List

router = APIRouter(prefix="/diario", tags=["Diário Emocional"])

@router.post("/", response_model=DiarioOut)
async def criar_diario(
    entrada: DiarioCreate,
    usuario_id: int,
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter_by(id=usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    sentimento, resposta = await analisar_diario(entrada.texto)

    novo_diario = DiarioEmocional(
        texto=entrada.texto,
        sentimento=sentimento,
        resposta=resposta,
        usuario_id=usuario.id
    )
    db.add(novo_diario)
    db.commit()
    db.refresh(novo_diario)
    return novo_diario

@router.get("/", response_model=List[DiarioOut])
def listar_diarios(usuario_id: int, db: Session = Depends(get_db)):
    return db.query(DiarioEmocional).filter_by(usuario_id=usuario_id).order_by(DiarioEmocional.data.desc()).all()
