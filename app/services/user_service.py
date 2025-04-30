from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import get_password_hash, verify_password

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()

def get_user_by_phone(db: Session, phone_number: str) -> Optional[User]:
    """Get user by phone number."""
    return db.query(User).filter(User.phone_number == phone_number).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get list of users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user_data: UserCreate, is_active: bool = True) -> User:
    """Create a new user."""
    # Kiểm tra xem ít nhất email hoặc số điện thoại phải được cung cấp
    if not user_data.email and not user_data.phone_number:
        raise ValueError("At least email or phone number must be provided")

    # Check if email, phone number, or username already exists
    if user_data.email and get_user_by_email(db, user_data.email):
        raise ValueError("Email already registered")
    if user_data.phone_number and get_user_by_phone(db, user_data.phone_number):
        raise ValueError("Phone number already registered")
    if get_user_by_username(db, user_data.username):
        raise ValueError("Username already taken")
    
    # Create user object with hashed password
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        phone_number=user_data.phone_number,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        is_active=is_active  # Cho phép tạo user không active cho việc xác thực OTP
    )
    
    # Add to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
    """Update user information."""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    # Update user fields if provided in the request
    update_data = user_data.dict(exclude_unset=True)
    
    # Hash password if it's being updated
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]
    
    # Update user object
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username_or_email_or_phone: str, password: str) -> Optional[User]:
    """Authenticate user by username, email, or phone number and password."""
    # Check if input is email, phone number, or username
    if "@" in username_or_email_or_phone:
        # Đăng nhập bằng email
        user = get_user_by_email(db, username_or_email_or_phone)
    elif username_or_email_or_phone.replace('+', '').isdigit() or (username_or_email_or_phone.startswith('+') and username_or_email_or_phone[1:].isdigit()):
        # Đăng nhập bằng số điện thoại (cả có và không có dấu +)
        user = get_user_by_phone(db, username_or_email_or_phone)
    else:
        # Đăng nhập bằng username
        user = get_user_by_username(db, username_or_email_or_phone)
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user

def deactivate_user(db: Session, user_id: int) -> Optional[User]:
    """Deactivate a user (soft delete)."""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    db_user.is_active = False
    db.commit()
    db.refresh(db_user)
    return db_user
