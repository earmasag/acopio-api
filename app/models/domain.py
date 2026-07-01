from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, CheckConstraint, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Truck(Base):
    __tablename__ = "truck"
    id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String(15), unique=True, nullable=False)
    driver_name = Column(String(100), nullable=False)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
    
    trips = relationship("Trip", back_populates="truck")

class Trip(Base):
    __tablename__ = "trip"
    id = Column(Integer, primary_key=True, index=True)
    truck_id = Column(Integer, ForeignKey("truck.id"), nullable=False)
    origin_camp = Column(String(50), nullable=False)
    destination_camp = Column(String(50), nullable=False)
    dispatched_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), nullable=False, server_default="CREATING")
    
    truck = relationship("Truck", back_populates="trips")
    packages = relationship("Package", back_populates="trip")

class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    # Slug coincide 1:1 con CategoryId del frontend (e.g. "ropa", "comida")
    slug = Column(String(50), unique=True, nullable=True)
    description = Column(String(255), nullable=True)
    
    items = relationship("PackageItem", back_populates="category")

class GarmentType(Base):
    """Tipos de prenda: camisa, pantalon, calzado, etc.
    Los IDs coinciden exactamente con GarmentTypeId del frontend.
    """
    __tablename__ = "garment_type"
    id = Column(String(50), primary_key=True)  # e.g. "camisa", "calzado"
    label = Column(String(100), nullable=False)

class Package(Base):
    __tablename__ = "package"
    id_uuid = Column(String(36), primary_key=True)
    trip_id = Column(Integer, ForeignKey("trip.id"), nullable=True)
    status = Column(String(25), nullable=False)
    packer_name = Column(String(100), nullable=True)
    receiver_name = Column(String(100), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    trip = relationship("Trip", back_populates="packages")
    items = relationship("PackageItem", back_populates="package", cascade="all, delete-orphan")

class PackageItem(Base):
    __tablename__ = "package_item"
    id = Column(Integer, primary_key=True, index=True)
    package_uuid = Column(String(36), ForeignKey("package.id_uuid", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    
    __table_args__ = (
        CheckConstraint('quantity > 0', name='chk_quantity'),
    )
    
    package = relationship("Package", back_populates="items")
    category = relationship("Category", back_populates="items")
    clothing_detail = relationship("ClothingItemDetail", back_populates="package_item", uselist=False, cascade="all, delete-orphan")

class ClothingItemDetail(Base):
    """Detalle de prenda para package_items de categoría 'ropa'.
    Relación 1:1 con PackageItem.
    La columna size es texto libre para soportar XS/S/M/L/XL/XXL/2XL/Única
    y también tallas numéricas de calzado (35, 36 ... 48).
    """
    __tablename__ = "clothing_item_detail"
    id = Column(Integer, primary_key=True, index=True)
    package_item_id = Column(Integer, ForeignKey("package_item.id", ondelete="CASCADE"), nullable=False, unique=True)
    garment_type_id = Column(String(50), ForeignKey("garment_type.id"), nullable=False)
    size = Column(String(10), nullable=False)

    package_item = relationship("PackageItem", back_populates="clothing_detail")

class CampToken(Base):
    __tablename__ = "camp_token"
    id = Column(Integer, primary_key=True, index=True)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    camp_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SyncLog(Base):
    __tablename__ = "sync_log"
    sync_id = Column(String(36), primary_key=True)
    event_type = Column(String(50), nullable=False)
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
    result = Column(String(50), nullable=False)
    centro_acopio_id = Column(String(50), nullable=True)
    total_events = Column(Integer, nullable=True)
    processed_count = Column(Integer, nullable=True)
    failed_count = Column(Integer, nullable=True)

class DeadLetterEvent(Base):
    __tablename__ = "dead_letter_queue"
    id = Column(Integer, primary_key=True, index=True)
    sync_id = Column(String(36), ForeignKey("sync_log.sync_id"), nullable=False)
    event_id = Column(String(36), nullable=False)
    event_payload = Column(String, nullable=False)
    error_reason = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
