import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/food", tags=["Food"])


def generate_code(prefix: str) -> str:
    return f"{prefix}-" + uuid.uuid4().hex[:8].upper()


def _serialize_order(order: models.FoodOrder) -> dict:
    return {
        "id": order.id,
        "order_code": order.order_code,
        "total_amount": order.total_amount,
        "status": order.status,
        "created_at": order.created_at,
        "items": [
            {
                "food_item_id": item.food_item_id,
                "food_item_name": item.food_item.name if item.food_item else "",
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "subtotal": item.subtotal,
            }
            for item in order.items
        ],
    }


@router.get("/items", response_model=List[schemas.FoodItemOut])
def list_food_items(db: Session = Depends(get_db)):
    return db.query(models.FoodItem).filter(models.FoodItem.is_active == True).all()  # noqa: E712


@router.post("/orders", response_model=schemas.FoodOrderOut)
def create_food_order(
    data: schemas.FoodOrderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    if not data.items:
        raise HTTPException(status_code=400, detail="Add at least one food item")

    line_items = []
    for item in data.items:
        food_item = db.query(models.FoodItem).filter(models.FoodItem.id == item.food_item_id).first()
        if not food_item:
            raise HTTPException(status_code=404, detail=f"Food item {item.food_item_id} not found")
        if item.quantity <= 0:
            continue
        line_items.append((food_item, item.quantity))

    if not line_items:
        raise HTTPException(status_code=400, detail="Add at least one food item")

    total_amount = sum(f.price * qty for f, qty in line_items)

    order = models.FoodOrder(
        order_code=generate_code("FOOD"),
        user_id=current_user.id,
        total_amount=total_amount,
        status=models.OrderStatus.confirmed,
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    for food_item, qty in line_items:
        db.add(models.FoodOrderItem(
            order_id=order.id,
            food_item_id=food_item.id,
            quantity=qty,
            unit_price=food_item.price,
            subtotal=food_item.price * qty,
        ))
    db.commit()
    db.refresh(order)

    return _serialize_order(order)


@router.get("/orders/me", response_model=List[schemas.FoodOrderOut])
def my_food_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    orders = (
        db.query(models.FoodOrder)
        .filter(models.FoodOrder.user_id == current_user.id)
        .order_by(models.FoodOrder.created_at.desc())
        .all()
    )
    return [_serialize_order(o) for o in orders]


@router.get("/orders", response_model=List[schemas.FoodOrderOut])
def all_food_orders(
    db: Session = Depends(get_db),
    _admin: models.User = Depends(auth.require_admin),
):
    orders = db.query(models.FoodOrder).order_by(models.FoodOrder.created_at.desc()).all()
    return [_serialize_order(o) for o in orders]
