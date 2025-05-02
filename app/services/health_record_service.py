from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import UploadFile, HTTPException, status

from app.models.health_record import HealthRecord, RecordType
from app.models.health_record_media import HealthRecordMedia, MediaType
from app.schemas.health_record import HealthRecordCreate, HealthRecordUpdate
from app.utils.file_storage import save_upload_file

def create_health_record(db: Session, record_data: HealthRecordCreate, user_id: int) -> HealthRecord:
    """Create a new health record for a pet"""
    db_record = HealthRecord(
        pet_id=record_data.pet_id,
        user_id=user_id,
        record_type=record_data.record_type,
        notes=record_data.notes,
        weight=record_data.weight,
        next_reminder_date=record_data.next_reminder_date
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def add_media_to_health_record(
    db: Session, 
    health_record_id: int, 
    file: UploadFile,
    file_type: MediaType
) -> HealthRecordMedia:
    """Add media (image, video, document) to a health record"""
    # Check if health record exists
    health_record = db.query(HealthRecord).filter(HealthRecord.id == health_record_id).first()
    if not health_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health record not found")
        
    # Save file to storage
    file_path = save_upload_file(file, f"health_records/{health_record_id}")
    
    # Create media record
    db_media = HealthRecordMedia(
        health_record_id=health_record_id,
        file_path=file_path,
        media_type=file_type
    )
    
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    return db_media

def add_multiple_media_to_health_record(
    db: Session,
    health_record_id: int,
    files: List[UploadFile],
    file_types: List[MediaType]
) -> List[HealthRecordMedia]:
    """Add multiple media files to a health record"""
    # Check if health record exists
    health_record = db.query(HealthRecord).filter(HealthRecord.id == health_record_id).first()
    if not health_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health record not found")
    
    # Process each file
    media_items = []
    for i, file in enumerate(files):
        # Use the provided file type or default to IMAGE if index out of range
        file_type = file_types[i] if i < len(file_types) else MediaType.IMAGE
        
        # Save file to storage
        file_path = save_upload_file(file, f"health_records/{health_record_id}")
        
        # Create media record
        db_media = HealthRecordMedia(
            health_record_id=health_record_id,
            file_path=file_path,
            media_type=file_type
        )
        
        db.add(db_media)
        media_items.append(db_media)
    
    # Commit all at once for better performance
    db.commit()
    
    # Refresh all items to get their IDs
    for item in media_items:
        db.refresh(item)
        
    return media_items

def get_pet_health_records(
    db: Session, 
    pet_id: int, 
    skip: int = 0, 
    limit: int = 100,
    record_type: Optional[RecordType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[HealthRecord]:
    """Get health records for a specific pet"""
    query = db.query(HealthRecord).filter(HealthRecord.pet_id == pet_id)
    
    if record_type:
        query = query.filter(HealthRecord.record_type == record_type)
    
    if start_date:
        query = query.filter(HealthRecord.record_date >= start_date)
        
    if end_date:
        query = query.filter(HealthRecord.record_date <= end_date)
        
    return query.order_by(
        HealthRecord.record_date.desc()
    ).offset(skip).limit(limit).all()

def get_health_record_by_id(db: Session, record_id: int) -> Optional[HealthRecord]:
    """Get a specific health record by ID"""
    return db.query(HealthRecord).filter(HealthRecord.id == record_id).first()

def update_health_record(db: Session, record_id: int, record_data: HealthRecordUpdate) -> Optional[HealthRecord]:
    """Update a health record"""
    db_record = get_health_record_by_id(db, record_id)
    if not db_record:
        return None
        
    # Update fields from the data
    update_data = record_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)
        
    db.commit()
    db.refresh(db_record)
    return db_record

def delete_health_record(db: Session, record_id: int) -> bool:
    """Delete a health record"""
    db_record = get_health_record_by_id(db, record_id)
    if not db_record:
        return False
        
    db.delete(db_record)
    db.commit()
    return True
