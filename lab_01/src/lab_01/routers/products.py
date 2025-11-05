from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.orm import Session

from .. import schemas, services, database

router = APIRouter(prefix="/api/products", tags=["products"])

def get_service(db: Session = Depends(database.get_db)):
    return services.ProductService(db)

@router.post("/", response_model=schemas.ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: schemas.ProductCreate, svc: services.ProductService = Depends(get_service)):
    return svc.create_product(payload)

@router.get("/", response_model=List[schemas.ProductOut])
def list_products(svc: services.ProductService = Depends(get_service)):
    return svc.list_products()

@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, svc: services.ProductService = Depends(get_service)):
    return svc.get_product(product_id)

@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(product_id: int, payload: schemas.ProductUpdate, svc: services.ProductService = Depends(get_service)):
    return svc.update_product(product_id, payload)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, svc: services.ProductService = Depends(get_service)):
    svc.delete_product(product_id)
    return None

@router.get("/{product_id}/history", response_model=List[schemas.ProductHistoryOut])
def get_history(product_id: int, svc: services.ProductService = Depends(get_service)):
    return svc.get_history(product_id)
