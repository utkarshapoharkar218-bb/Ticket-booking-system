from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/ticket-types", tags=["Ticket Types"])


@router.get("/", response_model=List[schemas.TicketTypeOut])
def list_ticket_types(db: Session = Depends(get_db)):
    return db.query(models.TicketType).filter(models.TicketType.is_active == True).all()  # noqa: E712


@router.post("/", response_model=schemas.TicketTypeOut)
def create_ticket_type(
    data: schemas.TicketTypeCreate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(auth.require_admin),
):
    ticket_type = models.TicketType(**data.model_dump())
    db.add(ticket_type)
    db.commit()
    db.refresh(ticket_type)
    return ticket_type
