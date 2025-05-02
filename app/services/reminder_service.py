from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from app.models.health_record import HealthRecord, RecordType
from app.models.user import User

def get_upcoming_reminders(
    db: Session, 
    user_id: int, 
    days_ahead: int = 7
) -> List[HealthRecord]:
    """
    Get upcoming reminders for a user's pets within the specified time period.
    
    Args:
        db: Database session
        user_id: ID of the user
        days_ahead: Number of days ahead to check for reminders (default: 7 days)
        
    Returns:
        List of health records with upcoming reminders
    """
    # Calculate the date range
    now = datetime.now()
    end_date = now + timedelta(days=days_ahead)
    
    # Query health records with reminders in the date range
    records = db.query(HealthRecord).join(
        HealthRecord.pet
    ).filter(
        HealthRecord.next_reminder_date.between(now, end_date),
        HealthRecord.pet.has(user_id=user_id)  # Filter by pets owned by the user
    ).order_by(
        HealthRecord.next_reminder_date
    ).all()
    
    return records

def create_vaccination_reminder(
    db: Session,
    pet_id: int,
    user_id: int,
    vaccine_name: str,
    reminder_date: datetime,
    notes: Optional[str] = None
) -> HealthRecord:
    """
    Create a vaccination reminder for a pet
    
    Args:
        db: Database session
        pet_id: ID of the pet
        user_id: ID of the user creating the reminder
        vaccine_name: Name of the vaccine
        reminder_date: Date when the reminder should be triggered
        notes: Additional notes
        
    Returns:
        Created health record with reminder
    """
    reminder_notes = f"Vaccination reminder: {vaccine_name}"
    if notes:
        reminder_notes += f"\n{notes}"
        
    record = HealthRecord(
        pet_id=pet_id,
        user_id=user_id,
        record_type=RecordType.VACCINATION,
        notes=reminder_notes,
        next_reminder_date=reminder_date
    )
    
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
