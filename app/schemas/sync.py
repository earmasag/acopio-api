from pydantic import BaseModel, ConfigDict
from typing import Literal, List, Any
from datetime import datetime
from uuid import UUID

class LogisticaEvent(BaseModel):
    event_id: UUID
    package_uuid: str
    action: str
    device_timestamp: datetime
    operator_name: str
    payload: dict[str, Any] = {}

class SyncPayload(BaseModel):
    sync_id: UUID
    centro_acopio_id: str
    events: List[LogisticaEvent]

class FailedEventDetail(BaseModel):
    event_id: UUID
    reason: str

class SyncResponse(BaseModel):
    status: Literal["success", "partial_success", "all_failed", "duplicate"]
    sync_id: UUID
    processed: int
    failed: int
    failed_events: List[FailedEventDetail] = []
    
    model_config = ConfigDict(from_attributes=True)
