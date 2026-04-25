from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from product_service.dto import (
    CategoryCreate,
    ProductCreate,
    ProductImageCreate,
    ProductSortBy,
    ProductUpdate,
    PromoCreate,
    ReviewCreate,
    SortDirection,
)
from product_service.schemas import (
    Category,
    Product,
    ProductImage,
    ProductPromotion,
    Promo,
    Review,
)


def create_category(db: Session, payload: CategoryCreate) -> Category:
    category = Category(name=payload.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_categories(db: Session) -> list[Category]:
    return db.query(Category).order_by(Category.name.asc()).all()


def get_category_by_id(db: Session, category_id: int) -> Category | None:
    return db.query(Category).filter(Category.id == category_id).first()


def create_product(db: Session, payload: ProductCreate) -> Product:
    product = Product(
        category_id=payload.category_id,
        name=payload.name,
        sku=payload.sku,
        description=payload.description,
        price=payload.price,
        stock_qty=payload.stock_qty,
        is_active=True,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_product_by_id(db: Session, product_id: int) -> Product | None:
    return (
        db.query(Product)
        .options(joinedload(Product.images))
        .filter(Product.id == product_id, Product.is_active.is_(True))
        .first()
    )


def get_products(
    db: Session,
    category_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock: bool = False,
    sort_by: ProductSortBy = ProductSortBy.CREATED_AT,
    sort_direction: SortDirection = SortDirection.DESC,
    skip: int = 0,
    limit: int = 20,
) -> list[Product]:
    query = db.query(Product).filter(Product.is_active.is_(True))

    if category_id is not None:
        query = query.filter(Product.category_id == category_id)

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if in_stock:
        query = query.filter(Product.stock_qty > 0)

    if sort_by == ProductSortBy.PRICE:
        query = (
            query.order_by(Product.price.asc())
            if sort_direction == SortDirection.ASC
            else query.order_by(Product.price.desc())
        )
    elif sort_by == ProductSortBy.STOCK_QTY:
        query = (
            query.order_by(Product.stock_qty.asc())
            if sort_direction == SortDirection.ASC
            else query.order_by(Product.stock_qty.desc())
        )
    elif sort_by == ProductSortBy.NAME:
        query = (
            query.order_by(Product.name.asc())
            if sort_direction == SortDirection.ASC
            else query.order_by(Product.name.desc())
        )
    else:
        query = (
            query.order_by(Product.created_at.asc())
            if sort_direction == SortDirection.ASC
            else query.order_by(Product.created_at.desc())
        )

    return query.offset(skip).limit(limit).all()


def update_product(db: Session, product: Product, payload: ProductUpdate) -> Product:
    if payload.category_id is not None:
        product.category_id = payload.category_id
    if payload.name is not None:
        product.name = payload.name
    if payload.sku is not None:
        product.sku = payload.sku
    if payload.description is not None:
        product.description = payload.description
    if payload.price is not None:
        product.price = payload.price
    if payload.stock_qty is not None:
        product.stock_qty = payload.stock_qty

    db.commit()
    db.refresh(product)
    return product


def deactivate_product(db: Session, product: Product) -> Product:
    product.is_active = False
    db.commit()
    db.refresh(product)
    return product


def create_product_image(
    db: Session,
    product_id: int,
    payload: ProductImageCreate,
) -> ProductImage:
    image = ProductImage(product_id=product_id, image_url=payload.image_url)
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


def delete_product_image(db: Session, image_id: int) -> bool:
    image = db.query(ProductImage).filter(ProductImage.id == image_id).first()
    if not image:
        return False

    db.delete(image)
    db.commit()
    return True


def get_reviews(
    db: Session, product_id: int, skip: int = 0, limit: int = 20
) -> list[Review]:
    return (
        db.query(Review)
        .filter(Review.product_id == product_id)
        .order_by(Review.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_review(db: Session, product_id: int, payload: ReviewCreate) -> Review:
    review = Review(
        product_id=product_id,
        user_id=payload.user_id,
        rating=payload.rating,
        description=payload.description,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def delete_review(db: Session, review_id: int) -> bool:
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        return False

    db.delete(review)
    db.commit()
    return True


def get_product_average_rating(db: Session, product_id: int) -> float:
    value = (
        db.query(func.avg(Review.rating))
        .filter(Review.product_id == product_id)
        .scalar()
    )
    if value is None:
        return 0.0
    return float(value)


def create_promo(db: Session, payload: PromoCreate) -> Promo:
    promo = Promo(
        name=payload.name,
        description=payload.description,
        discount=payload.discount,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    db.add(promo)
    db.commit()
    db.refresh(promo)
    return promo


def get_promo_by_id(db: Session, promo_id: int) -> Promo | None:
    return db.query(Promo).filter(Promo.id == promo_id).first()


def get_active_promos(db: Session, skip: int = 0, limit: int = 20) -> list[Promo]:
    now = datetime.utcnow()
    return (
        db.query(Promo)
        .filter(Promo.start_date <= now, Promo.end_date >= now)
        .order_by(Promo.start_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_product_active_promos(db: Session, product_id: int) -> list[Promo]:
    now = datetime.utcnow()
    return (
        db.query(Promo)
        .join(ProductPromotion, Promo.id == ProductPromotion.promo_id)
        .filter(
            ProductPromotion.product_id == product_id,
            Promo.start_date <= now,
            Promo.end_date >= now,
        )
        .order_by(Promo.start_date.desc())
        .all()
    )


def get_product_promo_link(
    db: Session,
    promo_id: int,
    product_id: int,
) -> ProductPromotion | None:
    return (
        db.query(ProductPromotion)
        .filter(
            ProductPromotion.promo_id == promo_id,
            ProductPromotion.product_id == product_id,
        )
        .first()
    )


def attach_product_to_promo(
    db: Session, promo_id: int, product_id: int
) -> ProductPromotion:
    link = ProductPromotion(promo_id=promo_id, product_id=product_id)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


def delete_product_promo_link(db: Session, link: ProductPromotion) -> None:
    db.delete(link)
    db.commit()
