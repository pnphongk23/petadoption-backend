from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from collections import defaultdict

from app.models.health_record import HealthRecord, RecordType
from app.models.pet import Pet

def get_weight_history(
    db: Session,
    pet_id: int,
    limit: int = 10
) -> List[Tuple[datetime, float]]:
    """
    Get weight history for a pet
    
    Args:
        db: Database session
        pet_id: ID of the pet
        limit: Maximum number of records to return
        
    Returns:
        List of (date, weight) tuples
    """
    weight_records = db.query(
        HealthRecord.record_date, 
        HealthRecord.weight
    ).filter(
        HealthRecord.pet_id == pet_id,
        HealthRecord.record_type == RecordType.WEIGHT,
        HealthRecord.weight.isnot(None)
    ).order_by(
        HealthRecord.record_date.desc()
    ).limit(limit).all()
    
    # Reverse to get chronological order
    return list(reversed(weight_records))

def get_health_record_summary(
    db: Session,
    pet_id: int
) -> Dict:
    """
    Get summary statistics for a pet's health records
    
    Args:
        db: Database session
        pet_id: ID of the pet
        
    Returns:
        Dictionary containing summary statistics
    """
    # Get total counts by record type
    record_counts = db.query(
        HealthRecord.record_type,
        func.count(HealthRecord.id)
    ).filter(
        HealthRecord.pet_id == pet_id
    ).group_by(
        HealthRecord.record_type
    ).all()
    
    # Convert to dictionary
    count_dict = {record_type: count for record_type, count in record_counts}
    
    # Get latest weight if available
    latest_weight = db.query(HealthRecord.weight).filter(
        HealthRecord.pet_id == pet_id,
        HealthRecord.record_type == RecordType.WEIGHT,
        HealthRecord.weight.isnot(None)
    ).order_by(
        HealthRecord.record_date.desc()
    ).first()
    
    # Get upcoming reminders
    upcoming_reminders = db.query(HealthRecord).filter(
        HealthRecord.pet_id == pet_id,
        HealthRecord.next_reminder_date.isnot(None),
        HealthRecord.next_reminder_date > datetime.now()
    ).order_by(
        HealthRecord.next_reminder_date
    ).limit(3).all()
    
    # Get most recent records
    recent_records = db.query(HealthRecord).filter(
        HealthRecord.pet_id == pet_id
    ).order_by(
        HealthRecord.record_date.desc()
    ).limit(5).all()
    
    # Compile summary
    summary = {
        "total_records": sum(count_dict.values()),
        "record_counts": count_dict,
        "latest_weight": latest_weight[0] if latest_weight else None,
        "upcoming_reminders": upcoming_reminders,
        "recent_records": recent_records
    }
    
    return summary

def get_vaccination_status(
    db: Session,
    pet_id: int
) -> Dict:
    """
    Get vaccination status for a pet
    
    Args:
        db: Database session
        pet_id: ID of the pet
        
    Returns:
        Dictionary containing vaccination information
    """
    # Get vaccination records
    vaccination_records = db.query(HealthRecord).filter(
        HealthRecord.pet_id == pet_id,
        HealthRecord.record_type == RecordType.VACCINATION
    ).order_by(
        HealthRecord.record_date.desc()
    ).all()
    
    # Check if pet exists
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        return {
            "pet_exists": False,
            "vaccinations": []
        }
    
    # Process vaccination records to extract vaccine names and dates
    vaccinations = []
    for record in vaccination_records:
        # Extract vaccine name from notes
        vaccine_name = None
        if record.notes and "Vaccination:" in record.notes:
            vaccine_name = record.notes.split("Vaccination:")[1].strip().split("\n")[0]
        
        vaccinations.append({
            "id": record.id,
            "date": record.record_date,
            "vaccine_name": vaccine_name or "Unknown vaccine",
            "next_due_date": record.next_reminder_date,
            "notes": record.notes
        })
    
    return {
        "pet_exists": True,
        "pet_name": pet.name,
        "vaccinations": vaccinations
    }
