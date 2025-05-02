from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.services.notification_service import get_user_notifications
from app.utils.security import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("")
def get_notifications(
    days_ahead: int = Query(7, description="Number of days ahead to check for reminders"),
    include_read: bool = Query(False, description="Whether to include already read notifications"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all active notifications for the current user.
    
    Notifications are generated based on upcoming health reminders for the user's pets.
    """
    return get_user_notifications(db, current_user.id, days_ahead, include_read)
