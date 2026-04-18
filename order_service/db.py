import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessiomaker, declarative_base

DB_USER = "postgres"
DB_PASSWORD = "password"

DATABASEE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"

engine = create_engine(DATABASEE_URL)
SessionLocal = sessiomaker(bind=engine)

Base = declarative_base()
