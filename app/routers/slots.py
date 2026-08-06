from datetime import date as date_type
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, auth
from ..database import get_db
from ..slot_utils import get_or_create_slot

router = APIRouter(prefix="/slots", tags=["Slots"])


@router.get("/{visit_date}/availability")
def check_availability(visit_date: date_type, db: Session = Depends(get_db)):
    """Public endpoint the booking page can call to show remaining seats for a date."""
    slot = get_or_create_slot(db, visit_date)
    booked = slot.booked_count(db)
    return {
        "date": visit_date,
        "capacity": slot.capacity,
        "booked": booked,
        "available": slot.capacity - booked,
    }


@router.patch("/{visit_date}/capacity")
def set_capacity(
    visit_date: date_type,
    capacity: int,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(auth.require_admin),
):
    """Admin can override the default daily capacity for a specific date."""
    slot = get_or_create_slot(db, visit_date)
    slot.capacity = capacity
    db.commit()
    db.refresh(slot)
    return {"date": slot.date, "capacity": slot.capacity}
