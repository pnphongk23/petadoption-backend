from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import os
from pathlib import Path

from app.models.health_record_media import HealthRecordMedia
from app.config import settings

def get_media_by_id(db: Session, media_id: int) -> Optional[HealthRecordMedia]:
    """Get media by ID"""
    return db.query(HealthRecordMedia).filter(HealthRecordMedia.id == media_id).first()

def delete_health_record_media(db: Session, media_id: int) -> bool:
    """Delete a media attachment from a health record"""
    media = get_media_by_id(db, media_id)
    if not media:
        return False
    
    # Delete the file from storage
    try:
        file_path = Path(settings.MEDIA_ROOT) / media.file_path
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        # Log error but continue with database deletion
        print(f"Error deleting file: {e}")
        
    # Delete from database
    db.delete(media)
    db.commit()
    return True

def get_media_for_health_record(db: Session, health_record_id: int) -> List[HealthRecordMedia]:
    """Get all media for a health record"""
    return db.query(HealthRecordMedia).filter(
        HealthRecordMedia.health_record_id == health_record_id
    ).all()
