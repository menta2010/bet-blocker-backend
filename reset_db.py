# reset_db.py
from sqlalchemy import text
from app.database import engine, Base
from app import models  # garante que os models registrem as tabelas

print("Dropando schema public com CASCADE…")
with engine.connect() as conn:
    conn.execution_options(isolation_level="AUTOCOMMIT")
    conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;"))

print("Recriando tabelas…")
Base.metadata.create_all(bind=engine)
print("Tabelas recriadas com sucesso!")
