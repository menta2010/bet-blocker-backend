from pydantic import BaseModel, EmailStr, field_validator, constr, Field, conint,condecimal,ConfigDict,RootModel
from datetime import  date, time,datetime
from typing import Optional, List, Literal


TargetType = Literal["streak", "money", "time_min"]
ChallengeStatus = Literal["draft", "active", "completed", "abandoned"]

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


class MetricsOut(BaseModel):
    streakDays: int
    avoidedBets: int
    moneySaved: float     # R$ acumulado
    timeSavedMin: int     # minutos


class CheckinTodayOut(BaseModel):
    done: bool
    checked_at: date | None = None   # evita colisão com o nome 'date'
    streakDays: int

    class Config:
        from_attributes = True

class HistoryPoint(BaseModel):
    date: date
    avoidedBets: int
    moneySaved: float
    timeSavedMin: int

class HistoryOut(BaseModel):
    points: List[HistoryPoint]

class ChallengeTemplateOut(BaseModel):
    id: int
    slug: Optional[str] = None
    title: str
    description: Optional[str] = None
    target_type: TargetType
    target_value: Optional[int] = None
    starts_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# -------- Create --------
class UserChallengeCreate(BaseModel):
    template_id: Optional[int] = None

    # para custom (quando não vem template_id)
    title: Optional[str] = None
    description: Optional[str] = None
    target_type: Optional[TargetType] = None
    target_value: Optional[int] = None

    # modelo usa deadline_days (mantemos opcional)
    deadline_days: Optional[int] = None


# -------- Start (com baselines) --------
class UserChallengeStart(BaseModel):
    baseline_money: Optional[int] = None
    baseline_time_min: Optional[int] = None
    baseline_streak_days: Optional[int] = None


# -------- Out --------
class UserChallengeOut(BaseModel):
    id: int
    user_id: int

    template_id: Optional[int] = None

    title: str
    description: Optional[str] = None

    target_type: TargetType
    target_value: int

    deadline_days: Optional[int] = None
    status: ChallengeStatus

    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    abandoned_at: Optional[datetime] = None

    # baselines expostos (read-only)
    baseline_money: Optional[int] = None
    baseline_time_min: Optional[int] = None
    baseline_streak_days: Optional[int] = None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserChallengesResponse(RootModel[List[UserChallengeOut]]):
    pass


# Para criar item de catálogo (template de desafio)
class ChallengeTemplateCreate(BaseModel):
    slug: str | None = None
    title: str
    description: str | None = None
    target_type: TargetType           # "streak" | "money" | "time_min"
    target_value: int | None = None   # opcional (o modelo permite NULL)
    starts_at: datetime | None = None
    expires_at: datetime | None = None
