from sqlalchemy.orm import Session

from order_service.dto import OrderCreate, OrderStatus
from order_service.schemas import Order, OrderProduct


def _get_actual_product_price(product_id: int) -> float:
    return float(100 + product_id * 10)


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
