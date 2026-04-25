from fastapi import HTTPException

PRODUCT_NOT_FOUND_DETAIL = "Product not found"
CATEGORY_NOT_FOUND_DETAIL = "Category not found"
IMAGE_NOT_FOUND_DETAIL = "Image not found"
REVIEW_NOT_FOUND_DETAIL = "Review not found"
PROMO_NOT_FOUND_DETAIL = "Promo not found"
PROMO_LINK_NOT_FOUND_DETAIL = "Promo-product link not found"
PROMO_LINK_ALREADY_EXISTS_DETAIL = "Promo already contains this product"
INVALID_PROMO_DATES_DETAIL = "Promo end_date must be after start_date"
FORBIDDEN_DETAIL = "Forbidden"


def product_not_found() -> HTTPException:
    return HTTPException(status_code=404, detail=PRODUCT_NOT_FOUND_DETAIL)


def category_not_found() -> HTTPException:
    return HTTPException(status_code=404, detail=CATEGORY_NOT_FOUND_DETAIL)


def image_not_found() -> HTTPException:
    return HTTPException(status_code=404, detail=IMAGE_NOT_FOUND_DETAIL)


def review_not_found() -> HTTPException:
    return HTTPException(status_code=404, detail=REVIEW_NOT_FOUND_DETAIL)


def promo_not_found() -> HTTPException:
    return HTTPException(status_code=404, detail=PROMO_NOT_FOUND_DETAIL)


def promo_link_not_found() -> HTTPException:
    return HTTPException(status_code=404, detail=PROMO_LINK_NOT_FOUND_DETAIL)


def promo_link_already_exists() -> HTTPException:
    return HTTPException(status_code=409, detail=PROMO_LINK_ALREADY_EXISTS_DETAIL)


def invalid_promo_dates() -> HTTPException:
    return HTTPException(status_code=400, detail=INVALID_PROMO_DATES_DETAIL)


def forbidden() -> HTTPException:
    return HTTPException(status_code=403, detail=FORBIDDEN_DETAIL)
