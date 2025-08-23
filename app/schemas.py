from pydantic import BaseModel, EmailStr, field_validator, constr, Field, conint,condecimal
from datetime import  date, time,datetime
from typing import Optional, List

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

# --- Verificação de e-mail por código ---
class RequestEmailCode(BaseModel):
    email: EmailStr

class VerifyEmailCode(BaseModel):
    email: EmailStr
    code: constr(min_length=6, max_length=6, pattern=r"^\d{6}$")

class VerifyEmailResponse(BaseModel):
    mensagem: str


# --- Redefinição de senha por código ---
class RequestPasswordResetCode(BaseModel):
    email: EmailStr

class ResetPasswordWithCode(BaseModel):
    email: EmailStr
    code: constr(min_length=6, max_length=6, pattern=r"^\d{6}$")
    nova_senha: constr(min_length=8)

class ResetPasswordResponse(BaseModel):
    mensagem: str


# ============== DESAFIO DE ABSTINÊNCIA ==============
class DesafioCreate(BaseModel):
    dias_meta: conint(ge=1, le=365) = Field(..., description="Meta de dias (ex.: 7, 14, 30)")

class DesafioOut(BaseModel):
    id: int
    data_inicio: date
    dias_meta: int
    streak_atual: int
    ultimo_checkin: Optional[date] = None
    concluido: bool
    data_conclusao: Optional[date] = None
    criado_em: datetime

    class Config:
        from_attributes = True


# ============== GATILHOS ==============
class GatilhoBase(BaseModel):
    nome: str
    dias_da_semana: List[int] = Field(default_factory=list, description="0=Seg ... 6=Dom")
    hora_inicio: time
    hora_fim: time
    ativo: bool = True

class GatilhoCreate(GatilhoBase):
    pass

class GatilhoUpdate(BaseModel):
    nome: Optional[str] = None
    dias_da_semana: Optional[List[int]] = None
    hora_inicio: Optional[time] = None
    hora_fim: Optional[time] = None
    ativo: Optional[bool] = None

class GatilhoOut(GatilhoBase):
    id: int
    criado_em: datetime
    class Config:
        from_attributes = True


# ============== PLANO DE DESINTOXICAÇÃO ==============
class DetoxPlanoCreate(BaseModel):
    titulo: str
    objetivos: str
    atividades_diarias: List[str] = Field(default_factory=list)
    dicas: Optional[str] = None

class DetoxPlanoOut(BaseModel):
    id: int
    titulo: str
    objetivos: str
    atividades_diarias: List[str]
    dicas: Optional[str] = None
    criado_em: datetime
    atualizado_em: datetime



# app/schemas.py
from pydantic import BaseModel, conint, condecimal, Field

class BaselineBase(BaseModel):
    tempo_diario_minutos: conint(ge=0, le=24*60) | None = Field(default=None, description="Minutos por dia")
    dias_por_semana: conint(ge=0, le=7) | None = Field(default=None, description="Dias por semana")
    gasto_medio_dia: condecimal(max_digits=10, decimal_places=2) | None = Field(default=None)
    moeda: str | None = "BRL"

class BaselineCreate(BaselineBase):
    pass

class BaselineUpdate(BaselineBase):
    pass

class BaselineOut(BaselineBase):
    id: int
    usuario_id: int

    class Config:
        from_attributes = True
