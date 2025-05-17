from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base

class SiteBloqueado(Base):
    __tablename__ = "sites_bloqueados"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    tipo = Column(String, default="apostas")
    data_cadastro = Column(DateTime, default=datetime.utcnow)

class TentativaAcesso(Base):
    __tablename__ = "tentativas_acesso"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    usuario_id = Column(String, index=True)
    data_hora = Column(DateTime, default=datetime.utcnow)
