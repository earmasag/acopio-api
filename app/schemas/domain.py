from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

class TruckBase(BaseModel):
    license_plate: str = Field(..., max_length=15)
    driver_name: str = Field(..., max_length=100)

class TruckCreate(TruckBase):
    pass

class TruckResponse(TruckBase):
    id: int
    registered_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class TripBase(BaseModel):
    truck_id: int
    origin_camp: str = Field(..., max_length=50)
    destination_camp: str = Field(..., max_length=50)

class TripCreate(TripBase):
    pass

class TripResponse(TripBase):
    id: int
    status: str
    dispatched_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)

class PackageItemResponse(BaseModel):
    id: int
    category_id: int
    quantity: int
    
    model_config = ConfigDict(from_attributes=True)

class PackageItemCreate(BaseModel):
    category_id: int
    quantity: int

class PackageResponse(BaseModel):
    id_uuid: str
    trip_id: Optional[int]
    status: str
    packer_name: Optional[str]
    receiver_name: Optional[str]
    updated_at: datetime
    items: List[PackageItemResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class CampTokenCreate(BaseModel):
    camp_name: str = Field(..., max_length=100)

class CampTokenResponse(BaseModel):
    id: int
    camp_name: str
    is_active: bool
    created_at: datetime
    # The actual token string is only returned once upon creation
    token: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
