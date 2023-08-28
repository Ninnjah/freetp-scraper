from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, BigInteger, func
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    ext: Mapped[str] = mapped_column(String(30), nullable=False)
    url: Mapped[str] = mapped_column(String(200), nullable=False)
    size: Mapped[Optional[int]] = mapped_column(BigInteger(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(), server_default=func.now(), server_onupdate=func.now())
