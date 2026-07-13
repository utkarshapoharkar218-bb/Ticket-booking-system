#1234
# Water Park Ticket Booking – Backend

FastAPI + PostgreSQL backend for a water park ticket booking system.

## 1. Setup

```bash
# create & activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# install dependencies
pip install -r requirements.txt
```

## 2. Database

1. Install PostgreSQL and create a database:
   ```sql
   CREATE DATABASE waterpark_db;
   ```
2. Copy `.env.example` to `.env` and fill in your real Postgres password and a
   random secret key:
   ```bash
   cp .env.example .env
   ```

Tables are created automatically on first run (see `Base.metadata.create_all`
in `app/main.py`) — you don't need to write any SQL by hand.

## 3. Run the server

```bash
uvicorn app.main:app --reload
```

Visit **http://127.0.0.1:8000/docs** — this is auto-generated interactive API
documentation (Swagger UI). Your frontend teammates can use this page to see
every endpoint, what data it expects, and test it directly in the browser.

## 4. Typical flow to test

1. `POST /auth/register` — create a user
2. `POST /auth/login` — get back a JWT `access_token` (plus your `role` and `name`)
3. Click "Authorize" in `/docs` (or send `Authorization: Bearer <token>` header)
4. `GET /ticket-types/` — see the auto-seeded Adult (₹800) / Child (₹500) types
5. `POST /bookings/` — book tickets: pass a `visit_date` and a list of
   `items` (e.g. `[{"ticket_type_id": 1, "quantity": 2}]`) — no need to create
   a slot first, one is auto-created per date with a default daily capacity
6. `GET /bookings/me` — see your bookings
7. `GET /food/items` and `POST /food/orders` — same cart pattern for food
8. `GET /stay/rooms` and `POST /stay/bookings` — book a room stay

To make a user admin (needed for `GET /bookings/`, `GET /food/orders`,
`GET /stay/bookings`, and adjusting slot capacity), run:
```bash
python make_admin.py your_email@example.com
```

## 5. Project structure

```
app/
  main.py            FastAPI app, CORS, router registration, catalog auto-seeding
  database.py         PostgreSQL connection + session
  models.py           SQLAlchemy tables (User, TicketType, Slot, Booking,
                       BookingItem, FoodItem, FoodOrder, FoodOrderItem,
                       Room, StayBooking)
  schemas.py           Pydantic request/response models
  auth.py              password hashing + JWT creation/verification
  slot_utils.py        auto-creates a daily capacity slot per visit date
  routers/
    auth.py            /auth/register, /auth/login
    ticket_types.py     /ticket-types
    slots.py            /slots/{date}/availability, /slots/{date}/capacity
    bookings.py         /bookings  (cart-style: multiple ticket types per booking)
    food.py             /food/items, /food/orders
    stay.py             /stay/rooms, /stay/bookings
```

## 6. Connecting your HTML/CSS frontend

CORS is already open (`allow_origins=["*"]`) so plain `fetch()` calls from
your frontend will work during development. Example from the frontend side:

```javascript
const res = await fetch("http://127.0.0.1:8000/auth/login", {
  method: "POST",
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
  body: new URLSearchParams({ username: email, password: password })
});
const data = await res.json();
localStorage.setItem("token", data.access_token); // careful: fine for a college project

// later, for authenticated requests:
fetch("http://127.0.0.1:8000/bookings/me", {
  headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
});
```

## 7. Ideas to extend (good "extra credit" additions)

- Real payment gateway integration (Razorpay/Stripe test mode)
- QR code generation for each booking (`qrcode` python package) for gate entry
- Email confirmation on booking (via `smtplib` or a service like SendGrid)
- Admin dashboard endpoints: daily revenue, occupancy per slot
- Rate-limit ticket cancellation (e.g., no cancellation within 24h of slot)
