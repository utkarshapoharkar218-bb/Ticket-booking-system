import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Date,
    ForeignKey, Enum, Text
)
from sqlalchemy.orm import relationship
from .database import Base


class UserRole(str, enum.Enum):
    customer = "customer"
    admin = "admin"


class OrderStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.customer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    bookings = relationship("Booking", back_populates="user")
    food_orders = relationship("FoodOrder", back_populates="user")
    stay_bookings = relationship("StayBooking", back_populates="user")


# ---------------------------------------------------------------
# Ticket booking (supports a "cart" of ticket types, e.g. 2 Adult + 1 Child)
# ---------------------------------------------------------------

class TicketType(Base):
    __tablename__ = "ticket_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)          # Adult, Child
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)


class Slot(Base):
    """One slot per calendar date. Auto-created the first time someone books that date."""
    __tablename__ = "slots"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False, index=True)
    capacity = Column(Integer, nullable=False)

    bookings = relationship("Booking", back_populates="slot")

    def booked_count(self, db):
        from sqlalchemy import func
        total = (
            db.query(func.coalesce(func.sum(BookingItem.quantity), 0))
            .join(Booking, Booking.id == BookingItem.booking_id)
            .filter(Booking.slot_id == self.id, Booking.status != OrderStatus.cancelled)
            .scalar()
        )
        return total or 0


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_code = Column(String(20), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    slot_id = Column(Integer, ForeignKey("slots.id"), nullable=False)
    booking_type = Column(String(30), default="Online Booking")
    payment_method = Column(String(30), nullable=True)
    address = Column(Text, nullable=True)
    total_amount = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.confirmed, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bookings")
    slot = relationship("Slot", back_populates="bookings")
    items = relationship("BookingItem", back_populates="booking", cascade="all, delete-orphan")


class BookingItem(Base):
    __tablename__ = "booking_items"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    ticket_type_id = Column(Integer, ForeignKey("ticket_types.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    booking = relationship("Booking", back_populates="items")
    ticket_type = relationship("TicketType")


# ---------------------------------------------------------------
# Food ordering
# ---------------------------------------------------------------

class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)


class FoodOrder(Base):
    __tablename__ = "food_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_code = Column(String(20), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.confirmed, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="food_orders")
    items = relationship("FoodOrderItem", back_populates="order", cascade="all, delete-orphan")


class FoodOrderItem(Base):
    __tablename__ = "food_order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("food_orders.id"), nullable=False)
    food_item_id = Column(Integer, ForeignKey("food_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    order = relationship("FoodOrder", back_populates="items")
    food_item = relationship("FoodItem")


# ---------------------------------------------------------------
# Stay booking
# ---------------------------------------------------------------

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)   # Standard Room, Deluxe Room, Luxury Cottage
    price_per_night = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)


class StayBooking(Base):
    __tablename__ = "stay_bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_code = Column(String(20), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    customer_name = Column(String(100), nullable=False)
    mobile = Column(String(15), nullable=False)
    checkin_date = Column(Date, nullable=False)
    checkout_date = Column(Date, nullable=False)
    guests = Column(Integer, default=1)
    rooms_count = Column(Integer, default=1)
    nights = Column(Integer, nullable=False)
    subtotal = Column(Float, nullable=False)
    gst_amount = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.confirmed, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="stay_bookings")
    room = relationship("Room")
