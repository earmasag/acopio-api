import json
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.sync import SyncPayload, SyncResponse, FailedEventDetail, LogisticaEvent
from app.models.domain import SyncLog, DeadLetterEvent, Package, PackageItem

class BusinessError(Exception):
    def __init__(self, reason: str):
        self.reason = reason

async def process_sync(db: AsyncSession, payload: SyncPayload) -> SyncResponse:
    # 1. Idempotency Check
    result = await db.execute(select(SyncLog).where(SyncLog.sync_id == str(payload.sync_id)))
    existing_sync = result.scalar_one_or_none()
    
    if existing_sync:
        return SyncResponse(
            status="duplicate",
            sync_id=payload.sync_id,
            processed=existing_sync.processed_count or 0,
            failed=existing_sync.failed_count or 0,
            failed_events=[]
        )
    
    processed_count = 0
    failed_events = []
    dlq_events_to_add = []
    seen_events = set()
    
    try:
        # 2. Process each event
        for event in payload.events:
            event_id_str = str(event.event_id)
            
            if event_id_str in seen_events:
                failed_events.append(FailedEventDetail(event_id=event.event_id, reason="duplicate event_id in batch"))
                continue
            seen_events.add(event_id_str)
            
            try:
                # Basic Validations
                if not event.package_uuid:
                    raise BusinessError("package_uuid is empty")
                if not event.operator_name:
                    raise BusinessError("operator_name is empty")
                
                # Buscar el paquete en DB
                res = await db.execute(select(Package).where(Package.id_uuid == event.package_uuid))
                package = res.scalar_one_or_none()
                
                # Si no existe, lo creamos implícitamente (consistencia eventual por eventos desordenados)
                if not package:
                    package = Package(
                        id_uuid=event.package_uuid,
                        status="CREATING",
                        packer_name=""
                    )
                    db.add(package)

                STATE_WEIGHTS = {
                    "CREATING": 0,
                    "PACKING": 1,
                    "SEALED": 2,
                    "IN_TRANSIT": 3,
                    "DELIVERED": 4
                }
                current_weight = STATE_WEIGHTS.get(package.status, 0)
                
                # State Machine & Actions - Flexible para out-of-order events
                if event.action == "PACK_START":
                    if not package.packer_name:
                        package.packer_name = event.operator_name
                    if current_weight < STATE_WEIGHTS["PACKING"]:
                        package.status = "PACKING"
                    
                elif event.action == "PACK_ADD_ITEM":
                    cat_id = event.payload.get("category_id")
                    qty = event.payload.get("quantity")
                    if not cat_id or not qty:
                        raise BusinessError("missing category_id or quantity")
                    
                    new_item = PackageItem(
                        package_uuid=event.package_uuid,
                        category_id=int(cat_id),
                        quantity=int(qty)
                    )
                    db.add(new_item)
                    if current_weight < STATE_WEIGHTS["PACKING"]:
                        package.status = "PACKING"
                    
                elif event.action == "PACK_SEAL":
                    if current_weight < STATE_WEIGHTS["SEALED"]:
                        package.status = "SEALED"
                    
                elif event.action == "LOAD_SCAN":
                    if current_weight < STATE_WEIGHTS["IN_TRANSIT"]:
                        package.status = "IN_TRANSIT"
                    
                elif event.action == "RECEIVE_SCAN":
                    if current_weight < STATE_WEIGHTS["DELIVERED"]:
                        package.status = "DELIVERED"
                    package.receiver_name = event.operator_name
                
                else:
                    raise BusinessError(f"unknown action: {event.action}")
                
                processed_count += 1
                
            except BusinessError as e:
                # Collect failure
                failed_events.append(FailedEventDetail(event_id=event.event_id, reason=e.reason))
                
                # Prepare DLQ event (do not add yet to avoid FK error)
                dlq_events_to_add.append(DeadLetterEvent(
                    sync_id=str(payload.sync_id),
                    event_id=str(event.event_id),
                    event_payload=event.model_dump_json(),
                    error_reason=e.reason
                ))
                
        # 3. Save SyncLog FIRST to satisfy Foreign Key
        sync_log = SyncLog(
            sync_id=str(payload.sync_id),
            event_type="BATCH_SYNC",
            result="success" if not failed_events else "partial",
            centro_acopio_id=payload.centro_acopio_id,
            total_events=len(payload.events),
            processed_count=processed_count,
            failed_count=len(failed_events)
        )
        db.add(sync_log)
        await db.flush() # Forces INSERT of SyncLog now
        
        # 4. Now save DLQ events safely
        for dlq in dlq_events_to_add:
            db.add(dlq)
        
        # 5. Commit everything in a single transaction
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        raise e
        
    # Calcular estado final
    status = "success"
    if failed_events and processed_count > 0:
        status = "partial_success"
    elif failed_events and processed_count == 0:
        status = "all_failed"
        
    return SyncResponse(
        status=status,
        sync_id=payload.sync_id,
        processed=processed_count,
        failed=len(failed_events),
        failed_events=failed_events
    )
