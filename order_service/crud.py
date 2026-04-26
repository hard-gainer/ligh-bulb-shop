import os

import httpx
from sqlalchemy.orm import Session

from order_service.dto import OrderCreate, OrderStatus
from order_service.exceptions import product_not_found, product_service_unavailable
from order_service.schemas import Order, OrderProduct

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product_service:8000")


def _get_actual_product_price(product_id: int) -> float:
    endpoint = f"{PRODUCT_SERVICE_URL.rstrip('/')}/api/v1/products/{product_id}"

    try:
        response = httpx.get(endpoint, timeout=5.0)
    except httpx.RequestError:
        raise product_service_unavailable()

    if response.status_code == 404:
        raise product_not_found(product_id)

    if response.status_code >= 400:
        raise product_service_unavailable()

    try:
        payload = response.json()
    except ValueError:
        raise product_service_unavailable()

    price = payload.get("price")
    if not isinstance(price, int | float):
        raise product_service_unavailable()

    return float(price)


def create_order(db: Session, payload: OrderCreate) -> Order:
    order = Order(
        phone=payload.phone,
        email=str(payload.email),
        delivery_address=payload.delivery_address,
        status=OrderStatus.CREATED.value,
        total_price=0.0,
    )
    db.add(order)
    db.flush()

    total_price = 0.0
    for item in payload.items:
        unit_price = _get_actual_product_price(item.product_id)
        total_price += unit_price * item.qty

        db.add(
            OrderProduct(
                order_id=order.id,
                product_id=item.product_id,
                qty=item.qty,
                unit_price=unit_price,
            )
        )

    order.total_price = total_price
    db.commit()
    db.refresh(order)
    return order


def get_orders(
    db: Session, email: str | None = None, skip: int = 0, limit: int = 20
) -> list[Order]:
    query = db.query(Order)
    if email:
        query = query.filter(Order.email == email)

    return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


def get_order_by_id(db: Session, order_id: int) -> Order | None:
    return db.query(Order).filter(Order.id == order_id).first()


def update_order_status(db: Session, order_id: int, status: str) -> Order | None:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return None

    order.status = status
    db.commit()
    db.refresh(order)
    return order
