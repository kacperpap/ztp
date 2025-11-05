# src/lab_01/seeds.py
from pathlib import Path
from typing import List
import traceback

from .database import DEFAULT_DB_PATH, DATABASE_URL, engine, SessionLocal, Base
from .models import ForbiddenPhrase
from .repositories import ForbiddenRepository
from .services import ProductService
from .schemas import ProductCreate, Category

def _default_forbidden() -> List[str]:
    return [
        "bad", "forbidden", "xxx", "unwanted", "illegal",
        "pirated", "offensive", "banned", "prohibited", "spam"
    ]

def _default_products() -> List[dict]:
    # must follow business price rules:
    # electronics: min 50.0
    # books: min 5.0
    # clothing: min 10.0
    return [
        {"name": "Phone100", "category": "electronics", "price": 199.99, "quantity": 10},
        {"name": "Laptop2", "category": "electronics", "price": 899.0, "quantity": 5},
        {"name": "Camera3", "category": "electronics", "price": 299.5, "quantity": 7},
        {"name": "EReader1", "category": "electronics", "price": 129.0, "quantity": 12},
        {"name": "NovelA1", "category": "books", "price": 19.99, "quantity": 40},
        {"name": "Textbook2", "category": "books", "price": 59.9, "quantity": 8},
        {"name": "Comic123", "category": "books", "price": 9.5, "quantity": 20},
        {"name": "Shirt01", "category": "clothing", "price": 25.0, "quantity": 50},
        {"name": "Jacket9", "category": "clothing", "price": 120.0, "quantity": 15},
        {"name": "Socks77", "category": "clothing", "price": 8.0, "quantity": 100},
        {"name": "Hat3", "category": "clothing", "price": 15.5, "quantity": 30},
        {"name": "Notebook7", "category": "books", "price": 7.0, "quantity": 60},
        {"name": "Headset5", "category": "electronics", "price": 75.0, "quantity": 22},
        {"name": "Mouse42", "category": "electronics", "price": 45.0 + 10.0, "quantity": 35},  # ensures >= 50 after addition
    ]

def initialize_db_and_seed():
    """
    If DB is file-based and the file doesn't exist yet: create tables and seed initial data.
    Otherwise do nothing.
    """
    # Only apply strict file-existence test for sqlite file URL
    should_seed = False

    if DATABASE_URL.startswith("sqlite"):
        # if DEFAULT_DB_PATH is set and file missing -> seed
        db_path = Path(DEFAULT_DB_PATH)
        if not db_path.exists():
            should_seed = True
    else:
        # For non-file DBs, fallback to: if no tables exist -> seed
        # But we default to not automatic seeding for non-sqlite to avoid unexpected modifications.
        should_seed = False

    if not should_seed:
        return

    # Create tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # --- seed forbidden phrases ---
        forb_repo = ForbiddenRepository(db)
        for phrase in _default_forbidden():
            try:
                if not forb_repo.get_by_phrase(phrase):
                    forb_repo.create(phrase)
            except Exception:
                # continue on errors but print
                print(f"Failed to create forbidden phrase '{phrase}':")
                traceback.print_exc()

        # --- seed products via service (records will also create history entries) ---
        svc = ProductService(db)
        for pdata in _default_products():
            try:
                # construct schema; ProductService will perform validations
                # ensure category uses correct enum string
                payload = ProductCreate(
                    name=pdata["name"],
                    category=Category(pdata["category"]),
                    price=float(pdata["price"]),
                    quantity=int(pdata["quantity"])
                )
                # create product; ignores duplicates due to check inside service
                svc.create_product(payload)
            except Exception as e:
                # print and continue (e.g. if duplicate or validation error)
                print(f"Skipping product {pdata.get('name')}: {e}")
    finally:
        db.close()
