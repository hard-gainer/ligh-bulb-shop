from fastapi import HTTPException

ORDER_NOT_FOUND_DETAIL = "Order not found"


def order_not_found() -> HTTPException:
    return HTTPException(status_code=404, detail=ORDER_NOT_FOUND_DETAIL)
