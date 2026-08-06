import os
from datetime import date
from sqlalchemy.orm import Session
from . import models

DEFAULT_DAILY_CAPACITY = int(os.getenv("DEFAULT_DAILY_CAPACITY", "500"))


def get_or_create_slot(db: Session, visit_date: date) -> models.Slot:
    """
    The frontend only lets a customer pick a date (no time-slot UI), so we
    manage one slot per calendar date automatically. Admins can still raise
    or lower a specific date's capacity via PATCH /slots/{date}.
    """
    slot = db.query(models.Slot).filter(models.Slot.date == visit_date).first()
    if slot:
        return slot

    slot = models.Slot(date=visit_date, capacity=DEFAULT_DAILY_CAPACITY)
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot
