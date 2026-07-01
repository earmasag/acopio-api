from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from app.core.config import settings
from app.models.domain import Category, CampToken, Package, PackageItem, Truck, Trip, SyncLog, DeadLetterEvent, GarmentType, ClothingItemDetail

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form.get("username"), form.get("password")
        
        # Validar contraseña con ADMIN_SECRET (ignoramos el usuario)
        if password == settings.ADMIN_SECRET:
            # Login exitoso
            request.session.update({"token": "admin_authenticated"})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False
        return True

authentication_backend = AdminAuth(secret_key=settings.ADMIN_SECRET)

# Definición de las Vistas (Cómo se ven las tablas)

class CampTokenView(ModelView, model=CampToken):
    column_list = [CampToken.id, CampToken.camp_name, CampToken.token_hash, CampToken.is_active, CampToken.created_at]
    column_searchable_list = [CampToken.camp_name]
    name = "Camp Token"
    name_plural = "Camp Tokens"
    icon = "fa-solid fa-key"

class CategoryView(ModelView, model=Category):
    column_list = [Category.id, Category.name, Category.description]
    name = "Category"
    name_plural = "Categories"
    icon = "fa-solid fa-tags"

class TruckView(ModelView, model=Truck):
    column_list = [Truck.id, Truck.license_plate, Truck.driver_name, Truck.registered_at]
    name = "Truck"
    name_plural = "Trucks"
    icon = "fa-solid fa-truck"

class TripView(ModelView, model=Trip):
    column_list = [Trip.id, Trip.truck_id, Trip.origin_camp, Trip.destination_camp, Trip.status, Trip.dispatched_at]
    name = "Trip"
    name_plural = "Trips"
    icon = "fa-solid fa-route"

class PackageView(ModelView, model=Package):
    column_list = [Package.id_uuid, Package.trip_id, Package.status, Package.packer_name, Package.receiver_name, Package.updated_at]
    column_searchable_list = [Package.id_uuid, Package.packer_name]
    name = "Package"
    name_plural = "Packages"
    icon = "fa-solid fa-box"

class PackageItemView(ModelView, model=PackageItem):
    column_list = [PackageItem.id, PackageItem.package_uuid, PackageItem.category_id, PackageItem.quantity]
    name = "Package Item"
    name_plural = "Package Items"
    icon = "fa-solid fa-boxes-stacked"

class GarmentTypeView(ModelView, model=GarmentType):
    column_list = [GarmentType.id, GarmentType.label]
    name = "Garment Type"
    name_plural = "Garment Types"
    icon = "fa-solid fa-shirt"

class ClothingItemDetailView(ModelView, model=ClothingItemDetail):
    column_list = [ClothingItemDetail.id, ClothingItemDetail.package_item_id, ClothingItemDetail.garment_type_id, ClothingItemDetail.size]
    column_searchable_list = [ClothingItemDetail.garment_type_id, ClothingItemDetail.size]
    name = "Clothing Detail"
    name_plural = "Clothing Details"
    icon = "fa-solid fa-tags"

class SyncLogView(ModelView, model=SyncLog):
    column_list = [SyncLog.sync_id, SyncLog.event_type, SyncLog.result, SyncLog.centro_acopio_id, SyncLog.total_events, SyncLog.processed_count, SyncLog.failed_count, SyncLog.processed_at]
    column_searchable_list = [SyncLog.sync_id, SyncLog.centro_acopio_id]
    name = "Sync Log"
    name_plural = "Sync Logs"
    icon = "fa-solid fa-list-check"

class DeadLetterEventView(ModelView, model=DeadLetterEvent):
    column_list = [DeadLetterEvent.id, DeadLetterEvent.sync_id, DeadLetterEvent.event_id, DeadLetterEvent.error_reason, DeadLetterEvent.created_at]
    column_searchable_list = [DeadLetterEvent.sync_id, DeadLetterEvent.event_id, DeadLetterEvent.error_reason]
    name = "Dead Letter Event"
    name_plural = "Dead Letter Events"
    icon = "fa-solid fa-triangle-exclamation"

# Exportamos todas las vistas
admin_views = [
    CampTokenView,
    CategoryView,
    GarmentTypeView,
    ClothingItemDetailView,
    TruckView,
    TripView,
    PackageView,
    PackageItemView,
    SyncLogView,
    DeadLetterEventView
]
