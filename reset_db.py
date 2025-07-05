from app.database import Base, engine

# ✅ Importa o arquivo que contém os models (isso registra as tabelas)
from app.models import * 

print("Deletando tabelas...")
Base.metadata.drop_all(bind=engine)

print("Recriando tabelas...")
Base.metadata.create_all(bind=engine)

print("Tabelas recriadas com sucesso!")
