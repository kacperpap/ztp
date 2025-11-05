import os
import json
import tempfile
import pytest
from fastapi.testclient import TestClient

# ensure using a temp sqlite db for tests
os.environ["DATABASE_URL"] = "sqlite:///./test_lab01.db"

from lab_01.main import app
from lab_01.database import engine, Base

@pytest.fixture(autouse=True)
def prepare_db():
    # make fresh db file
    try:
        os.remove("test_lab01.db")
    except FileNotFoundError:
        pass
    Base.metadata.create_all(bind=engine)
    yield
    try:
        os.remove("test_lab01.db")
    except FileNotFoundError:
        pass

client = TestClient(app)

def test_create_and_get_product_and_history_and_constraints():
    # create a forbidden phrase
    r = client.post("/api/forbidden/", json={"phrase": "bad"})
    assert r.status_code == 201

    # try to create product with forbidden phrase in name (blocked)
    r = client.post("/api/products/", json={
        "name": "GoodBadProduct",
        "category": "electronics",
        "price": 100.0,
        "quantity": 1
    })
    assert r.status_code == 400
    assert "forbidden" in r.json()["detail"]["name"].lower()

    # create valid product
    r = client.post("/api/products/", json={
        "name": "Phone123",
        "category": "electronics",
        "price": 500.0,
        "quantity": 10
    })
    assert r.status_code == 201
    product = r.json()
    pid = product["id"]

    # duplicate name should fail
    r = client.post("/api/products/", json={
        "name": "Phone123",
        "category": "electronics",
        "price": 600.0,
        "quantity": 1
    })
    assert r.status_code == 400

    # price out of range for category
    r = client.post("/api/products/", json={
        "name": "CheapBook1",
        "category": "books",
        "price": 1.0,
        "quantity": 1
    })
    assert r.status_code == 400
    assert "price" in r.json()["detail"]

    # update product price and quantity (valid)
    r = client.put(f"/api/products/{pid}", json={
        "price": 1000.0,
        "quantity": 5
    })
    assert r.status_code == 200
    updated = r.json()
    assert updated["price"] == 1000.0
    assert updated["quantity"] == 5

    # get history for product (should have create + update)
    r = client.get(f"/api/products/{pid}/history")
    assert r.status_code == 200
    history = r.json()
    # at least two entries
    assert len(history) >= 2

    # delete product
    r = client.delete(f"/api/products/{pid}")
    assert r.status_code == 204

    # history still accessible (after deletion should still have entries)
    r = client.get(f"/api/products/{pid}/history")
    assert r.status_code == 200
    history_after = r.json()
    assert any(h["operation"] == "delete" for h in history_after)

def test_name_validation_and_quantity():
    # name too short
    r = client.post("/api/products/", json={
        "name": "ab",
        "category": "clothing",
        "price": 20.0,
        "quantity": 1
    })
    assert r.status_code == 422  # pydantic validation

    # invalid characters
    r = client.post("/api/products/", json={
        "name": "name-with-dash",
        "category": "clothing",
        "price": 20.0,
        "quantity": 1
    })
    assert r.status_code == 422

    # negative quantity
    r = client.post("/api/products/", json={
        "name": "Shirt1",
        "category": "clothing",
        "price": 20.0,
        "quantity": -5
    })
    assert r.status_code == 422
