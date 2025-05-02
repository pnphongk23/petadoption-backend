from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.health_record import RecordType
from app.models.health_record_media import MediaType
from app.schemas.health_record import (
    HealthRecordCreate, 
    HealthRecordResponse, 
    HealthRecordUpdate,
    HealthRecordMediaResponse
)
from app.services.health_record_service import (
    create_health_record, 
    get_pet_health_records,
    get_health_record_by_id,
    update_health_record,
    delete_health_record,
    add_media_to_health_record,
    add_multiple_media_to_health_record
)
from app.services.health_record_media_service import (
    delete_health_record_media,
    get_media_by_id,
    get_media_for_health_record
)
from app.utils.security import get_current_user
from app.utils.pet_ownership import verify_pet_ownership

router = APIRouter(prefix="/health-records", tags=["Health Records"])

@router.post("", response_model=HealthRecordResponse)
def create_record(
    record_data: HealthRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new health record for a pet.
    """
    # Verify the user has access to this pet
    verify_pet_ownership(db, current_user.id, record_data.pet_id)
    
    return create_health_record(db, record_data, current_user.id)

@router.post("/{record_id}/media", response_model=HealthRecordMediaResponse)
def add_media(
    record_id: int,
    file: UploadFile = File(...),
    media_type: MediaType = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add media (image, video, document) to a health record.
    """
    # Check if health record exists and belongs to user's pet
    health_record = get_health_record_by_id(db, record_id)
    if not health_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health record not found")
    
    verify_pet_ownership(db, current_user.id, health_record.pet_id)
    
    return add_media_to_health_record(db, record_id, file, media_type)

@router.post("/{record_id}/media/bulk", response_model=List[HealthRecordMediaResponse])
def add_multiple_media(
    record_id: int,
    files: List[UploadFile] = File(...),
    media_types: List[str] = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add multiple media files (images, videos, documents) to a health record.
    
    - `files`: List of files to upload
    - `media_types`: Comma-separated list of media types (image, video, document)
      Example: "image,video,image"
    """
    # Check if health record exists and belongs to user's pet
    health_record = get_health_record_by_id(db, record_id)
    if not health_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health record not found")
    
    verify_pet_ownership(db, current_user.id, health_record.pet_id)
    
    # Convert string media types to enum values
    try:
        parsed_media_types = []
        for type_str in media_types:
            parsed_media_types.append(MediaType(type_str))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid media type. Allowed values are: image, video, document"
        )
    
    return add_multiple_media_to_health_record(db, record_id, files, parsed_media_types)

@router.get("/pet/{pet_id}", response_model=List[HealthRecordResponse])
def get_records_for_pet(
    pet_id: int,
    skip: int = 0,
    limit: int = 100,
    record_type: Optional[RecordType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get health records for a specific pet.
    
    Optional filters:
    - record_type: Filter by record type (general, vaccination, treatment, weight)
    - start_date: Filter records from this date (format: YYYY-MM-DD)
    - end_date: Filter records until this date (format: YYYY-MM-DD)
    """
    # Verify the user has access to this pet
    verify_pet_ownership(db, current_user.id, pet_id)
    
    return get_pet_health_records(
        db, 
        pet_id, 
        skip, 
        limit, 
        record_type,
        start_date,
        end_date
    )

@router.get("/{record_id}", response_model=HealthRecordResponse)
def get_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific health record.
    """
    health_record = get_health_record_by_id(db, record_id)
    if not health_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health record not found")
    
    verify_pet_ownership(db, current_user.id, health_record.pet_id)
    
    return health_record

@router.put("/{record_id}", response_model=HealthRecordResponse)
def update_record(
    record_id: int,
    record_data: HealthRecordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a health record.
    """
    health_record = get_health_record_by_id(db, record_id)
    if not health_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health record not found")
    
    verify_pet_ownership(db, current_user.id, health_record.pet_id)
    
    updated_record = update_health_record(db, record_id, record_data)
    return updated_record

@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a health record.
    """
    health_record = get_health_record_by_id(db, record_id)
    if not health_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health record not found")
    
    verify_pet_ownership(db, current_user.id, health_record.pet_id)
    
    delete_health_record(db, record_id)
    return None

@router.delete("/{record_id}/media/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_media(
    record_id: int,
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete media (image, video, document) from a health record.
    """
    # Check if health record exists
    health_record = get_health_record_by_id(db, record_id)
    if not health_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health record not found")
    
    # Check if current user has access to this pet
    verify_pet_ownership(db, current_user.id, health_record.pet_id)
    
    # Check if media exists and belongs to this health record
    media = get_media_by_id(db, media_id)
    if not media or media.health_record_id != record_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Media not found or doesn't belong to this health record"
        )
    
    # Delete media
    delete_health_record_media(db, media_id)
    return None

@router.get("/{record_id}/media", response_model=List[HealthRecordMediaResponse])
def get_media_list(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all media items for a health record.
    """
    # Check if health record exists
    health_record = get_health_record_by_id(db, record_id)
    if not health_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health record not found")
    
    # Check if current user has access to this pet
    verify_pet_ownership(db, current_user.id, health_record.pet_id)
    
    # Return media items
    return get_media_for_health_record(db, record_id)
