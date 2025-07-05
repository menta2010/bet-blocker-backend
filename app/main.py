from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import sites, tentativas, auth, usuarios


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bet Blocker Backend")

# Permitir acesso da API por qualquer origem (frontend, mobile etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Pode trocar por ['http://localhost', 'https://seusite.com'] depois
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sites.router)
app.include_router(tentativas.router)
app.include_router(auth.router)
app.include_router(usuarios.router)