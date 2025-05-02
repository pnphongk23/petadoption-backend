from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from calendar import monthrange
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models.health_record import HealthRecord, RecordType

def get_month_calendar_events(
    db: Session,
    user_id: int,
    year: int = None,
    month: int = None
) -> Dict[str, Any]:
    """
    Get a calendar view of health events for a specific month
    
    Args:
        db: Database session
        user_id: User ID for filtering pet access
        year: Year to get events for (defaults to current year)
        month: Month to get events for (defaults to current month)
        
    Returns:
        Dictionary with calendar events organized by date
    """
    # Use current month if not specified
    today = date.today()
    year = year or today.year
    month = month or today.month
    
    # Get first and last day of the month
    first_day = date(year, month, 1)
    _, last_day_num = monthrange(year, month)
    last_day = date(year, month, last_day_num)
    
    # Convert to datetime for database queries
    start_date = datetime.combine(first_day, datetime.min.time())
    end_date = datetime.combine(last_day, datetime.max.time())
    
    # Query for records with events during the month
    # This includes both record dates and reminder dates
    records = db.query(HealthRecord).join(
        HealthRecord.pet
    ).filter(
        HealthRecord.pet.has(user_id=user_id),
        or_(
            and_(
                HealthRecord.record_date >= start_date,
                HealthRecord.record_date <= end_date
            ),
            and_(
                HealthRecord.next_reminder_date.isnot(None),
                HealthRecord.next_reminder_date >= start_date,
                HealthRecord.next_reminder_date <= end_date
            )
        )
    ).all()
    
    # Organize events by date
    calendar_data = {
        "year": year,
        "month": month,
        "days": {}
    }
    
    # Add record dates to calendar
    for record in records:
        # Check if the record date is within our month
        if record.record_date.year == year and record.record_date.month == month:
            day = record.record_date.day
            
            if day not in calendar_data["days"]:
                calendar_data["days"][day] = []
                
            calendar_data["days"][day].append({
                "id": record.id,
                "pet_id": record.pet_id,
                "type": "record",
                "event_type": record.record_type,
                "date": record.record_date,
                "title": f"{record.record_type.capitalize()} record"
            })
        
        # Check if reminder date is within our month
        if (record.next_reminder_date and 
            record.next_reminder_date.year == year and 
            record.next_reminder_date.month == month):
            
            reminder_day = record.next_reminder_date.day
            
            if reminder_day not in calendar_data["days"]:
                calendar_data["days"][reminder_day] = []
                
            calendar_data["days"][reminder_day].append({
                "id": record.id,
                "pet_id": record.pet_id,
                "type": "reminder",
                "event_type": record.record_type,
                "date": record.next_reminder_date,
                "title": f"Reminder: {record.record_type.capitalize()}"
            })
    
    return calendar_data
