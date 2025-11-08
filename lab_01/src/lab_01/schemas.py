from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, constr
from enum import Enum

class Category(Enum):
    electronics = "electronics"
    books = "books"
    clothing = "clothing"

class ProductCreate(BaseModel):
    name: constr(min_length=3, max_length=20, pattern=r'^[A-Za-z0-9]+$') = Field(..., description="Only letters and digits, 3-20 chars.")
    category: Category
    price: float
    quantity: int

    @field_validator("quantity")
    def quantity_non_negative(cls, v):
        if v < 0:
            raise ValueError("quantity must be >= 0")
        return v

class ProductUpdate(BaseModel):
    name: Optional[constr(min_length=3, max_length=20, pattern=r'^[A-Za-z0-9]+$')]
    category: Optional[Category]
    price: Optional[float]
    quantity: Optional[int]

    @field_validator("quantity")
    def quantity_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("quantity must be >= 0")
        return v

class ProductOut(BaseModel):
    id: int
    name: str
    category: Category
    price: float
    quantity: int

    model_config = {"from_attributes": True}

class ForbiddenPhraseCreate(BaseModel):
    phrase: str = Field(..., min_length=1)

class ForbiddenPhraseOut(BaseModel):
    id: int
    phrase: str

    model_config = {"from_attributes": True}

class ProductHistoryOut(BaseModel):
    id: int
    product_id: int
    changed_at: datetime
    operation: str
    snapshot: str

    model_config = {"from_attributes": True}
