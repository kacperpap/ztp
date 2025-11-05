from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import JSON

from .database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)

    histories = relationship("ProductHistory", back_populates="product", cascade="all, delete-orphan")


class ProductHistory(Base):
    __tablename__ = "product_histories"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    operation = Column(String(20), nullable=False)  # 'create', 'update', 'delete'
    snapshot = Column(Text, nullable=False)  # JSON string snapshot

    product = relationship("Product", back_populates="histories")


class ForbiddenPhrase(Base):
    __tablename__ = "forbidden_phrases"

    id = Column(Integer, primary_key=True, index=True)
    phrase = Column(String(200), unique=True, nullable=False, index=True)
