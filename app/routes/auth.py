from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app import schemas, crud, database
from app.core.security import verify_password, create_access_token, get_password_hash
from app.schemas import UserOut
from app.dependencies.auth import get_current_user
from app.database import get_db
from app.services.email_service import send_email_verification_code, send_password_reset_code
from app.schemas import VerifyEmailCode



router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já registrado")
    return crud.create_user(db, user)


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.senha):
        raise HTTPException(status_code=400, detail="Credenciais inválidas")
    
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def read_users_me(current_user: UserOut = Depends(get_current_user)):
    return current_user

@router.post("/request-email-code", response_model=schemas.VerifyEmailResponse)
async def request_email_code(payload: schemas.RequestEmailCode, db: Session = Depends(database.get_db)):
    user = crud.get_user_by_email(db, payload.email)
    if not user:
        # por segurança, responda 200 mesmo se não existir
        return schemas.VerifyEmailResponse(mensagem="Se existir cadastro, um código foi enviado.")
    record = crud.create_email_verification_code(db, user_id=user.id, minutes_valid=15)
    await send_email_verification_code(user.email, user.nome, record.code, 15)
    return schemas.VerifyEmailResponse(mensagem="Código enviado para o seu e-mail.")

# 5.2 Verificar e-mail com código
@router.post("/verify-email", response_model=schemas.VerifyEmailResponse)
def verify_email(payload: VerifyEmailCode, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, payload.email)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    ok = crud.verify_email_with_code(db, user, payload.code)
    if not ok:
        raise HTTPException(status_code=400, detail="Código inválido ou expirado")

    return {"mensagem": "E-mail verificado com sucesso."}

# 5.3 Solicitar código de redefinição de senha
@router.post("/request-password-reset-code", response_model=schemas.ResetPasswordResponse)
async def request_password_reset_code(payload: schemas.RequestPasswordResetCode, db: Session = Depends(database.get_db)):
    user = crud.get_user_by_email(db, payload.email)
    # retornamos 200 mesmo se não existir
    if not user:
        return schemas.ResetPasswordResponse(mensagem="Se existir cadastro, um código foi enviado.")
    record = crud.create_password_reset_code(db, user_id=user.id, minutes_valid=15)
    await send_password_reset_code(user.email, user.nome, record.code, 15)
    return schemas.ResetPasswordResponse(mensagem="Código de redefinição enviado para o e-mail.")

# 5.4 Redefinir senha com código
@router.post("/reset-password", response_model=schemas.ResetPasswordResponse)
def reset_password(payload: schemas.ResetPasswordWithCode, db: Session = Depends(database.get_db)):
    user = crud.validate_password_reset_code(db, email=payload.email, code=payload.code)
    if not user:
        raise HTTPException(status_code=400, detail="Código inválido ou expirado.")
    user.senha = get_password_hash(payload.nova_senha)
    db.commit()
    return schemas.ResetPasswordResponse(mensagem="Senha redefinida com sucesso.")