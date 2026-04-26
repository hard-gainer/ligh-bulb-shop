import importlib
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from typing import Any

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from product_service import crud
from product_service.db import Base, engine, get_db
from product_service.dto import (
    CategoryCreate,
    CategoryResponse,
    ProductCreate,
    ProductDetailsResponse,
    ProductImageCreate,
    ProductImageResponse,
    ProductResponse,
    ProductSortBy,
    ProductUpdate,
    PromoCreate,
    PromoResponse,
    ReviewCreate,
    ReviewResponse,
    SortDirection,
    to_category_response,
    to_product_details_response,
    to_product_image_response,
    to_product_response,
    to_promo_response,
    to_review_response,
)
from product_service.exceptions import (
    category_not_found,
    image_not_found,
    invalid_promo_dates,
    product_not_found,
    promo_link_already_exists,
    promo_link_not_found,
    promo_not_found,
    review_not_found,
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    importlib.import_module("product_service.schemas")
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/api/v1/products", response_model=list[ProductResponse])
async def get_products(
    category_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock: bool = False,
    sort_by: ProductSortBy = ProductSortBy.CREATED_AT,
    sort_direction: SortDirection = SortDirection.DESC,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
) -> Any:
    found_products = crud.get_products(
        db,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        sort_by=sort_by,
        sort_direction=sort_direction,
        skip=skip,
        limit=limit,
    )
    return [
        to_product_response(
            product,
            rating=crud.get_product_average_rating(db, product.id),
        )
        for product in found_products
    ]


@app.get("/api/v1/products/{product_id}", response_model=ProductDetailsResponse)
async def get_product_by_id(product_id: int, db: Session = Depends(get_db)) -> Any:
    found_product = crud.get_product_by_id(db, product_id)
    if not found_product:
        raise product_not_found()

    rating = crud.get_product_average_rating(db, found_product.id)
    active_promos = crud.get_product_active_promos(db, found_product.id)
    return to_product_details_response(
        found_product, rating=rating, promos=active_promos
    )


@app.post("/api/v1/products", response_model=ProductResponse)
async def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
) -> Any:
    found_category = crud.get_category_by_id(db, payload.category_id)
    if not found_category:
        raise category_not_found()

    created_product = crud.create_product(db, payload)
    return to_product_response(created_product, rating=0.0)


@app.put("/api/v1/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
) -> Any:
    found_product = crud.get_product_by_id(db, product_id)
    if not found_product:
        raise product_not_found()

    if payload.category_id is not None:
        found_category = crud.get_category_by_id(db, payload.category_id)
        if not found_category:
            raise category_not_found()

    updated_product = crud.update_product(db, found_product, payload)
    rating = crud.get_product_average_rating(db, updated_product.id)
    return to_product_response(updated_product, rating=rating)


@app.delete("/api/v1/products/{product_id}", response_model=ProductResponse)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> Any:
    found_product = crud.get_product_by_id(db, product_id)
    if not found_product:
        raise product_not_found()

    deleted_product = crud.deactivate_product(db, found_product)
    rating = crud.get_product_average_rating(db, deleted_product.id)
    return to_product_response(deleted_product, rating=rating)


@app.get("/api/v1/categories", response_model=list[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)) -> Any:
    categories = crud.get_categories(db)
    return [to_category_response(category) for category in categories]


@app.post("/api/v1/categories", response_model=CategoryResponse)
async def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
) -> Any:
    created_category = crud.create_category(db, payload)
    return to_category_response(created_category)


@app.post("/api/v1/products/{product_id}/images", response_model=ProductImageResponse)
async def create_product_image(
    product_id: int,
    payload: ProductImageCreate,
    db: Session = Depends(get_db),
) -> Any:
    found_product = crud.get_product_by_id(db, product_id)
    if not found_product:
        raise product_not_found()

    created_image = crud.create_product_image(db, product_id, payload)
    return to_product_image_response(created_image)


@app.delete("/api/v1/products/images/{image_id}")
async def delete_product_image(
    image_id: int,
    db: Session = Depends(get_db),
) -> Any:
    deleted = crud.delete_product_image(db, image_id)
    if not deleted:
        raise image_not_found()
    return {"message": "Image deleted"}


@app.get("/api/v1/products/{product_id}/reviews", response_model=list[ReviewResponse])
async def get_product_reviews(
    product_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
) -> Any:
    found_product = crud.get_product_by_id(db, product_id)
    if not found_product:
        raise product_not_found()

    reviews = crud.get_reviews(db, product_id, skip=skip, limit=limit)
    return [to_review_response(review) for review in reviews]


@app.post("/api/v1/products/{product_id}/reviews", response_model=ReviewResponse)
async def create_review(
    product_id: int,
    payload: ReviewCreate,
    db: Session = Depends(get_db),
) -> Any:
    found_product = crud.get_product_by_id(db, product_id)
    if not found_product:
        raise product_not_found()

    created_review = crud.create_review(
        db,
        product_id,
        user_id=payload.user_id,
        payload=payload,
    )
    return to_review_response(created_review)


@app.delete("/api/v1/reviews/{review_id}")
async def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
) -> Any:
    found_review = crud.get_review_by_id(db, review_id)
    if not found_review:
        raise review_not_found()

    crud.delete_review(db, found_review)
    return {"message": "Review deleted"}


@app.get("/api/v1/promos", response_model=list[PromoResponse])
async def get_active_promos(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
) -> Any:
    promos = crud.get_active_promos(db, skip=skip, limit=limit)
    return [to_promo_response(promo) for promo in promos]


@app.post("/api/v1/promos", response_model=PromoResponse)
async def create_promo(
    payload: PromoCreate,
    db: Session = Depends(get_db),
) -> Any:
    if payload.end_date <= payload.start_date:
        raise invalid_promo_dates()

    created_promo = crud.create_promo(db, payload)
    return to_promo_response(created_promo)


@app.post("/api/v1/promos/{promo_id}/products/{product_id}")
async def add_product_to_promo(
    promo_id: int,
    product_id: int,
    db: Session = Depends(get_db),
) -> Any:
    found_promo = crud.get_promo_by_id(db, promo_id)
    if not found_promo:
        raise promo_not_found()

    found_product = crud.get_product_by_id(db, product_id)
    if not found_product:
        raise product_not_found()

    existing_link = crud.get_product_promo_link(db, promo_id, product_id)
    if existing_link:
        raise promo_link_already_exists()

    crud.attach_product_to_promo(db, promo_id, product_id)
    return {"message": "Product added to promo"}


@app.delete("/api/v1/promos/{promo_id}/products/{product_id}")
async def remove_product_from_promo(
    promo_id: int,
    product_id: int,
    db: Session = Depends(get_db),
) -> Any:
    found_link = crud.get_product_promo_link(db, promo_id, product_id)
    if not found_link:
        raise promo_link_not_found()

    crud.delete_product_promo_link(db, found_link)
    return {"message": "Product removed from promo"}
