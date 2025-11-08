import os
import json
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from lab_01.main import app
from lab_01.database import Base, get_db

@pytest.fixture(autouse=True)
def prepare_db():
    db_fd, db_path = tempfile.mkstemp()
    database_url = f"sqlite:///{db_path}"
    
    engine = create_engine(database_url)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield  # run the tests
    
    # Cleanup
    engine.dispose()
    os.close(db_fd)
    os.unlink(db_path)

client = TestClient(app)

def test_create_and_get_product_and_history_and_constraints():
    # create a forbidden phrase
    r = client.post("/api/v1/forbidden/", json={"phrase": "bad"})
    assert r.status_code == 201

    # try to create product with forbidden phrase in name (blocked)
    r = client.post("/api/v1/products/", json={
        "name": "GoodBadProduct",
        "category": "electronics",
        "price": 100.0,
        "quantity": 1
    })
    assert r.status_code == 400
    assert "forbidden" in r.json()["detail"]["name"].lower()

    # create valid product
    r = client.post("/api/v1/products/", json={
        "name": "Phone123",
        "category": "electronics",
        "price": 500.0,
        "quantity": 10
    })
    assert r.status_code == 201
    product = r.json()
    pid = product["id"]

    # duplicate name should fail
    r = client.post("/api/v1/products/", json={
        "name": "Phone123",
        "category": "electronics",
        "price": 600.0,
        "quantity": 1
    })
    assert r.status_code == 400

    # price out of range for category
    r = client.post("/api/v1/products/", json={
        "name": "CheapBook1",
        "category": "books",
        "price": 1.0,
        "quantity": 1
    })
    assert r.status_code == 400
    assert "price" in r.json()["detail"]

    # update product price and quantity (valid)
    r = client.put(f"/api/v1/products/{pid}", json={
        "name": "Phone123",
        "category": "electronics",
        "price": 1000.0,
        "quantity": 5
    })
    assert r.status_code == 200
    updated = r.json()
    assert updated["price"] == 1000.0
    assert updated["quantity"] == 5

    # get history for product (should have create + update)
    r = client.get(f"/api/v1/products/{pid}/history")
    assert r.status_code == 200
    history = r.json()
    # at least two entries
    assert len(history) >= 2

    # delete product
    r = client.delete(f"/api/v1/products/{pid}")
    assert r.status_code == 204

def test_name_validation_and_quantity():
    # name too short
    r = client.post("/api/v1/products/", json={
        "name": "ab",
        "category": "clothing",
        "price": 20.0,
        "quantity": 1
    })
    assert r.status_code == 422  # pydantic validation

    # invalid characters
    r = client.post("/api/v1/products/", json={
        "name": "name-with-dash",
        "category": "clothing",
        "price": 20.0,
        "quantity": 1
    })
    assert r.status_code == 422

    # negative quantity
    r = client.post("/api/v1/products/", json={
        "name": "Shirt1",
        "category": "clothing",
        "price": 20.0,
        "quantity": -5
    })
    assert r.status_code == 422
