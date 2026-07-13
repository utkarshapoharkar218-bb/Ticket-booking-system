import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/stay", tags=["Stay"])

GST_RATE = 0.18


def generate_code(prefix: str) -> str:
    return f"{prefix}-" + uuid.uuid4().hex[:8].upper()


@router.get("/rooms", response_model=List[schemas.RoomOut])
def list_rooms(db: Session = Depends(get_db)):
    return db.query(models.Room).filter(models.Room.is_active == True).all()  # noqa: E712


@router.post("/bookings", response_model=schemas.StayBookingOut)
def create_stay_booking(
    data: schemas.StayBookingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    room = db.query(models.Room).filter(models.Room.id == data.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if data.checkout_date <= data.checkin_date:
        raise HTTPException(status_code=400, detail="Check-out date must be after check-in date")

    nights = (data.checkout_date - data.checkin_date).days
    rooms_count = max(1, data.rooms_count)

    subtotal = room.price_per_night * rooms_count * nights
    gst_amount = round(subtotal * GST_RATE, 2)
    total_amount = subtotal + gst_amount

    booking = models.StayBooking(
        booking_code=generate_code("STAY"),
        user_id=current_user.id,
        room_id=room.id,
        customer_name=data.customer_name,
        mobile=data.mobile,
        checkin_date=data.checkin_date,
        checkout_date=data.checkout_date,
        guests=data.guests,
        rooms_count=rooms_count,
        nights=nights,
        subtotal=subtotal,
        gst_amount=gst_amount,
        total_amount=total_amount,
        status=models.OrderStatus.confirmed,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/bookings/me", response_model=List[schemas.StayBookingOut])
def my_stay_bookings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return (
        db.query(models.StayBooking)
        .filter(models.StayBooking.user_id == current_user.id)
        .order_by(models.StayBooking.created_at.desc())
        .all()
    )


@router.get("/bookings", response_model=List[schemas.StayBookingOut])
def all_stay_bookings(
    db: Session = Depends(get_db),
    _admin: models.User = Depends(auth.require_admin),
):
    return db.query(models.StayBooking).order_by(models.StayBooking.created_at.desc()).all()
