from fastapi import FastAPI
from sqladmin import Admin
from app.api.endpoints import admin, qrcodes, sync
from app.db.session import engine
from app.admin_panel import authentication_backend, admin_views

app = FastAPI(title="Acopio API")

# Configurar SQLAdmin
admin_panel = Admin(app, engine, authentication_backend=authentication_backend)
for view in admin_views:
    admin_panel.add_view(view)

app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(qrcodes.router, prefix="/api/v1/qrcodes", tags=["qrcodes"])
app.include_router(sync.router, prefix="/api/v1/sync", tags=["sync"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Acopio API"}
