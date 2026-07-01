from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.domain import Product

router = APIRouter()


class ProductResponse(BaseModel):
    barcode: str
    name: str
    brand: str | None = None
    category_id: int | None = None
    source_api: str | None = None
    image_url: str | None = None

    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    barcode: str
    name: str
    brand: str | None = None
    category_id: int | None = None
    source_api: str | None = None
    image_url: str | None = None


@router.get("/{barcode}", response_model=ProductResponse, summary="Buscar producto en el catálogo local")
async def get_product(barcode: str, db: AsyncSession = Depends(get_db)):
    """
    Primer paso del flujo de escaneo del móvil.
    Consulta el catálogo local de la BD antes de llamar a APIs externas.

    - 200: Producto encontrado en el catálogo local (respuesta rápida, sin internet).
    - 404: Producto no encontrado. El móvil debe consultar las APIs externas y luego
           llamar a POST /api/v1/products para guardar el resultado en el catálogo.
    """
    result = await db.execute(select(Product).where(Product.barcode == barcode.strip()))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado en el catálogo local.")
    return product


@router.post("/", response_model=ProductResponse, status_code=201, summary="Registrar producto en el catálogo local")
async def create_product(data: ProductCreate, db: AsyncSession = Depends(get_db)):
    """
    Segundo paso del flujo de escaneo: el móvil encontró el producto en una API externa
    y lo registra aquí para que futuras consultas sean inmediatas (cache-aside pattern).

    Si el barcode ya existe en el catálogo (otro voluntario lo registró primero), se
    devuelve el registro existente sin error (operación idempotente).
    """
    # Idempotente: si ya existe, devolver sin error
    result = await db.execute(select(Product).where(Product.barcode == data.barcode.strip()))
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    product = Product(
        barcode=data.barcode.strip(),
        name=data.name.strip(),
        brand=data.brand,
        category_id=data.category_id,
        source_api=data.source_api,
        image_url=data.image_url,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product
