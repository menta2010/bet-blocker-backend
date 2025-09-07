# app/seed.py
from datetime import date, datetime, time, timezone
from sqlalchemy.orm import Session
from app import models

def dttoday() -> datetime:
    """Início do dia em UTC (aware)."""
    now = datetime.now(timezone.utc)
    return now.replace(hour=0, minute=0, second=0, microsecond=0)  # 🛠️

def dt_at_day(day: int) -> datetime:
    """Início do dia 'day' deste mês em UTC (aware)."""
    today_utc = datetime.now(timezone.utc).date()                  # 🛠️
    target_date = today_utc.replace(day=day)                       # cuidado: use valores válidos p/ o mês
    return datetime.combine(target_date, time.min, tzinfo=timezone.utc)  # 🛠️

SEED = [
    dict(
        slug="streak-7",
        title="Ficar 7 dias sem apostar",
        description="Mantenha o streak por 7 dias.",
        target_type="streak",
        target_value=7,
        starts_at=None,
        expires_at=None,
    ),
    dict(
        slug="save-100",
        title="Poupar R$ 100",
        description="Economize evitando apps de aposta.",
        target_type="money",
        target_value=100,
        starts_at=dttoday(),         # 🛠️ aware em UTC
        expires_at=dt_at_day(28),    # 🛠️ aware em UTC
    ),
    dict(
        slug="time-300",
        title="Salvar 5h de tempo",
        description="Acumule 300 min sem apostar.",
        target_type="time_min",
        target_value=300,
        starts_at=None,
        expires_at=None,
    ),
]

def seed_templates(db: Session):
    existing = {t.slug for t in db.query(models.ChallengeTemplate).all()}
    for item in SEED:
        if item["slug"] in existing:
            continue
        db.add(models.ChallengeTemplate(**item))
    db.commit()
