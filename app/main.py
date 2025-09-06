# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import engine, Base, SessionLocal

# >>> IMPORTANTE: importar models antes de create_all
from app import models  # garante que todas as tabelas entrem no metadata

# cria tabelas
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # roda o seed na subida do app
    from app.seed import seed_templates
    db = SessionLocal()
    try:
        try:
            seed_templates(db)
            print("[seed] templates Ok")
        except Exception as se:
            # loga mas não derruba o app
            print(f"[seed] erro: {se}")
        yield
    finally:
        db.close()

# >>> Passe o lifespan aqui
app = FastAPI(title="Bet Blocker Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# importa e registra as rotas
import importlib

ROUTES = [
    "app.routes.sites",
    "app.routes.tentativas",
    "app.routes.auth",
    "app.routes.usuarios",
    "app.routes.aconselhamento",
    "app.routes.diario_emocional",
    "app.routes.emergencia",
    "app.routes.desafios",
    "app.routes.gatilhos",
    "app.routes.detox",
    "app.routes.challenges",
]

for mod_path in ROUTES:
    try:
        mod = importlib.import_module(mod_path)
        app.include_router(mod.router)
    except Exception as e:
        # se der erro, loga e relança para não ficar "carregando infinito"
        print(f"[ROUTER ERRO] Falha ao importar {mod_path}: {e}")
        raise
