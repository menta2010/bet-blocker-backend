from fastapi import FastAPI
from app.database import engine, Base
from app.routes import sites, tentativas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bet Blocker Backend")

app.include_router(sites.router)
app.include_router(tentativas.router)
