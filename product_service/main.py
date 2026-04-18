from datetime import datetime
from typing import List, Optional
from models import ProductResponse, ReviewCreate, PromoCreate
from fastapi import APIRouter, Depends, HTTPException

product_router = APIRouter(prefix="/api/v1", tags=["Products"])

def get_current_user(token: str = "dummy_token"):
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"user_id": 1, "email": "user@example.com"}

@product_router.get("/products", response_model=List[ProductResponse])
async def get_products(category_id: Optional[int] = None, skip: int = 0, limit: int = 10):
    return [{
        "product_id": 1, "category_id": 1, "sku": "LED-10W-E27", 
        "price": 150.0, "stock_qty": 500, "rating": 4.8, "created_at": datetime.now()
    }]

@product_router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    return {
        "product_id": product_id, "category_id": 1, "sku": "LED-10W-E27", 
        "price": 150.0, "stock_qty": 500, "rating": 4.8, "created_at": datetime.now()
    }

@product_router.post("/products/{product_id}/reviews")
async def add_review(product_id: int, review: ReviewCreate, user: dict = Depends(get_current_user)):
    return {"message": "Review added successfully", "review_id": 101}

@product_router.post("/promos")
async def create_promo(promo: PromoCreate):
    return {"message": "Promo created", "promo_id": 10}