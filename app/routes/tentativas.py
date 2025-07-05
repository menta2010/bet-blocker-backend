from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app import schemas, crud, database
from app.services.email_service import send_email_alert

router = APIRouter(prefix="/tentativas", tags=["tentativas"])

@router.post("/", response_model=schemas.TentativaAcessoResponse)
async def criar_tentativa(tentativa: schemas.TentativaAcessoCreate, background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    db_tentativa = crud.create_tentativa(db, tentativa)
    background_tasks.add_task(send_email_alert, db, db_tentativa) 
    return db_tentativa
