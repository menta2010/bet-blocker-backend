from sqlalchemy.orm import Session
from . import models, schemas
from app.core.security import hash_password
from datetime import datetime , timedelta
import random

# CRUD para SiteBloqueado

def _generate_6digit_code() -> str:
    return f"{random.randint(0, 999999):06d}"

def get_site_by_url(db: Session, url: str, usuario_id: int):
    return (
        db.query(models.SiteBloqueado)
        .filter(models.SiteBloqueado.url == url, models.SiteBloqueado.usuario_id == usuario_id)
        .first()
    )

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
    expires_at = datetime.utcnow() + timedelta(minutes=minutes_valid)

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
            models.EmailVerificationCode.expires_at > datetime.utcnow(),
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
            models.EmailVerificationCode.expires_at > datetime.utcnow(),
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
    expires_at = datetime.utcnow() + timedelta(minutes=minutes_valid)

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
            models.PasswordResetCode.expires_at > datetime.utcnow(),
        )
        .order_by(models.PasswordResetCode.id.desc())
        .first()
    )
    if not rec:
        return None

    rec.used = True
    db.commit()
    return user

# app/crud.py
from sqlalchemy.orm import Session
from app import models, schemas

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