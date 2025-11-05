from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from typing import Optional, List
import json

from . import models, schemas

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, product_id: int) -> Optional[models.Product]:
        return self.db.get(models.Product, product_id)

    def get_by_name(self, name: str) -> Optional[models.Product]:
        stmt = select(models.Product).where(models.Product.name == name)
        return self.db.execute(stmt).scalars().first()

    def list_all(self) -> List[models.Product]:
        stmt = select(models.Product)
        return self.db.execute(stmt).scalars().all()

    def create(self, product: models.Product) -> models.Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update(self, product: models.Product) -> models.Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product: models.Product):
        self.db.delete(product)
        self.db.commit()

class ForbiddenRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> List[models.ForbiddenPhrase]:
        stmt = select(models.ForbiddenPhrase)
        return self.db.execute(stmt).scalars().all()

    def get_by_phrase(self, phrase: str) -> Optional[models.ForbiddenPhrase]:
        stmt = select(models.ForbiddenPhrase).where(models.ForbiddenPhrase.phrase == phrase)
        return self.db.execute(stmt).scalars().first()

    def create(self, phrase: str) -> models.ForbiddenPhrase:
        obj = models.ForbiddenPhrase(phrase=phrase)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete_by_id(self, phrase_id: int):
        stmt = delete(models.ForbiddenPhrase).where(models.ForbiddenPhrase.id == phrase_id)
        self.db.execute(stmt)
        self.db.commit()

class HistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_history(self, product_id: int, operation: str, snapshot_obj: dict) -> models.ProductHistory:
        snapshot_json = json.dumps(snapshot_obj, default=str)
        hist = models.ProductHistory(product_id=product_id, operation=operation, snapshot=snapshot_json)
        self.db.add(hist)
        self.db.commit()
        self.db.refresh(hist)
        return hist

    def list_for_product(self, product_id: int):
        stmt = select(models.ProductHistory).where(models.ProductHistory.product_id == product_id).order_by(models.ProductHistory.changed_at.desc())
        return self.db.execute(stmt).scalars().all()
