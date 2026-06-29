import uuid
import hashlib
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.session import get_db
from app.models.domain import CampToken
from app.schemas.domain import CampTokenCreate, CampTokenResponse
from app.api.deps import verify_admin_secret

router = APIRouter()

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

@router.post("/tokens", response_model=CampTokenResponse, dependencies=[Depends(verify_admin_secret)])
async def create_token(token_in: CampTokenCreate, db: AsyncSession = Depends(get_db)):
    raw_token = str(uuid.uuid4())
    hashed_token = hash_token(raw_token)
    
    db_token = CampToken(
        token_hash=hashed_token,
        camp_name=token_in.camp_name,
        is_active=True
    )
    db.add(db_token)
    await db.commit()
    await db.refresh(db_token)
    
    response_data = db_token.__dict__.copy()
    response_data["token"] = raw_token
    return response_data

@router.get("/tokens", response_model=List[CampTokenResponse], dependencies=[Depends(verify_admin_secret)])
async def list_tokens(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CampToken))
    tokens = result.scalars().all()
    return tokens

@router.delete("/tokens/{token_id}", dependencies=[Depends(verify_admin_secret)])
async def revoke_token(token_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CampToken).where(CampToken.id == token_id))
    db_token = result.scalar_one_or_none()
    if not db_token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    db_token.is_active = False
    await db.commit()
    return {"status": "revoked"}
