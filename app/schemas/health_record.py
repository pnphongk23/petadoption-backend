from typing import Optional, List, Union
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from enum import Enum

class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"

class RecordType(str, Enum):
    GENERAL = "general"
    VACCINATION = "vaccination"
    TREATMENT = "treatment"
    WEIGHT = "weight"

class HealthRecordMediaBase(BaseModel):
    media_type: MediaType
    file_path: str

class HealthRecordMediaCreate(HealthRecordMediaBase):
    pass

class HealthRecordMediaResponse(HealthRecordMediaBase):
    id: int
    health_record_id: int
    upload_date: datetime
    
    class Config:
        orm_mode = True

class HealthRecordBase(BaseModel):
    record_type: RecordType
    notes: Optional[str] = None
    weight: Optional[float] = None
    next_reminder_date: Optional[datetime] = None

class HealthRecordCreate(HealthRecordBase):
    pet_id: int

class HealthRecordUpdate(HealthRecordBase):
    pass

class HealthRecordResponse(HealthRecordBase):
    id: int
    pet_id: int
    user_id: int
    record_date: datetime
    media_items: List[HealthRecordMediaResponse] = []
    
    class Config:
        orm_mode = True
