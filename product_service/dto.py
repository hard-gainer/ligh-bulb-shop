from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from product_service.schemas import Category, Product, ProductImage, Promo, Review


class ProductSortBy(str, Enum):
    CREATED_AT = "created_at"
    PRICE = "price"
    STOCK_QTY = "stock_qty"
    NAME = "name"


class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)


class CategoryResponse(BaseModel):
    category_id: int
    name: str


class ProductCreate(BaseModel):
    category_id: int
    name: str = Field(min_length=1, max_length=255)
    sku: str = Field(min_length=1, max_length=128)
    description: str | None = None
    price: float = Field(gt=0)
    stock_qty: int = Field(ge=0)


class ProductUpdate(BaseModel):
    category_id: int | None = None
    name: str | None = Field(default=None, min_length=1, max_length=255)
    sku: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    stock_qty: int | None = Field(default=None, ge=0)


class ProductImageCreate(BaseModel):
    image_url: str = Field(min_length=1, max_length=1024)


class ProductImageResponse(BaseModel):
    image_id: int
    image_url: str


class ReviewCreate(BaseModel):
    user_id: int
    rating: int = Field(ge=1, le=5)
    description: str = Field(min_length=1)


class ReviewResponse(BaseModel):
    review_id: int
    user_id: int
    rating: int
    description: str
    created_at: datetime


class PromoCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    discount: float = Field(gt=0, le=100)
    start_date: datetime
    end_date: datetime


class PromoResponse(BaseModel):
    promo_id: int
    name: str
    description: str
    discount: float
    start_date: datetime
    end_date: datetime


class ProductResponse(BaseModel):
    product_id: int
    category_id: int
    name: str
    sku: str
    description: str | None
    price: float
    stock_qty: int
    rating: float
    created_at: datetime


class ProductDetailsResponse(ProductResponse):
    images: list[ProductImageResponse]
    promos: list[PromoResponse]


def to_category_response(category: Category) -> CategoryResponse:
    return CategoryResponse(category_id=category.id, name=category.name)


def to_product_image_response(image: ProductImage) -> ProductImageResponse:
    return ProductImageResponse(image_id=image.id, image_url=image.image_url)


def to_review_response(review: Review) -> ReviewResponse:
    return ReviewResponse(
        review_id=review.id,
        user_id=review.user_id,
        rating=review.rating,
        description=review.description,
        created_at=review.created_at,
    )


def to_promo_response(promo: Promo) -> PromoResponse:
    return PromoResponse(
        promo_id=promo.id,
        name=promo.name,
        description=promo.description,
        discount=promo.discount,
        start_date=promo.start_date,
        end_date=promo.end_date,
    )


def to_product_response(product: Product, rating: float) -> ProductResponse:
    return ProductResponse(
        product_id=product.id,
        category_id=product.category_id,
        name=product.name,
        sku=product.sku,
        description=product.description,
        price=product.price,
        stock_qty=product.stock_qty,
        rating=rating,
        created_at=product.created_at,
    )


def to_product_details_response(
    product: Product,
    rating: float,
    promos: list[Promo],
) -> ProductDetailsResponse:
    return ProductDetailsResponse(
        **to_product_response(product, rating=rating).model_dump(),
        images=[to_product_image_response(image) for image in product.images],
        promos=[to_promo_response(promo) for promo in promos],
    )
