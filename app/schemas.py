from pydantic import BaseModel, EmailStr , field_validator
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
        from_attributes = True

# Schemas para TentativaAcesso
class TentativaAcessoBase(BaseModel):
    site_id: int
    usuario_id: int

class TentativaAcessoCreate(TentativaAcessoBase):
    pass

class TentativaAcessoResponse(TentativaAcessoBase):
    id: int
    data_hora: datetime

    class Config:
        from_attributes = True

# Registro
class UserCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str

    @field_validator("senha")
    @classmethod
    def senha_forte(cls, v: str):
        if len(v) < 8:
            raise ValueError("A senha deve ter pelo menos 8 caracteres.")
        if v.isdigit() or v.isalpha():
            raise ValueError("Use letras e números para uma senha mais segura.")
        return v
    
# Retorno do usuário
class UserOut(BaseModel):
    id: int
    nome: str
    email: EmailStr

    class Config:
        from_attributes = True

# Login
class LoginSchema(BaseModel):
    email: EmailStr
    senha: str

# Token JWT
class Token(BaseModel):
    access_token: str
    token_type: str


class TrocaSenha(BaseModel):
    senha_atual: str
    nova_senha: str

class AconselhamentoRequest(BaseModel):
    mensagem: str

class AconselhamentoResponse(BaseModel):
    resposta: str

class AconselhamentoOut(BaseModel):
    id: int
    mensagem: str
    resposta: str
    data: datetime

class DiarioCreate(BaseModel):
    texto: str

    @field_validator("texto")
    @classmethod
    def limitar_tamanho(cls, v: str):
        if len(v) > 3000:
            raise ValueError("Texto muito longo (máx 3000 caracteres).")
        return v

class DiarioOut(BaseModel):
    id: int
    texto: str
    sentimento: str
    resposta: str
    data: datetime

class ContatoEmergenciaCreate(BaseModel):
    email: EmailStr
    nome: str | None = None

class ContatoEmergenciaOut(BaseModel):
    id: int
    email: EmailStr
    nome: str | None = None
    criado_em: datetime
    class Config:
        from_attributes = True

class EmergenciaResponse(BaseModel):
    mensagem: str
    enviado_para: list[EmailStr]
    data_hora: datetime

    class Config:
        from_attributes = True
