from fastapi import FastAPI
from app.api.endpoints import admin, qrcodes, sync

app = FastAPI(title="Acopio API")

app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(qrcodes.router, prefix="/api/v1/qrcodes", tags=["qrcodes"])
app.include_router(sync.router, prefix="/api/v1/sync", tags=["sync"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Acopio API"}
