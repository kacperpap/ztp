from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Dict, Any
import re

from . import repositories, models, schemas

PRICE_RULES = {
    "electronics": {"min": 50.0, "max": 50000.0},
    "books": {"min": 5.0, "max": 500.0},
    "clothing": {"min": 10.0, "max": 5000.0},
}

class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = repositories.ProductRepository(db)
        self.forbidden_repo = repositories.ForbiddenRepository(db)
        self.history_repo = repositories.HistoryRepository(db)

    def _check_forbidden(self, name: str):
        phrases = [p.phrase for p in self.forbidden_repo.list_all()]
        lowered = name.lower()
        for ph in phrases:
            if ph.lower() in lowered:
                raise HTTPException(status_code=400, detail={"name": f"Name contains forbidden phrase '{ph}'"})

    def _validate_price_for_category(self, category: str, price: float):
        rules = PRICE_RULES.get(category)
        if not rules:
            raise HTTPException(status_code=400, detail={"category": f"Unknown category '{category}'"})
        if price < rules["min"] or price > rules["max"]:
            raise HTTPException(status_code=400, detail={"price": f"Price {price} out of allowed range [{rules['min']}, {rules['max']}] for category {category}"})

    def create_product(self, data: schemas.ProductCreate) -> models.Product:
        # name uniqueness
        existing = self.repo.get_by_name(data.name)
        if existing:
            raise HTTPException(status_code=400, detail={"name": "Product with this name already exists"})

        # forbidden phrases
        self._check_forbidden(data.name)

        # price rules
        self._validate_price_for_category(data.category.value, data.price)

        product = models.Product(
            name=data.name,
            category=data.category.value,
            price=data.price,
            quantity=data.quantity
        )
        created = self.repo.create(product)
        # save history
        self.history_repo.add_history(created.id, "create", {
            "id": created.id, "name": created.name, "category": created.category, "price": created.price, "quantity": created.quantity
        })
        return created

    def list_products(self):
        return self.repo.list_all()

    def get_product(self, product_id: int):
        p = self.repo.get_by_id(product_id)
        if not p:
            raise HTTPException(status_code=404, detail="Product not found")
        return p

    def update_product(self, product_id: int, data: schemas.ProductUpdate):
        product = self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # if name changes, check uniqueness and pattern already validated by Pydantic
        if data.name and data.name != product.name:
            if self.repo.get_by_name(data.name):
                raise HTTPException(status_code=400, detail={"name": "Product with this name already exists"})
            self._check_forbidden(data.name)
            product.name = data.name

        if data.category:
            # category change may affect price rules for price value later
            product.category = data.category.value

        if data.price is not None:
            # validate price against current or new category
            self._validate_price_for_category(product.category, data.price)
            product.price = data.price

        if data.quantity is not None:
            if data.quantity < 0:
                raise HTTPException(status_code=400, detail={"quantity": "Quantity must be >= 0"})
            product.quantity = data.quantity

        updated = self.repo.update(product)
        # save history (snapshot after update)
        self.history_repo.add_history(updated.id, "update", {
            "id": updated.id, "name": updated.name, "category": updated.category, "price": updated.price, "quantity": updated.quantity
        })
        return updated

    def delete_product(self, product_id: int):
        product = self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        # snapshot before delete
        self.history_repo.add_history(product.id, "delete", {
            "id": product.id, "name": product.name, "category": product.category, "price": product.price, "quantity": product.quantity
        })
        self.repo.delete(product)

    def get_history(self, product_id: int):
        histories = self.history_repo.list_for_product(product_id)
        if not histories:
            raise HTTPException(status_code=404, detail="No history found for product")
        return histories

class ForbiddenService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = repositories.ForbiddenRepository(db)

    def list_phrases(self):
        return self.repo.list_all()

    def create_phrase(self, phrase: str):
        existing = self.repo.get_by_phrase(phrase)
        if existing:
            raise HTTPException(status_code=400, detail="Phrase already exists")
        return self.repo.create(phrase)

    def delete_phrase(self, phrase_id: int):
        self.repo.delete_by_id(phrase_id)
