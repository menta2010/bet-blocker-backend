from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.models import Usuario
from app.schemas import EmergenciaResponse
from app.dependencies.auth import get_current_user
from app.database import get_db
from app.services.emergencia_service import lidar_emergencia

router = APIRouter(prefix="/emergencia", tags=["Emergência"])

@router.post("/", response_model=EmergenciaResponse)
async def acionar_emergencia(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    try:
        return await lidar_emergencia(db, usuario, background_tasks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao acionar emergência: {str(e)}")
