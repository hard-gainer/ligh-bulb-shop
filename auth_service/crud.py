import hashlib
import os
import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from auth_service.dto import UserRegister, UserRole, UserUpdate
from auth_service.exceptions import email_already_exists
from auth_service.schemas import RefreshToken, User

PASSWORD_SALT = os.getenv("AUTH_PASSWORD_SALT", "auth-salt")
REFRESH_TOKEN_TTL_DAYS = int(os.getenv("AUTH_REFRESH_TOKEN_TTL_DAYS", "14"))
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@admin.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin1234")


def _hash_password(password: str) -> str:
    value = f"{PASSWORD_SALT}:{password}".encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def create_user(db: Session, payload: UserRegister) -> User:
    existing_user = get_user_by_email(db, str(payload.email))
    if existing_user:
        raise email_already_exists()

    user = User(
        email=str(payload.email),
        password_hash=_hash_password(payload.password),
        role=UserRole.USER.value,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    found_user = get_user_by_email(db, str(email))
    if not found_user:
        return None

    if found_user.password_hash != _hash_password(password):
        return None

    if not found_user.is_active:
        return None

    return found_user


def create_refresh_token(db: Session, user_id: int) -> str:
    token = secrets.token_urlsafe(48)
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_TTL_DAYS)
    refresh_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
        revoked=False,
    )
    db.add(refresh_token)
    db.commit()
    return token


def get_valid_refresh_token(db: Session, token: str) -> RefreshToken | None:
    found_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == token, RefreshToken.revoked.is_(False))
        .first()
    )
    if not found_token:
        return None

    if found_token.expires_at < datetime.utcnow():
        return None

    return found_token


def revoke_refresh_token(db: Session, refresh_token: RefreshToken) -> RefreshToken:
    refresh_token.revoked = True
    db.commit()
    db.refresh(refresh_token)
    return refresh_token


def seed_admin(db: Session) -> None:
    if get_user_by_email(db, ADMIN_EMAIL):
        return
    admin = User(
        email=ADMIN_EMAIL,
        password_hash=_hash_password(ADMIN_PASSWORD),
        role=UserRole.ADMIN.value,
        is_active=True,
    )
    db.add(admin)
    db.commit()


def update_user(db: Session, user: User, payload: UserUpdate) -> User:
    user.password_hash = _hash_password(payload.password)
    db.commit()
    db.refresh(user)
    return user
