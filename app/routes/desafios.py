from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.models import DesafioAbstinencia, Usuario
from app.schemas import DesafioCreate, DesafioOut
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/desafios", tags=["Desafio de Abstinência"])

@router.post("/", response_model=DesafioOut, status_code=201)
def criar_desafio(payload: DesafioCreate,
                  db: Session = Depends(get_db),
                  usuario: Usuario = Depends(get_current_user)):
    # Permitir apenas 1 desafio "em aberto" por usuário
    em_aberto = db.query(DesafioAbstinencia).filter(
        DesafioAbstinencia.usuario_id == usuario.id,
        DesafioAbstinencia.concluido == False
    ).first()
    if em_aberto:
        raise HTTPException(status_code=400, detail="Você já possui um desafio em andamento.")

    novo = DesafioAbstinencia(
        usuario_id=usuario.id,
        dias_meta=payload.dias_meta,
        data_inicio=date.today(),
        streak_atual=0,
        concluido=False,
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

@router.get("/me", response_model=list[DesafioOut])
def listar_meus_desafios(db: Session = Depends(get_db),
                         usuario: Usuario = Depends(get_current_user)):
    return db.query(DesafioAbstinencia)\
        .filter(DesafioAbstinencia.usuario_id == usuario.id)\
        .order_by(DesafioAbstinencia.criado_em.desc()).all()

@router.patch("/{desafio_id}/checkin", response_model=DesafioOut)
def fazer_checkin(desafio_id: int,
                  db: Session = Depends(get_db),
                  usuario: Usuario = Depends(get_current_user)):
    desafio = db.query(DesafioAbstinencia).filter(
        DesafioAbstinencia.id == desafio_id,
        DesafioAbstinencia.usuario_id == usuario.id
    ).first()
    if not desafio:
        raise HTTPException(status_code=404, detail="Desafio não encontrado.")

    if desafio.concluido:
        raise HTTPException(status_code=400, detail="Desafio já concluído.")

    hoje = date.today()
    if desafio.ultimo_checkin == hoje:
        raise HTTPException(status_code=400, detail="Você já fez check-in hoje.")

    # Regra simples: incrementa streak em 1 por dia de check-in
    desafio.streak_atual += 1
    desafio.ultimo_checkin = hoje

    # Conclui ao atingir a meta
    if desafio.streak_atual >= desafio.dias_meta:
        desafio.concluido = True
        desafio.data_conclusao = hoje

    db.commit()
    db.refresh(desafio)
    return desafio
