"""Rack, Item, and Admin ORM models — see specs/001-inventory-tracking/data-model.md."""

from datetime import datetime, timezone

from passlib.context import CryptContext
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _pwd_context.verify(password, password_hash)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Rack(Base):
    """A physical storage location. rack_number is unique, required;
    capacity is required and must be > 0 (data-model.md)."""

    __tablename__ = "racks"

    id = Column(Integer, primary_key=True)
    rack_number = Column(String, unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    items = relationship("Item", back_populates="rack", cascade="all, delete-orphan")

    @property
    def used_capacity(self) -> int:
        """Sum of quantity across all Item rows where rack_id matches this rack."""
        return sum(item.quantity for item in self.items)

    @property
    def remaining_capacity(self) -> int:
        return self.capacity - self.used_capacity


class Item(Base):
    """A stock entry on a rack. quantity is required and must be >= 0;
    rack_id is required, not nullable (data-model.md)."""

    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    rack_id = Column(Integer, ForeignKey("racks.id"), nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    rack = relationship("Rack", back_populates="items")


class Admin(Base):
    """The authenticated user who manages racks/items. Single role in scope
    (data-model.md). password_hash is required, never stored/returned in
    plaintext."""

    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
