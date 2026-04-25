from fastapi import HTTPException

ORDER_NOT_FOUND_DETAIL = "Order not found"
ORDER_ACCESS_FORBIDDEN_DETAIL = "You have no access to this order"


def order_not_found() -> HTTPException:
    return HTTPException(status_code=404, detail=ORDER_NOT_FOUND_DETAIL)


def order_access_forbidden() -> HTTPException:
    return HTTPException(status_code=403, detail=ORDER_ACCESS_FORBIDDEN_DETAIL)
