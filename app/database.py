from sqlalchemy import create_engine, String
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import Mapped, mapped_column

from app.config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from datetime import date, datetime

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)

Base = declarative_base()


class Spimex(Base):
    __tablename__ = "spimex"

    id: Mapped[int] = mapped_column(default=None, primary_key=True)
    exchange_product_id: Mapped[str]
    exchange_product_name: Mapped[str]
    oil_id: Mapped[str] = mapped_column(String(4))
    delivery_basis_id: Mapped[str] = mapped_column(String(3))
    delivery_basis_name: Mapped[str]
    delivery_type_id: Mapped[str] = mapped_column(String(1))
    volume: Mapped[float]
    total: Mapped[float]
    count: Mapped[float]
    date: Mapped[date]
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=datetime.now(),
        nullable=True,
    )
