from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud, database
from app.models import Usuario
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/sites-bloqueados", tags=["sites-bloqueados"])

@router.post("/", response_model=schemas.SiteBloqueadoResponse)
def criar_site(
    site: schemas.SiteBloqueadoCreate,
    db: Session = Depends(database.get_db),
    usuario: Usuario = Depends(get_current_user)
):
    existing = crud.get_site_by_url(db, site.url, usuario.id)
    if existing:
        raise HTTPException(status_code=400, detail="Site já cadastrado")
    return crud.create_site(db, site, usuario.id)

@router.get("/", response_model=List[schemas.SiteBloqueadoResponse])
def listar_sites(
    db: Session = Depends(database.get_db),
    usuario: Usuario = Depends(get_current_user)
):
    return crud.list_sites(db, usuario.id)

@router.put("/{site_id}", response_model=schemas.SiteBloqueadoResponse)
def atualizar_site(
    site_id: int,
    site: schemas.SiteBloqueadoCreate,
    db: Session = Depends(database.get_db),
    usuario: Usuario = Depends(get_current_user)
):
    db_site = crud.get_site_by_id(db, site_id)
    if not db_site or db_site.usuario_id != usuario.id:
        raise HTTPException(status_code=404, detail="Site não encontrado ou acesso negado")
    db_site.url = site.url
    db_site.tipo = site.tipo
    db.commit()
    db.refresh(db_site)
    return db_site

@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_site(
    site_id: int,
    db: Session = Depends(database.get_db),
    usuario: Usuario = Depends(get_current_user)
):
    db_site = crud.get_site_by_id(db, site_id)
    if not db_site or db_site.usuario_id != usuario.id:
        raise HTTPException(status_code=404, detail="Site não encontrado ou acesso negado")
    db.delete(db_site)
    db.commit()
    return None
