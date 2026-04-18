from datetime import datetime
from models import OrderCreate, OrderResponse
from fastapi import FastAPI


app = FastAPI()


@app.post("", response_model=OrderResponse)
async def create_order(order: OrderCreate):
    return {
        "order_id": 505,
        "status": "CREATED",
        "total_price": 1500.0,
        "created_at": datetime.now(),
    }


@app.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int):
    return {
        "order_id": order_id,
        "status": "PROCESSING",
        "total_price": 1500.0,
        "created_at": datetime.now(),
    }


@app.patch("/{order_id}/status")
async def update_order_status(order_id: int, status: str):
    return {"message": f"Order {order_id} status updated to {status}"}
