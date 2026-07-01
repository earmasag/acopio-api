from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.sync import SyncPayload, SyncResponse
from app.services.sync_service import process_sync

router = APIRouter()

@router.post("/", response_model=SyncResponse)
async def sync_events(payload: SyncPayload, db: AsyncSession = Depends(get_db)):
    response = await process_sync(db, payload)
    
    status_code = 200
    if response.status in ["partial_success", "all_failed"]:
        status_code = 207
        
    return JSONResponse(content=response.model_dump(mode="json"), status_code=status_code)
