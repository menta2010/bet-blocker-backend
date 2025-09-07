from sqlalchemy.orm import Session
from . import models, schemas
from app.core.security import hash_password
from datetime import datetime , timedelta , timezone, date
import random
from fastapi import HTTPException

# CRUD para SiteBloqueado

def _generate_6digit_code() -> str:
    return f"{random.randint(0, 999999):06d}"

def get_site_by_url(db: Session, url: str, usuario_id: int):
    return (
        db.query(models.SiteBloqueado)
        .filter(models.SiteBloqueado.url == url, models.SiteBloqueado.usuario_id == usuario_id)
        .first()
    )

def today_utc() -> date:
    """Retorna a data de hoje em UTC."""
    return datetime.now(timezone.utc).date()

def _days_since(dt: datetime | None) -> int:
    if not dt:
        return 0
    # usar hoje em UTC para diferenças
    return max(0, (today_utc() - dt.date()).days)

def create_site(db: Session, site: schemas.SiteBloqueadoCreate, usuario_id: int):
    db_site = models.SiteBloqueado(
        url=site.url,
        tipo=site.tipo,
        usuario_id=usuario_id
    )
    db.add(db_site)
    db.commit()
    db.refresh(db_site)
    return db_site

def list_sites(db: Session, usuario_id: int):
    return db.query(models.SiteBloqueado).filter(models.SiteBloqueado.usuario_id == usuario_id).all()

def get_site_by_id(db: Session, site_id: int):
    return db.query(models.SiteBloqueado).filter(models.SiteBloqueado.id == site_id).first()

# CRUD para TentativaAcesso
def create_tentativa(db: Session, tentativa: schemas.TentativaAcessoCreate):
    db_tentativa = models.TentativaAcesso(
        site_id=tentativa.site_id,
        usuario_id=tentativa.usuario_id
    )
    db.add(db_tentativa)
    db.commit()
    db.refresh(db_tentativa)
    return db_tentativa

# CRUD para Usuario
def get_user_by_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    email_norm = user.email.lower().strip()
    hashed_pw = hash_password(user.senha)
    db_user = models.Usuario(
        nome=user.nome,
        email=email_norm,
        senha=hashed_pw,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def add_contato_emergencia(db: Session, usuario_id: int, email: str):
    contato = models.EmergenciaContato(usuario_id=usuario_id, email=email)
    db.add(contato)
    db.commit()
    db.refresh(contato)
    return contato

def list_contatos_emergencia(db: Session, usuario_id: int):
    return db.query(models.EmergenciaContato)\
             .filter(models.EmergenciaContato.usuario_id == usuario_id)\
             .all()

def delete_contato_emergencia(db: Session, usuario_id: int, contato_id: int):
    contato = db.query(models.EmergenciaContato)\
                .filter(models.EmergenciaContato.id == contato_id,
                        models.EmergenciaContato.usuario_id == usuario_id)\
                .first()
    if contato:
        db.delete(contato)
        db.commit()
    return contato

def create_email_verification_code(db: Session, user_id: int, minutes_valid: int = 15) -> models.EmailVerificationCode:
    code = _generate_6digit_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=minutes_valid)

    # invalida códigos anteriores não usados (opcional)
    db.query(models.EmailVerificationCode).filter(
        models.EmailVerificationCode.user_id == user_id,
        models.EmailVerificationCode.used == False,
    ).update({models.EmailVerificationCode.used: True})

    record = models.EmailVerificationCode(
        user_id=user_id,
        code=code,
        expires_at=expires_at,
        used=False,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def validate_email_verification_code(db: Session, email: str, code: str) -> models.Usuario | None:
    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not user:
        return None

    rec = (
        db.query(models.EmailVerificationCode)
        .filter(
            models.EmailVerificationCode.user_id == user.id,
            models.EmailVerificationCode.code == code,
            models.EmailVerificationCode.used == False,
            models.EmailVerificationCode.expires_at > datetime.now(timezone.utc),
        )
        .order_by(models.EmailVerificationCode.id.desc())
        .first()
    )
    if not rec:
        return None

    # marca como usado
    rec.used = True
    db.commit()
    return user

def verify_email_with_code(db: Session, user: models.Usuario, code: str) -> bool:
    rec = (
        db.query(models.EmailVerificationCode)
        .filter(
            models.EmailVerificationCode.user_id == user.id,
            models.EmailVerificationCode.code == code,
            models.EmailVerificationCode.used == False,
            models.EmailVerificationCode.expires_at >datetime.now(timezone.utc),
        )
        .first()
    )
    if not rec:
        return False

    # marca verificado + marca código como usado
    user.email_verificado = True
    rec.used = True

    # garante que ambos estão anexados e persiste
    db.add_all([user, rec])
    db.commit()
    db.refresh(user)
    return True
# ====== PASSWORD RESET ======
def create_password_reset_code(db: Session, user_id: int, minutes_valid: int = 15) -> models.PasswordResetCode:
    code = _generate_6digit_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=minutes_valid)

    # invalida códigos anteriores
    db.query(models.PasswordResetCode).filter(
        models.PasswordResetCode.user_id == user_id,
        models.PasswordResetCode.used == False,
    ).update({models.PasswordResetCode.used: True})

    record = models.PasswordResetCode(
        user_id=user_id,
        code=code,
        expires_at=expires_at,
        used=False,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def validate_password_reset_code(db: Session, email: str, code: str) -> models.Usuario | None:
    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not user:
        return None

    rec = (
        db.query(models.PasswordResetCode)
        .filter(
            models.PasswordResetCode.user_id == user.id,
            models.PasswordResetCode.code == code,
            models.PasswordResetCode.used == False,
            models.PasswordResetCode.expires_at > datetime.now(timezone.utc),
        )
        .order_by(models.PasswordResetCode.id.desc())
        .first()
    )
    if not rec:
        return None

    rec.used = True
    db.commit()
    return user

def get_baseline_by_user(db: Session, usuario_id: int) -> models.UsuarioBaseline | None:
    return db.query(models.UsuarioBaseline).filter(models.UsuarioBaseline.usuario_id == usuario_id).first()

def create_baseline(db: Session, usuario_id: int, data: schemas.BaselineCreate) -> models.UsuarioBaseline:
    baseline = models.UsuarioBaseline(
        usuario_id=usuario_id,
        tempo_diario_minutos=data.tempo_diario_minutos,
        dias_por_semana=data.dias_por_semana,
        gasto_medio_dia=data.gasto_medio_dia,
        moeda=data.moeda or "BRL",
    )
    db.add(baseline)
    db.commit()
    db.refresh(baseline)
    return baseline

def update_baseline(db: Session, baseline: models.UsuarioBaseline, data: schemas.BaselineUpdate) -> models.UsuarioBaseline:
    for field in ("tempo_diario_minutos", "dias_por_semana", "gasto_medio_dia", "moeda"):
        val = getattr(data, field, None)
        if val is not None:
            setattr(baseline, field, val)
    db.commit()
    db.refresh(baseline)
    return baseline


# ----------------- Streak / Check-in -----------------

def get_current_streak_days(usuario: models.Usuario) -> int:
    """
    Dias consecutivos de streak, contando de streak_started_at ATÉ o último dia com check-in (inclusivo).
    Ex.: start=2025-09-01, last=2025-09-02 -> 2 dias.
    """
    if not usuario.streak_started_at or not usuario.last_checkin_date:
        return 0

    start = usuario.streak_started_at.date()  # já é timezone-aware na criação
    last  = usuario.last_checkin_date         # Date (não datetime)

    # inclusivo: +1
    days = (last - start).days + 1
    return max(0, days)

def start_streak(db: Session, usuario: models.Usuario) -> models.Usuario:
    if not usuario.streak_started_at:
        usuario.streak_started_at = datetime.now(tz=timezone.utc)
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
    return usuario

def reset_streak(db: Session, usuario: models.Usuario) -> models.Usuario:
    current = get_current_streak_days(usuario)
    if current > 0:
        usuario.last_streak_days = current
        if current > (usuario.best_streak_days or 0):
            usuario.best_streak_days = current
    usuario.streak_started_at = None
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario

def has_checkin_today(usuario: models.Usuario) -> bool:
    return bool(usuario.last_checkin_date == today_utc())

def do_daily_checkin(db: Session, usuario: models.Usuario) -> int:
    """
    Registra o check-in do dia.
    - Se ficou 2+ dias sem check-in, fecha a streak anterior (atualiza best/last) e reinicia.
    - Atualiza last_checkin_date e retorna a streak atual.
    """
    today = today_utc()

    # já fez hoje → não muda nada
    if usuario.last_checkin_date == today:
        return get_current_streak_days(usuario)

    # primeira vez
    if not usuario.streak_started_at:
        usuario.streak_started_at = datetime.now(tz=timezone.utc)
    else:
        # dias desde o último check-in
        if usuario.last_checkin_date and (today - usuario.last_checkin_date).days > 1:
            # fechamos a streak anterior
            current = get_current_streak_days(usuario)
            if current > 0:
                usuario.last_streak_days = current
                if current > (usuario.best_streak_days or 0):
                    usuario.best_streak_days = current
            # reinicia a streak a partir de hoje
            usuario.streak_started_at = datetime.now(tz=timezone.utc)

    usuario.last_checkin_date = today

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return get_current_streak_days(usuario)

def list_active_templates(db: Session, now: datetime | None = None):
    q = db.query(models.ChallengeTemplate)
    if now:
        q = q.filter(
            (models.ChallengeTemplate.starts_at == None) | (models.ChallengeTemplate.starts_at <= now)
        ).filter(
            (models.ChallengeTemplate.expires_at == None) | (models.ChallengeTemplate.expires_at >= now)
        )
    return q.order_by(models.ChallengeTemplate.created_at.desc()).all()


def create_template(db: Session, payload: schemas.ChallengeTemplateCreate):
    t = models.ChallengeTemplate(**payload.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


# --- User challenges ---

def list_my_challenges(db: Session, user_id: int):
    return (
        db.query(models.UserChallenge)
        .filter(models.UserChallenge.user_id == user_id)
        .order_by(models.UserChallenge.created_at.desc())
        .all()
    )


# -------- Criação --------
def create_user_challenge(db: Session, user_id: int, payload: schemas.UserChallengeCreate):
    # via template
    if payload.template_id:
        tpl = db.query(models.ChallengeTemplate).get(payload.template_id)
        if not tpl:
            raise HTTPException(status_code=404, detail="Template inexistente")

        uc = models.UserChallenge(
            user_id=user_id,
            template_id=tpl.id,
            title=tpl.title,
            description=tpl.description,
            target_type=tpl.target_type,
            target_value=tpl.target_value or 1,
            deadline_days=None,
            status="draft",
        )
    else:
        # custom obrigatório
        if not (payload.title and payload.target_type and payload.target_value is not None):
            raise HTTPException(status_code=400, detail="title, target_type e target_value são obrigatórios")
        uc = models.UserChallenge(
            user_id=user_id,
            title=payload.title,
            description=payload.description,
            target_type=payload.target_type,
            target_value=payload.target_value,
            deadline_days=payload.deadline_days,
            status="draft",
        )

    db.add(uc)
    db.commit()
    db.refresh(uc)
    return uc


# -------- Start (grava baselines) --------
def start_user_challenge(db: Session, user_id: int, challenge_id: int, payload: schemas.UserChallengeStart | None):
    uc = (
        db.query(models.UserChallenge)
        .filter(models.UserChallenge.id == challenge_id, models.UserChallenge.user_id == user_id)
        .first()
    )
    if not uc:
        raise HTTPException(status_code=404, detail="Challenge não encontrado")

    if uc.status != "draft":
        raise HTTPException(status_code=400, detail="Só é possível iniciar desafios em rascunho")

    if payload:
        uc.baseline_money = payload.baseline_money
        uc.baseline_time_min = payload.baseline_time_min
        uc.baseline_streak_days = payload.baseline_streak_days

    uc.status = "active"
    uc.started_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(uc)
    return uc


# -------- Completar / Abandonar --------
def complete_user_challenge(db: Session, user_id: int, challenge_id: int):
    uc = (
        db.query(models.UserChallenge)
        .filter(models.UserChallenge.id == challenge_id, models.UserChallenge.user_id == user_id)
        .first()
    )
    if not uc:
        raise HTTPException(status_code=404, detail="Challenge não encontrado")
    uc.status = "completed"
    uc.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(uc)
    return uc


def abandon_user_challenge(db: Session, user_id: int, challenge_id: int):
    uc = (
        db.query(models.UserChallenge)
        .filter(models.UserChallenge.id == challenge_id, models.UserChallenge.user_id == user_id)
        .first()
    )
    if not uc:
        raise HTTPException(status_code=404, detail="Challenge não encontrado")
    uc.status = "abandoned"
    uc.abandoned_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(uc)
    return uc

def list_catalog(db: Session):
    return list_active_templates(db, datetime.now(timezone.utc))