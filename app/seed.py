# app/seed.py
from datetime import date
from sqlalchemy.orm import Session
from app import models

SEED = [
    dict(slug="streak-7", title="Ficar 7 dias sem apostar",
         description="Mantenha o streak por 7 dias.",
         target_type="streak", target_value=7,
         starts_at=None, expires_at=None, is_active=True),
    dict(slug="save-100", title="Poupar R$ 100",
         description="Economize evitando apps de aposta.",
         target_type="money", target_value=100,
         starts_at=date.today(), expires_at=date.today().replace(day=28),
         is_active=True),
    dict(slug="time-300", title="Salvar 5h de tempo",
         description="Acumule 300 min sem apostar.",
         target_type="time_min", target_value=300,
         starts_at=None, expires_at=None, is_active=True),
]

def seed_templates(db: Session):
    existing = {t.slug for t in db.query(models.ChallengeTemplate).all()}
    for item in SEED:
        if item["slug"] in existing:
            continue
        db.add(models.ChallengeTemplate(**item))
    db.commit()
