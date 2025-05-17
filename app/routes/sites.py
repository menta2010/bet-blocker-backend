from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud, database

router = APIRouter(prefix="/sites-bloqueados", tags=["sites-bloqueados"])

@router.post("/", response_model=schemas.SiteBloqueadoResponse)
def criar_site(site: schemas.SiteBloqueadoCreate, db: Session = Depends(database.get_db)):
    existing = crud.get_site_by_url(db, site.url)
    if existing:
        raise HTTPException(status_code=400, detail="Site já cadastrado")
    return crud.create_site(db, site)

@router.get("/", response_model=List[schemas.SiteBloqueadoResponse])
def listar_sites(db: Session = Depends(database.get_db)):
    return crud.list_sites(db)

@router.put("/{site_id}", response_model=schemas.SiteBloqueadoResponse)
def atualizar_site(site_id: int, site: schemas.SiteBloqueadoCreate, db: Session = Depends(database.get_db)):
    db_site = crud.get_site_by_id(db, site_id)
    if not db_site:
        raise HTTPException(status_code=404, detail="Site não encontrado")
    db_site.url = site.url
    db_site.tipo = site.tipo
    db.commit()
    db.refresh(db_site)
    return db_site

@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_site(site_id: int, db: Session = Depends(database.get_db)):
    db_site = crud.get_site_by_id(db, site_id)
    if not db_site:
        raise HTTPException(status_code=404, detail="Site não encontrado")
    db.delete(db_site)
    db.commit()
    return None
