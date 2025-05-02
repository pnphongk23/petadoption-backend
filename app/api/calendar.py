from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, date

from app.db.session import get_db
from app.models.user import User
from app.services.calendar_service import get_month_calendar_events
from app.utils.security import get_current_user

router = APIRouter(prefix="/calendar", tags=["Calendar"])

@router.get("/month")
def get_monthly_calendar(
    year: Optional[int] = None,
    month: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a calendar view of health events for a specific month.
    
    Args:
        year: Year to get events for (defaults to current year)
        month: Month to get events for (1-12, defaults to current month)
        
    Returns:
        Calendar with events organized by date
    """
    # Validate month input if provided
    if month is not None and (month < 1 or month > 12):
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    
    # Validate year input if provided (reasonable range)
    current_year = datetime.now().year
    if year is not None and (year < 2020 or year > current_year + 5):
        raise HTTPException(
            status_code=400, 
            detail=f"Year must be between 2020 and {current_year + 5}"
        )
        
    return get_month_calendar_events(db, current_user.id, year, month)
