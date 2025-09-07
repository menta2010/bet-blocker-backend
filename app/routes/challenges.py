from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone  # 🛠️ usar timezone-aware
from app.database import get_db
from app.dependencies.auth import get_current_user
from app import schemas, models, crud

router = APIRouter(prefix="/challenges", tags=["Challenges"])

# --- Catálogo ---

@router.get("/catalog", response_model=list[schemas.ChallengeTemplateOut])
def list_catalog(db: Session = Depends(get_db)):
    # antes: crud.list_active_templates(...)
    return crud.list_catalog(db)

@router.post("/catalog", response_model=schemas.ChallengeTemplateOut)
def create_catalog_item(
    payload: schemas.ChallengeTemplateCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    # mantém como estava na sua versão
    return crud.create_template(db, payload)


# --- Minhas instâncias ---

@router.get("/me", response_model=list[schemas.UserChallengeOut])
def my_challenges(db: Session = Depends(get_db), user = Depends(get_current_user)):
    # antes: crud.list_user_challenges(...)
    return crud.list_my_challenges(db, user.id)

@router.post("/", response_model=schemas.UserChallengeOut)
def create_user_challenge(
    payload: schemas.UserChallengeCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    # valida disponibilidade do template (se houver)
    if payload.template_id:
        tpl = db.query(models.ChallengeTemplate).get(payload.template_id)
        if not tpl:
            raise HTTPException(status_code=404, detail="Template não encontrado")

        # 🛠️ agora timezone-aware para bater com DateTime(timezone=True)
        now = datetime.now(timezone.utc)

        if (tpl.starts_at and tpl.starts_at > now) or (tpl.expires_at and tpl.expires_at < now):
            raise HTTPException(status_code=400, detail="Template indisponível/expirado")

    uc = crud.create_user_challenge(db, user.id, payload)
    return uc


# --- Ciclo de vida: start/abandon/complete ---

@router.post("/{challenge_id}/start", response_model=schemas.UserChallengeOut)
def start_challenge(
    challenge_id: int,
    payload: schemas.UserChallengeStart | None = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    # agora grava baselines e muda para "active"
    return crud.start_user_challenge(db, user.id, challenge_id, payload)

@router.patch("/{challenge_id}/abandon", response_model=schemas.UserChallengeOut)
def abandon_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    return crud.abandon_user_challenge(db, user.id, challenge_id)

@router.patch("/{challenge_id}/complete", response_model=schemas.UserChallengeOut)
def complete_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    return crud.complete_user_challenge(db, user.id, challenge_id)
