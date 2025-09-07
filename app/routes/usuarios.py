from fastapi import APIRouter, Depends, HTTPException, status , BackgroundTasks,Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.models import Usuario , EmergenciaContato
from app.services.email_service import send_email_notificacao 
from app.schemas import TrocaSenha, UserOut, ContatoEmergenciaCreate, ContatoEmergenciaOut, BaselineOut,BaselineCreate,BaselineUpdate,MetricsOut,CheckinTodayOut,HistoryOut, HistoryPoint
from app.core.security import verify_password, get_password_hash
from typing import List
from app import crud
from datetime import datetime,date,timedelta,timezone

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


class TrocaEmailRequest(BaseModel):
    novo_email: EmailStr


class StreakOut(BaseModel):
    currentDays: int
    bestDays: int
    since: datetime | None

@router.patch("/{usuario_id}/email", status_code=200)
async def trocar_email(
    usuario_id: int,
    payload: TrocaEmailRequest,
    background_tasks: BackgroundTasks,
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
        background_tasks.add_task(
            send_email_notificacao,
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
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),

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
        background_tasks.add_task(
        send_email_notificacao,
            email =usuario.email,
            nome=usuario.nome,
            mensagem="Sua senha foi alterada com sucesso. Se não foi você, entre em contato com o suporte."
        )
    except Exception as e:
        print("Erro ao enviar notificação de alteração de senha:", str(e))

    return usuario

@router.post("/{usuario_id}/contatos", response_model=ContatoEmergenciaOut, status_code=201)
def adicionar_contato_emergencia(
    usuario_id: int,
    payload: ContatoEmergenciaCreate,
    db: Session = Depends(get_db),
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # evita duplicados por e-mail
    existe = (
        db.query(EmergenciaContato)
        .filter(EmergenciaContato.usuario_id == usuario_id, EmergenciaContato.email == payload.email)
        .first()
    )
    if existe:
        raise HTTPException(status_code=400, detail="Contato já cadastrado para esse usuário")

    contato = EmergenciaContato(usuario_id=usuario_id, email=payload.email, nome=payload.nome)
    db.add(contato)
    db.commit()
    db.refresh(contato)
    return contato

@router.get("/{usuario_id}/contatos", response_model=List[ContatoEmergenciaOut])
def listar_contatos_emergencia(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario.contatos_emergencia

@router.delete("/{usuario_id}/contatos/{contato_id}", status_code=204)
def remover_contato_emergencia(usuario_id: int, contato_id: int, db: Session = Depends(get_db)):
    contato = (
        db.query(EmergenciaContato)
        .filter(EmergenciaContato.id == contato_id, EmergenciaContato.usuario_id == usuario_id)
        .first()
    )
    if not contato:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    db.delete(contato)
    db.commit()
    return None


@router.get("/{usuario_id}/baseline", response_model= BaselineOut)
def obter_baseline(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    baseline = crud.get_baseline_by_user(db, usuario_id)
    if not baseline:
        raise HTTPException(status_code=404, detail="Baseline não encontrado")
    return baseline

@router.post("/{usuario_id}/baseline", response_model=BaselineOut, status_code=201)
def criar_baseline(usuario_id: int, payload: BaselineCreate, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    existente = crud.get_baseline_by_user(db, usuario_id)
    if existente:
        raise HTTPException(status_code=400, detail="Baseline já cadastrado para este usuário")

    return crud.create_baseline(db, usuario_id, payload)

@router.patch("/{usuario_id}/baseline", response_model=BaselineOut)
def atualizar_baseline(usuario_id: int, payload: BaselineUpdate, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    baseline = crud.get_baseline_by_user(db, usuario_id)
    if not baseline:
        # opcional: criar caso não exista
        baseline = crud.create_baseline(db, usuario_id, BaselineCreate(**payload.dict()))
        return baseline

    return crud.update_baseline(db, baseline, payload)


@router.get("/{usuario_id}/metrics", response_model=MetricsOut)
def get_user_metrics(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    baseline = crud.get_baseline_by_user(db, usuario_id)
    if not baseline:
        raise HTTPException(status_code=404, detail="Baseline não encontrado")

    streak_days = crud.get_current_streak_days(usuario)
    avoided_bets = round((baseline.dias_por_semana or 0) * (streak_days / 7) * 2)
    money_saved = round((baseline.gasto_medio_dia or 0.0) * streak_days, 2)
    time_saved_min = int((baseline.tempo_diario_minutos or 0) * streak_days)

    return MetricsOut(
        streakDays=streak_days,
        avoidedBets=avoided_bets,
        moneySaved=money_saved,
        timeSavedMin=time_saved_min,
    )

# -------- streak / check-in --------

@router.get("/{usuario_id}/streak", response_model=StreakOut)
def get_streak(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(404, "Usuário não encontrado")
    return StreakOut(
        currentDays=crud.get_current_streak_days(usuario),
        bestDays=usuario.best_streak_days or 0,
        since=usuario.streak_started_at,
    )

@router.post("/{usuario_id}/streak/start", response_model=StreakOut)
def start_streak_route(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(404, "Usuário não encontrado")
    usuario = crud.start_streak(db, usuario)
    return StreakOut(
        currentDays=crud.get_current_streak_days(usuario),
        bestDays=usuario.best_streak_days or 0,
        since=usuario.streak_started_at,
    )

@router.post("/{usuario_id}/streak/reset", response_model=StreakOut)
def reset_streak_route(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(404, "Usuário não encontrado")
    usuario = crud.reset_streak(db, usuario)
    return StreakOut(
        currentDays=crud.get_current_streak_days(usuario),
        bestDays=usuario.best_streak_days or 0,
        since=usuario.streak_started_at,
    )

@router.get("/{usuario_id}/checkin/today", response_model=CheckinTodayOut)
def get_checkin_today(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    done = crud.has_checkin_today(usuario)
    streak = crud.get_current_streak_days(usuario)
    return CheckinTodayOut(done=done, checked_at=usuario.last_checkin_date, streakDays=streak)

@router.post("/{usuario_id}/checkin", response_model=CheckinTodayOut, status_code=201)
def do_checkin(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    streak = crud.do_daily_checkin(db, usuario)
    return CheckinTodayOut(done=True, checked_at=usuario.last_checkin_date, streakDays=streak)



@router.get("/{usuario_id}/history", response_model=HistoryOut)
def get_history(usuario_id: int, days: int = Query(7, ge=1, le=90), db: Session = Depends(get_db)):
    usuario: Usuario | None = db.query(Usuario).filter_by(id=usuario_id).first()
    if not usuario:
        raise HTTPException(404, "Usuário não encontrado")

    baseline = crud.get_baseline_by_user(db, usuario_id)
    if not baseline:
        # sem baseline não faz sentido calcular métricas
        return HistoryOut(points=[])

    # streak atual (em dias) e heurística simples:
    streak_days = crud.get_current_streak_days(usuario)

    last = usuario.last_checkin_date or crud.today_utc()
    # se tiver streak>0, o início é "last - (streak_days-1)"
    streak_start = last - timedelta(days=max(0, streak_days - 1))

    start = crud.today_utc() - timedelta(days=days - 1)
    points: list[HistoryPoint] = []

    for i in range(days):
        d = start + timedelta(days=i)
        active = (streak_days > 0) and (streak_start <= d <= last)

        avoided = int((baseline.dias_por_semana or 0) / 7) if active else 0
        money  = float(baseline.gasto_medio_dia or 0.0) if active else 0.0
        time_m = int(baseline.tempo_diario_minutos or 0) if active else 0

        points.append(HistoryPoint(
            date=d,
            avoidedBets=avoided,
            moneySaved=round(money, 2),
            timeSavedMin=time_m
        ))

    return HistoryOut(points=points)