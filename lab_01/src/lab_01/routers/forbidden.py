from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.orm import Session

from .. import schemas, services, database

router = APIRouter(prefix="/api/v1/forbidden", tags=["forbidden"])

def get_service(db: Session = Depends(database.get_db)):
    return services.ForbiddenService(db)

@router.get("/", response_model=List[schemas.ForbiddenPhraseOut])
def list_phrases(svc: services.ForbiddenService = Depends(get_service)):
    return svc.list_phrases()

@router.post("/", response_model=schemas.ForbiddenPhraseOut, status_code=status.HTTP_201_CREATED)
def create_phrase(payload: schemas.ForbiddenPhraseCreate, svc: services.ForbiddenService = Depends(get_service)):
    return svc.create_phrase(payload.phrase)

@router.delete("/{phrase_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_phrase(phrase_id: int, svc: services.ForbiddenService = Depends(get_service)):
    svc.delete_phrase(phrase_id)
    return None
