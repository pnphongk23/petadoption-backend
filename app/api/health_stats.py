from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.schemas.health_record import HealthRecordResponse
from app.services.health_stats_service import (
    get_weight_history,
    get_health_record_summary,
    get_vaccination_status
)
from app.utils.security import get_current_user
from app.utils.pet_ownership import verify_pet_ownership

router = APIRouter(prefix="/health-stats", tags=["Health Statistics"])

@router.get("/pet/{pet_id}/weight-history")
def get_pet_weight_history(
    pet_id: int,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get weight history for a pet.
    
    Args:
        pet_id: ID of the pet
        limit: Maximum number of records to return (default: 10)
    """
    # Verify the user has access to this pet
    verify_pet_ownership(db, current_user.id, pet_id)
    
    weight_history = get_weight_history(db, pet_id, limit)
    
    # Format the response
    result = []
    for date, weight in weight_history:
        result.append({
            "date": date,
            "weight": weight
        })
        
    return result

@router.get("/pet/{pet_id}/summary")
def get_pet_health_summary(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for a pet's health records.
    """
    # Verify the user has access to this pet
    verify_pet_ownership(db, current_user.id, pet_id)
    
    summary = get_health_record_summary(db, pet_id)
    
    # Format the response to be JSON serializable
    return {
        "total_records": summary["total_records"],
        "record_counts": summary["record_counts"],
        "latest_weight": summary["latest_weight"],
        "upcoming_reminders": [
            HealthRecordResponse.from_orm(reminder) 
            for reminder in summary["upcoming_reminders"]
        ],
        "recent_records": [
            HealthRecordResponse.from_orm(record) 
            for record in summary["recent_records"]
        ]
    }

@router.get("/pet/{pet_id}/vaccination-status")
def get_pet_vaccination_status(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get vaccination status for a pet.
    """
    # Verify the user has access to this pet
    verify_pet_ownership(db, current_user.id, pet_id)
    
    return get_vaccination_status(db, pet_id)
