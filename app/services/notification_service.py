from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.health_record import HealthRecord
from app.models.pet import Pet

class NotificationType:
    """Types of notifications"""
    VACCINATION_DUE = "vaccination_due"
    TREATMENT_DUE = "treatment_due"
    HEALTH_REMINDER = "health_reminder"
    WEIGHT_CHECK = "weight_check"

def get_user_notifications(
    db: Session,
    user_id: int,
    days_ahead: int = 7,
    include_read: bool = False
) -> List[Dict[str, Any]]:
    """
    Get all active notifications for a user
    
    Args:
        db: Database session
        user_id: User ID
        days_ahead: Number of days ahead to check for reminders
        include_read: Whether to include already read notifications
        
    Returns:
        List of notification objects with format:
        {
            "id": int,
            "type": str,
            "pet_id": int,
            "pet_name": str, 
            "message": str,
            "due_date": datetime,
            "days_left": int,
            "is_read": bool
        }
    """
    # Get current date and target date
    now = datetime.now()
    target_date = now + timedelta(days=days_ahead)
    
    # Query for health records with reminders in the date range
    upcoming_reminders = db.query(
        HealthRecord, Pet
    ).join(
        Pet, HealthRecord.pet_id == Pet.id
    ).filter(
        Pet.user_id == user_id,
        HealthRecord.next_reminder_date.isnot(None),
        HealthRecord.next_reminder_date >= now,
        HealthRecord.next_reminder_date <= target_date
    ).all()
    
    # Format into notifications
    notifications = []
    
    for record, pet in upcoming_reminders:
        # Calculate days left
        days_left = (record.next_reminder_date - now).days
        
        # Determine notification type based on record type
        notification_type = NotificationType.HEALTH_REMINDER
        if record.record_type == "vaccination":
            notification_type = NotificationType.VACCINATION_DUE
        elif record.record_type == "treatment":
            notification_type = NotificationType.TREATMENT_DUE
        elif record.record_type == "weight":
            notification_type = NotificationType.WEIGHT_CHECK
            
        # Create notification message
        message = f"{record.record_type.capitalize()} reminder for {pet.name}"
        if record.notes and len(record.notes) > 0:
            # Extract first line of notes if available
            first_line = record.notes.split("\n")[0]
            if "Vaccination:" in first_line and notification_type == NotificationType.VACCINATION_DUE:
                vaccine_name = first_line.split("Vaccination:")[1].strip()
                message = f"Vaccination due for {pet.name}: {vaccine_name}"
        
        # Create notification object
        notification = {
            "id": record.id,
            "type": notification_type,
            "pet_id": pet.id,
            "pet_name": pet.name,
            "message": message,
            "due_date": record.next_reminder_date,
            "days_left": days_left,
            "is_read": False  # For future implementation of read/unread status
        }
        
        notifications.append(notification)
    
    # Sort by due date (soonest first)
    notifications.sort(key=lambda n: n["due_date"])
    
    return notifications
