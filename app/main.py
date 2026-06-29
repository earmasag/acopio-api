from fastapi import FastAPI
from app.api.endpoints import admin

app = FastAPI(title="Acopio API")

app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Acopio API"}
