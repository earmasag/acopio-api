from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.domain import CampToken

router = APIRouter()


class CampValidationResponse(BaseModel):
    valid: bool
    camp_name: str | None = None


@router.get("/validate/{camp_code}", response_model=CampValidationResponse,
            summary="Validar código de centro de acopio")
async def validate_camp_code(camp_code: str, db: AsyncSession = Depends(get_db)):
    """
    Endpoint público para que el móvil valide un código de centro de acopio
    al momento de ingresarlo. Devuelve el nombre del campamento si es válido.
    """
    normalized = camp_code.strip().lower()
    result = await db.execute(
        select(CampToken).where(
            CampToken.token_hash == normalized,
            CampToken.is_active == True
        )
    )
    camp = result.scalar_one_or_none()

    if not camp:
        return CampValidationResponse(valid=False)

    return CampValidationResponse(valid=True, camp_name=camp.camp_name)
