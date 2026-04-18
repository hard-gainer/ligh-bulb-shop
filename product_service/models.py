from pydantic import BaseModel
from datetime import datetime

class ProductBase(BaseModel):
    category_id: int
    sku: str
    price: float
    stock_qty: int

class ProductResponse(ProductBase):
    product_id: int
    rating: float
    created_at: datetime

class ReviewCreate(BaseModel):
    rating: int
    description: str

class PromoCreate(BaseModel):
    name: str
    description: str
    discount: float
    start_date: datetime
    end_date: datetime