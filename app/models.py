from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean,func ,Date, Time,UniqueConstraint,Numeric,Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime , date
from .database import Base

ChallengeStatusEnum = SAEnum(
    "draft", "active", "completed", "abandoned",
    name="challenge_status_enum"
)

TargetTypeEnum = SAEnum("streak", "money", "time_min", name="challenge_target_type_enum")

class SiteBloqueado(Base):
    __tablename__ = "sites_bloqueados"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    tipo = Column(String, default="apostas")
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)

    usuario = relationship("Usuario", back_populates="sites")


class TentativaAcesso(Base):
    __tablename__ = "tentativas_acesso"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites_bloqueados.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    data_hora = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="tentativas")


class Aconselhamento(Base):
    __tablename__ = "aconselhamentos"

    id = Column(Integer, primary_key=True, index=True)
    mensagem = Column(Text, nullable=False)
    resposta = Column(Text, nullable=False)
    data = Column(DateTime, default=datetime.utcnow)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    usuario = relationship("Usuario", back_populates="aconselhamentos")


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    email = Column(String, unique=True, index=True)
    senha = Column(String)
    email_verificado = Column(Boolean, default=False, nullable=False)
    streak_started_at = Column(DateTime, nullable=True)
    best_streak_days = Column(Integer, nullable=False, default=0)
    last_streak_days = Column(Integer, nullable=False, default=0)
    last_checkin_date = Column(Date, nullable=True)
    

    tentativas = relationship("TentativaAcesso", back_populates="usuario", cascade="all, delete-orphan")
    sites = relationship("SiteBloqueado", back_populates="usuario", cascade="all, delete-orphan")
    aconselhamentos = relationship("Aconselhamento", back_populates="usuario", cascade="all, delete-orphan")
    diarios = relationship("DiarioEmocional", back_populates="usuario", cascade="all, delete")
    contatos_emergencia = relationship("EmergenciaContato", back_populates="usuario", cascade="all, delete-orphan")
    email_codes = relationship("EmailVerificationCode",back_populates="user",cascade="all, delete-orphan")
    desafios = relationship("DesafioAbstinencia", back_populates="usuario", cascade="all, delete")
    gatilhos = relationship("Gatilho", back_populates="usuario", cascade="all, delete")
    detox_planos = relationship("DetoxPlano", back_populates="usuario", cascade="all, delete")

class DiarioEmocional(Base):
    __tablename__ = "diario_emocional"
    id = Column(Integer, primary_key=True, index=True)
    texto = Column(Text, nullable=False)
    sentimento = Column(String)
    resposta = Column(Text)
    data = Column(DateTime, default=datetime.utcnow)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario", back_populates="diarios")

class EmergenciaContato(Base):
    __tablename__ = "contatos_emergencia" 

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    email = Column(String, nullable=False)
    nome = Column(String, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="contatos_emergencia")

class EmailVerificationCode(Base):
    __tablename__ = "email_verification_codes"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), index=True, nullable=False)
    code = Column(String(6), index=True, nullable=False)  
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("Usuario", back_populates="email_codes")


class PasswordResetCode(Base):
    __tablename__ = "password_reset_codes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(6), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("Usuario", backref="password_codes")

# --- GATILHOS ---
class Gatilho(Base):
    __tablename__ = "gatilhos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)

    nome = Column(String, nullable=False)                 # ex.: "Noite", "Dia de pagamento"
    # dias_da_semana: 0=Seg ... 6=Dom (para simplificar salvaremos como string CSV "0,1,6")
    dias_da_semana = Column(String, default="", nullable=False)
    hora_inicio = Column(Time, nullable=False)            # ex.: 20:00
    hora_fim = Column(Time, nullable=False)               # ex.: 23:59
    ativo = Column(Boolean, default=True, nullable=False)

    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

    usuario = relationship("Usuario", back_populates="gatilhos")

# --- PLANO DE DESINTOXICAÇÃO ---
class DetoxPlano(Base):
    __tablename__ = "detox_planos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)

    titulo = Column(String, nullable=False)               # ex.: "Plano de 14 dias"
    objetivos = Column(Text, nullable=False)              # texto livre
    atividades_diarias = Column(Text, nullable=False)     # pode ser JSON em texto
    dicas = Column(Text, nullable=True)

    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    usuario = relationship("Usuario", back_populates="detox_planos")

    # Em Usuario, garanta que existe a relação:
# desafios = relationship("DesafioAbstinencia", back_populates="usuario", cascade="all, delete-orphan")

class DesafioAbstinencia(Base):
    __tablename__ = "desafios_abstinencia"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)

    # nomes que a rota/schemas usam
    data_inicio = Column(Date, default=date.today, nullable=False)
    dias_meta = Column(Integer, nullable=False)           # ex.: 7, 14, 30
    streak_atual = Column(Integer, default=0, nullable=False)
    ultimo_checkin = Column(Date, nullable=True)
    concluido = Column(Boolean, default=False, nullable=False)
    data_conclusao = Column(Date, nullable=True)

    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

    usuario = relationship("Usuario", back_populates="desafios")



class UsuarioBaseline(Base):
    __tablename__ = "usuarios_baseline"
    __table_args__ = (UniqueConstraint("usuario_id", name="uq_baseline_usuario"),)

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)

    # hábitos declarados
    tempo_diario_minutos = Column(Integer, nullable=True)    # ex.: 45
    dias_por_semana = Column(Integer, nullable=True)         # ex.: 5
    gasto_medio_dia = Column(Numeric(10, 2), nullable=True)  # ex.: 50.00
    moeda = Column(String(8), nullable=True, default="BRL")

    criado_em = Column(DateTime, server_default=func.now())
    atualizado_em = Column(DateTime, onupdate=func.now(), server_default=func.now())

    usuario = relationship("Usuario", backref="baseline", uselist=False)


class ChallengeTemplate(Base):
    __tablename__ = "challenge_templates"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(80), unique=True, nullable=True)
    title = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)

    target_type = Column(TargetTypeEnum, nullable=False)
    target_value = Column(Integer, nullable=True)

    starts_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class UserChallenge(Base):
    __tablename__ = "user_challenges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    template_id = Column(Integer, ForeignKey("challenge_templates.id"), nullable=True)
    template = relationship("ChallengeTemplate")

    title = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)

    target_type = Column(TargetTypeEnum, nullable=False)
    target_value = Column(Integer, nullable=False)

    # Observação: o modelo usa deadline_days (não deadline_at)
    deadline_days = Column(Integer, nullable=True)

    # Status agora SEM 'available'
    status = Column(ChallengeStatusEnum, nullable=False, default="draft")

    # datas de ciclo
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    abandoned_at = Column(DateTime, nullable=True)

    # >>> Baselines gravados no start (novos campos)
    baseline_money = Column(Integer, nullable=True)
    baseline_time_min = Column(Integer, nullable=True)
    baseline_streak_days = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)