from pydantic import BaseModel , EmailStr
from datetime import datetime

# Schemas para SiteBloqueado
class SiteBloqueadoBase(BaseModel):
    url: str
    tipo: str = "apostas"

class SiteBloqueadoCreate(SiteBloqueadoBase):
    pass

class SiteBloqueadoResponse(SiteBloqueadoBase):
    id: int
    data_cadastro: datetime

    class Config:
        orm_mode = True

# Schemas para TentativaAcesso
class TentativaAcessoBase(BaseModel):
    url: str
    usuario_id: str

class TentativaAcessoCreate(TentativaAcessoBase):
    pass

class TentativaAcessoResponse(TentativaAcessoBase):
    id: int
    data_hora: datetime

    class Config:
        orm_mode = True

# Registro
class UserCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str

# Retorno do usuário
class UserOut(BaseModel):
    id: int
    nome: str
    email: EmailStr

    class Config:
        from_attributes = True  # substitui orm_mode em Pydantic v2

# Login
class LoginSchema(BaseModel):
    email: EmailStr
    senha: str

# Token JWT
class Token(BaseModel):
    access_token: str
    token_type: str
