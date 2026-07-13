from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base, SessionLocal
from .routers import auth, ticket_types, slots, bookings, food, stay
from . import models

Base.metadata.create_all(bind=engine)


def seed_catalog():
    """
    Seeds ticket types, food items, and rooms if they don't exist yet, so the
    frontend has real IDs to book against without an admin manually creating
    them first. Prices match the frontend's hardcoded prices.
    """
    db = SessionLocal()
    try:
        if db.query(models.TicketType).count() == 0:
            db.add_all([
                models.TicketType(name="Adult", description="Adult entry ticket", price=800),
                models.TicketType(name="Child", description="Child entry ticket", price=500),
            ])

        if db.query(models.FoodItem).count() == 0:
            db.add_all([
                models.FoodItem(name="Veg Combo", price=250),
                models.FoodItem(name="Burger Combo", price=300),
                models.FoodItem(name="Pizza Combo", price=450),
                models.FoodItem(name="Non Veg Combo", price=400),
                models.FoodItem(name="French Fries", price=150),
                models.FoodItem(name="Cold Drink", price=80),
                models.FoodItem(name="Ice Cream", price=120),
            ])

        if db.query(models.Room).count() == 0:
            db.add_all([
                models.Room(name="Standard Room", price_per_night=2500),
                models.Room(name="Deluxe Room", price_per_night=4000),
                models.Room(name="Luxury Cottage", price_per_night=6500),
            ])

        db.commit()
    finally:
        db.close()


app = FastAPI(title="Water Park Ticket Booking API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    seed_catalog()


app.include_router(auth.router)
app.include_router(ticket_types.router)
app.include_router(slots.router)
app.include_router(bookings.router)
app.include_router(food.router)
app.include_router(stay.router)


@app.get("/")
def root():
    return {"message": "Water Park Ticket Booking API is running. Visit /docs for the interactive API docs."}
