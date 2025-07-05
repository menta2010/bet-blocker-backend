from sqlalchemy import Column, Integer, String, DateTime ,ForeignKey
from sqlalchemy.orm import relationship
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
    site_id = Column(Integer, ForeignKey("sites_bloqueados.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    data_hora = Column(DateTime, default=datetime.utcnow)
    usuario = relationship("Usuario", back_populates="tentativas")

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    email = Column(String, unique=True, index=True)
    senha = Column(String)

    tentativas = relationship("TentativaAcesso", back_populates="usuario")