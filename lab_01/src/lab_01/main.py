# src/lab_01/main.py
from fastapi import FastAPI
import uvicorn

from .routers import products, forbidden
from .seeds import initialize_db_and_seed

app = FastAPI(title="Lab 01 - Products API")

app.include_router(products.router)
app.include_router(forbidden.router)

@app.on_event("startup")
async def on_startup():
    # initialize DB and seed WHEN file DB doesn't yet exist
    initialize_db_and_seed()

def run_dev() -> None:
    uvicorn.run("lab_01.main:app", host="127.0.0.1", port=8000, reload=True, log_level="debug")

def run_prod() -> None:
    uvicorn.run("lab_01.main:app", host="0.0.0.0", port=8000, reload=False, log_level="info")

if __name__ == "__main__":
    run_dev()
