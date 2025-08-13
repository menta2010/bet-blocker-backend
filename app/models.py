from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint 
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

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

    tentativas = relationship("TentativaAcesso", back_populates="usuario", cascade="all, delete-orphan")
    sites = relationship("SiteBloqueado", back_populates="usuario", cascade="all, delete-orphan")
    aconselhamentos = relationship("Aconselhamento", back_populates="usuario", cascade="all, delete-orphan")
    diarios = relationship("DiarioEmocional", back_populates="usuario", cascade="all, delete")
    contatos_emergencia = relationship("EmergenciaContato", back_populates="usuario", cascade="all, delete-orphan")

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
