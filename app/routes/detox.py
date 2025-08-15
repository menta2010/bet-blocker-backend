import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies.auth import get_current_user
from app.database import get_db
from app.models import DetoxPlano, Usuario
from app.schemas import DetoxPlanoCreate, DetoxPlanoOut

router = APIRouter(prefix="/detox", tags=["Detox"])

@router.post("/", response_model=DetoxPlanoOut, status_code=201)
def criar_plano(
    payload: DetoxPlanoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    db_obj = DetoxPlano(
        usuario_id=usuario.id,
        titulo=payload.titulo,
        objetivos=payload.objetivos,
        atividades_diarias=json.dumps(payload.atividades_diarias, ensure_ascii=False),
        dicas=payload.dicas,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    return DetoxPlanoOut(
        id=db_obj.id,
        titulo=db_obj.titulo,
        objetivos=db_obj.objetivos,
        atividades_diarias=json.loads(db_obj.atividades_diarias or "[]"),
        dicas=db_obj.dicas,
        criado_em=db_obj.criado_em,
        atualizado_em=db_obj.atualizado_em,
    )

@router.get("/", response_model=list[DetoxPlanoOut])
def listar_planos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    itens = (
        db.query(DetoxPlano)
        .filter(DetoxPlano.usuario_id == usuario.id)
        .order_by(DetoxPlano.criado_em.desc())
        .all()
    )
    return [
        DetoxPlanoOut(
            id=i.id,
            titulo=i.titulo,
            objetivos=i.objetivos,
            atividades_diarias=json.loads(i.atividades_diarias or "[]"),
            dicas=i.dicas,
            criado_em=i.criado_em,
            atualizado_em=i.atualizado_em,
        )
        for i in itens
    ]

@router.put("/{plano_id}", response_model=DetoxPlanoOut)
def atualizar_plano(
    plano_id: int,
    payload: DetoxPlanoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    i = (
        db.query(DetoxPlano)
        .filter(DetoxPlano.id == plano_id, DetoxPlano.usuario_id == usuario.id)
        .first()
    )
    if not i:
        raise HTTPException(status_code=404, detail="Plano não encontrado.")

    i.titulo = payload.titulo
    i.objetivos = payload.objetivos
    i.atividades_diarias = json.dumps(payload.atividades_diarias, ensure_ascii=False)
    i.dicas = payload.dicas

    db.commit()
    db.refresh(i)
    return DetoxPlanoOut(
        id=i.id,
        titulo=i.titulo,
        objetivos=i.objetivos,
        atividades_diarias=json.loads(i.atividades_diarias or "[]"),
        dicas=i.dicas,
        criado_em=i.criado_em,
        atualizado_em=i.atualizado_em,
    )

@router.delete("/{plano_id}", status_code=204)
def deletar_plano(
    plano_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    i = (
        db.query(DetoxPlano)
        .filter(DetoxPlano.id == plano_id, DetoxPlano.usuario_id == usuario.id)
        .first()
    )
    if not i:
        raise HTTPException(status_code=404, detail="Plano não encontrado.")
    db.delete(i)
    db.commit()
    return None