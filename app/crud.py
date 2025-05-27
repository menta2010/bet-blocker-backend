from sqlalchemy.orm import Session
from . import models, schemas
from app.core.security import hash_password

# CRUD para SiteBloqueado
def get_site_by_url(db: Session, url: str):
    return db.query(models.SiteBloqueado).filter(models.SiteBloqueado.url == url).first()

def create_site(db: Session, site: schemas.SiteBloqueadoCreate):
    db_site = models.SiteBloqueado(url=site.url, tipo=site.tipo)
    db.add(db_site)
    db.commit()
    db.refresh(db_site)
    return db_site

def list_sites(db: Session):
    return db.query(models.SiteBloqueado).all()

# CRUD para TentativaAcesso
def create_tentativa(db: Session, tentativa: schemas.TentativaAcessoCreate):
    db_tentativa = models.TentativaAcesso(
        url=tentativa.url,
        usuario_id=tentativa.usuario_id
    )
    db.add(db_tentativa)
    db.commit()
    db.refresh(db_tentativa)
    return db_tentativa

def get_site_by_id(db: Session, site_id: int):
    return db.query(models.SiteBloqueado).filter(models.SiteBloqueado.id == site_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_pw = hash_password(user.senha)
    db_user = models.User(
        nome=user.nome,
        email=user.email,
        senha=hashed_pw
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

