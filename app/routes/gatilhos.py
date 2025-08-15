from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.dependencies.auth import get_current_user
from app.database import get_db
from app.models import Gatilho, Usuario
from app.schemas import GatilhoCreate, GatilhoUpdate, GatilhoOut

router = APIRouter(prefix="/gatilhos", tags=["Gatilhos"])

def _ints_to_csv(val: list[int]) -> str:
    return ",".join(str(v) for v in val) if val else ""

def _csv_to_ints(val: str) -> list[int]:
    if not val:
        return []
    return [int(x) for x in val.split(",") if x != ""]

@router.post("/", response_model=GatilhoOut, status_code=201)
def criar_gatilho(
    payload: GatilhoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    db_obj = Gatilho(
        usuario_id=usuario.id,
        nome=payload.nome,
        dias_da_semana=_ints_to_csv(payload.dias_da_semana),
        hora_inicio=payload.hora_inicio,
        hora_fim=payload.hora_fim,
        ativo=payload.ativo,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return GatilhoOut(
        id=db_obj.id,
        nome=db_obj.nome,
        dias_da_semana=_csv_to_ints(db_obj.dias_da_semana),
        hora_inicio=db_obj.hora_inicio,
        hora_fim=db_obj.hora_fim,
        ativo=db_obj.ativo,
        criado_em=db_obj.criado_em,
    )

@router.get("/", response_model=list[GatilhoOut])
def listar_gatilhos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    itens = (
        db.query(Gatilho)
        .filter(Gatilho.usuario_id == usuario.id)
        .order_by(Gatilho.criado_em.desc())
        .all()
    )
    return [
        GatilhoOut(
            id=i.id,
            nome=i.nome,
            dias_da_semana=_csv_to_ints(i.dias_da_semana),
            hora_inicio=i.hora_inicio,
            hora_fim=i.hora_fim,
            ativo=i.ativo,
            criado_em=i.criado_em,
        )
        for i in itens
    ]

@router.patch("/{gatilho_id}", response_model=GatilhoOut)
def atualizar_gatilho(
    gatilho_id: int,
    payload: GatilhoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    g = (
        db.query(Gatilho)
        .filter(Gatilho.id == gatilho_id, Gatilho.usuario_id == usuario.id)
        .first()
    )
    if not g:
        raise HTTPException(status_code=404, detail="Gatilho não encontrado.")

    if payload.nome is not None:
        g.nome = payload.nome
    if payload.dias_da_semana is not None:
        g.dias_da_semana = _ints_to_csv(payload.dias_da_semana)
    if payload.hora_inicio is not None:
        g.hora_inicio = payload.hora_inicio
    if payload.hora_fim is not None:
        g.hora_fim = payload.hora_fim
    if payload.ativo is not None:
        g.ativo = payload.ativo

    db.commit()
    db.refresh(g)
    return GatilhoOut(
        id=g.id,
        nome=g.nome,
        dias_da_semana=_csv_to_ints(g.dias_da_semana),
        hora_inicio=g.hora_inicio,
        hora_fim=g.hora_fim,
        ativo=g.ativo,
        criado_em=g.criado_em,
    )

@router.delete("/{gatilho_id}", status_code=204)
def deletar_gatilho(
    gatilho_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    g = (
        db.query(Gatilho)
        .filter(Gatilho.id == gatilho_id, Gatilho.usuario_id == usuario.id)
        .first()
    )
    if not g:
        raise HTTPException(status_code=404, detail="Gatilho não encontrado.")
    db.delete(g)
    db.commit()
    return None

@router.get("/agora/ativos", response_model=list[GatilhoOut])
def gatilhos_ativos_agora(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Retorna gatilhos ativos no dia da semana/hora atuais."""
    agora = datetime.now()
    dia_semana = (agora.weekday())  # 0=Seg ... 6=Dom
    hora_atual = agora.time()

    itens = (
        db.query(Gatilho)
        .filter(Gatilho.usuario_id == usuario.id, Gatilho.ativo == True)
        .all()
    )

    ativos = []
    for i in itens:
        dias = _csv_to_ints(i.dias_da_semana)
        if dias and (dia_semana not in dias):
            continue
        if i.hora_inicio <= hora_atual <= i.hora_fim:
            ativos.append(
                GatilhoOut(
                    id=i.id,
                    nome=i.nome,
                    dias_da_semana=dias,
                    hora_inicio=i.hora_inicio,
                    hora_fim=i.hora_fim,
                    ativo=i.ativo,
                    criado_em=i.criado_em,
                )
            )
    return ativos
