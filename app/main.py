# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app import models  # 1) registra models

Base.metadata.create_all(bind=engine)  # 2) cria tabelas

app = FastAPI(title="Bet Blocker Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3) importa routers de forma segura
import importlib

ROUTES = [
    "app.routes.sites",
    "app.routes.tentativas",
    "app.routes.auth",            # rotas de auth (login/register)
    "app.routes.usuarios",
    "app.routes.aconselhamento",
    "app.routes.diario_emocional",
    "app.routes.emergencia",
    "app.routes.desafios",
    "app.routes.gatilhos",
    "app.routes.detox",
]

for mod_path in ROUTES:
    try:
        mod = importlib.import_module(mod_path)
        app.include_router(mod.router)
    except Exception as e:
        print(f"[ROUTER ERRO] Falha ao importar {mod_path}: {e}")
        raise
