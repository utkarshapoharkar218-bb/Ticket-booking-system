import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db
from ..slot_utils import get_or_create_slot

router = APIRouter(prefix="/bookings", tags=["Bookings"])


def generate_code(prefix: str) -> str:
    return f"{prefix}-" + uuid.uuid4().hex[:8].upper()


def _serialize_booking(booking: models.Booking) -> dict:
    return {
        "id": booking.id,
        "booking_code": booking.booking_code,
        "visit_date": booking.slot.date,
        "booking_type": booking.booking_type,
        "payment_method": booking.payment_method,
        "total_amount": booking.total_amount,
        "status": booking.status,
        "created_at": booking.created_at,
        "customer_name": booking.user.name if booking.user else None,
        "items": [
            {
                "ticket_type_id": item.ticket_type_id,
                "ticket_type_name": item.ticket_type.name if item.ticket_type else "",
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "subtotal": item.subtotal,
            }
            for item in booking.items
        ],
    }


@router.post("/", response_model=schemas.BookingOut)
def create_booking(
    data: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    if not data.items:
        raise HTTPException(status_code=400, detail="Add at least one ticket to your booking")

    slot = get_or_create_slot(db, data.visit_date)

    # sum requested tickets and validate all ticket types exist
    requested_qty = 0
    line_items = []
    for item in data.items:
        ticket_type = db.query(models.TicketType).filter(
            models.TicketType.id == item.ticket_type_id, models.TicketType.is_active == True  # noqa: E712
        ).first()
        if not ticket_type:
            raise HTTPException(status_code=404, detail=f"Ticket type {item.ticket_type_id} not found")
        if item.quantity <= 0:
            continue
        requested_qty += item.quantity
        line_items.append((ticket_type, item.quantity))

    if requested_qty == 0:
        raise HTTPException(status_code=400, detail="Add at least one ticket to your booking")

    already_booked = slot.booked_count(db)
    if already_booked + requested_qty > slot.capacity:
        remaining = slot.capacity - already_booked
        raise HTTPException(status_code=400, detail=f"Only {remaining} tickets left for {data.visit_date}")

    total_amount = sum(t.price * qty for t, qty in line_items)

    booking = models.Booking(
        booking_code=generate_code("WP"),
        user_id=current_user.id,
        slot_id=slot.id,
        booking_type=data.booking_type,
        payment_method=data.payment_method,
        address=data.address,
        total_amount=total_amount,
        status=models.OrderStatus.confirmed,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    for ticket_type, qty in line_items:
        db.add(models.BookingItem(
            booking_id=booking.id,
            ticket_type_id=ticket_type.id,
            quantity=qty,
            unit_price=ticket_type.price,
            subtotal=ticket_type.price * qty,
        ))
    db.commit()
    db.refresh(booking)

    return _serialize_booking(booking)


@router.get("/me", response_model=List[schemas.BookingOut])
def my_bookings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    bookings = (
        db.query(models.Booking)
        .filter(models.Booking.user_id == current_user.id)
        .order_by(models.Booking.created_at.desc())
        .all()
    )
    return [_serialize_booking(b) for b in bookings]


@router.get("/", response_model=List[schemas.BookingOut])
def all_bookings(
    db: Session = Depends(get_db),
    _admin: models.User = Depends(auth.require_admin),
):
    bookings = db.query(models.Booking).order_by(models.Booking.created_at.desc()).all()
    return [_serialize_booking(b) for b in bookings]


@router.delete("/{booking_id}", response_model=schemas.BookingOut)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != current_user.id and current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not allowed to cancel this booking")

    booking.status = models.OrderStatus.cancelled
    db.commit()
    db.refresh(booking)
    return _serialize_booking(booking)
