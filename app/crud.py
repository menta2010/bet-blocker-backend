from sqlalchemy.orm import Session
from . import models, schemas
from app.core.security import hash_password

# CRUD para SiteBloqueado
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