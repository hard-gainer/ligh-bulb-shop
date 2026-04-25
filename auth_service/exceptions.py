from fastapi import HTTPException

EMAIL_ALREADY_EXISTS_DETAIL = "Email already exists"
INVALID_CREDENTIALS_DETAIL = "Invalid credentials"
INVALID_REFRESH_TOKEN_DETAIL = "Invalid refresh token"
USER_NOT_FOUND_DETAIL = "User not found"


def email_already_exists() -> HTTPException:
    return HTTPException(status_code=409, detail=EMAIL_ALREADY_EXISTS_DETAIL)


def invalid_credentials() -> HTTPException:
    return HTTPException(status_code=401, detail=INVALID_CREDENTIALS_DETAIL)


def invalid_refresh_token() -> HTTPException:
    return HTTPException(status_code=401, detail=INVALID_REFRESH_TOKEN_DETAIL)


def user_not_found() -> HTTPException:
    return HTTPException(status_code=404, detail=USER_NOT_FOUND_DETAIL)
