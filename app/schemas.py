from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict
from .models import UserRole, OrderStatus


# ---------- User / Auth ----------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    name: str


# ---------- Ticket types ----------
class TicketTypeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


class TicketTypeOut(TicketTypeCreate):
    id: int
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


# ---------- Ticket booking (cart style) ----------
class BookingItemIn(BaseModel):
    ticket_type_id: int
    quantity: int


class BookingItemOut(BaseModel):
    ticket_type_id: int
    ticket_type_name: str
    quantity: int
    unit_price: float
    subtotal: float
    model_config = ConfigDict(from_attributes=True)


class BookingCreate(BaseModel):
    visit_date: date
    booking_type: str = "Online Booking"
    payment_method: Optional[str] = None
    address: Optional[str] = None
    items: List[BookingItemIn]


class BookingOut(BaseModel):
    id: int
    booking_code: str
    visit_date: date
    booking_type: str
    payment_method: Optional[str] = None
    total_amount: float
    status: OrderStatus
    created_at: datetime
    items: List[BookingItemOut] = []
    customer_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# ---------- Food ----------
class FoodItemOut(BaseModel):
    id: int
    name: str
    price: float
    model_config = ConfigDict(from_attributes=True)


class FoodOrderItemIn(BaseModel):
    food_item_id: int
    quantity: int


class FoodOrderItemOut(BaseModel):
    food_item_id: int
    food_item_name: str
    quantity: int
    unit_price: float
    subtotal: float
    model_config = ConfigDict(from_attributes=True)


class FoodOrderCreate(BaseModel):
    items: List[FoodOrderItemIn]


class FoodOrderOut(BaseModel):
    id: int
    order_code: str
    total_amount: float
    status: OrderStatus
    created_at: datetime
    items: List[FoodOrderItemOut] = []
    model_config = ConfigDict(from_attributes=True)


# ---------- Stay ----------
class RoomOut(BaseModel):
    id: int
    name: str
    price_per_night: float
    model_config = ConfigDict(from_attributes=True)


class StayBookingCreate(BaseModel):
    room_id: int
    customer_name: str
    mobile: str
    checkin_date: date
    checkout_date: date
    guests: int = 1
    rooms_count: int = 1


class StayBookingOut(BaseModel):
    id: int
    booking_code: str
    room_id: int
    customer_name: str
    mobile: str
    checkin_date: date
    checkout_date: date
    guests: int
    rooms_count: int
    nights: int
    subtotal: float
    gst_amount: float
    total_amount: float
    status: OrderStatus
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
