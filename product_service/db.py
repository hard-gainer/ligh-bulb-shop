import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DB_USER = os.getenv("PRODUCT_DB_USER") or os.getenv("DB_USER")
DB_PASSWORD = os.getenv("PRODUCT_DB_PASSWORD") or os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("PRODUCT_DB_HOST") or os.getenv("DB_HOST", "product_db")
DB_NAME = os.getenv("PRODUCT_DB_NAME") or os.getenv("DB_NAME")

if not DB_USER or not DB_PASSWORD or not DB_NAME:
    raise ValueError(
        "PRODUCT_DB_USER, PRODUCT_DB_PASSWORD and PRODUCT_DB_NAME must be set "
        "(or fallback DB_USER, DB_PASSWORD and DB_NAME)"
    )

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
