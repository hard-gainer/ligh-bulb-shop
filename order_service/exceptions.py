from fastapi import HTTPException

ORDER_NOT_FOUND_DETAIL = "Order not found"
ORDER_ACCESS_FORBIDDEN_DETAIL = "You have no access to this order"
PRODUCT_NOT_FOUND_DETAIL = "Product not found"
PRODUCT_SERVICE_UNAVAILABLE_DETAIL = "Product service is unavailable"


def order_not_found() -> HTTPException:
    return HTTPException(status_code=404, detail=ORDER_NOT_FOUND_DETAIL)


def order_access_forbidden() -> HTTPException:
    return HTTPException(status_code=403, detail=ORDER_ACCESS_FORBIDDEN_DETAIL)


def product_not_found(product_id: int) -> HTTPException:
    return HTTPException(
        status_code=404,
        detail=f"{PRODUCT_NOT_FOUND_DETAIL}: {product_id}",
    )


def product_service_unavailable() -> HTTPException:
    return HTTPException(status_code=503, detail=PRODUCT_SERVICE_UNAVAILABLE_DETAIL)
