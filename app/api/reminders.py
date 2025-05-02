from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.user import User
from app.schemas.health_record import HealthRecordResponse
from app.services.reminder_service import get_upcoming_reminders, create_vaccination_reminder
from app.utils.security import get_current_user
from app.utils.pet_ownership import verify_pet_ownership

router = APIRouter(prefix="/reminders", tags=["Reminders"])

class VaccinationReminderCreate(BaseModel):
    pet_id: int
    vaccine_name: str
    reminder_date: datetime
    notes: Optional[str] = None

@router.get("/upcoming", response_model=List[HealthRecordResponse])
def get_upcoming(
    days_ahead: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all upcoming reminders for the current user's pets in the next X days.
    
    Args:
        days_ahead: Number of days ahead to check for reminders (default: 7 days)
    """
    return get_upcoming_reminders(db, current_user.id, days_ahead)

@router.post("/vaccination", response_model=HealthRecordResponse)
def create_vaccination(
    reminder: VaccinationReminderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a vaccination reminder for a pet.
    """
    # Verify the user has access to this pet
    verify_pet_ownership(db, current_user.id, reminder.pet_id)
    
    return create_vaccination_reminder(
        db,
        reminder.pet_id,
        current_user.id,
        reminder.vaccine_name,
        reminder.reminder_date,
        reminder.notes
    )
