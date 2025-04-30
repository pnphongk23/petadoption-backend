from typing import Optional, Union
from pydantic import BaseModel, EmailStr, validator, field_validator
from datetime import datetime
import re

# Shared properties
class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = "user"
    
    @field_validator('role')
    def validate_role(cls, v):
        if v not in ["user", "admin", "moderator"]:
            raise ValueError('Role must be one of: user, admin, moderator')
        return v
        
    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if v is not None:
            # Simple regex for international phone number validation
            # Accepts formats like: +84912345678, 84912345678, 0912345678
            pattern = r'^(\+?\d{1,3})?[-\s]?\d{9,15}$'
            if not re.match(pattern, v):
                raise ValueError('Invalid phone number format')
        return v
        
    @field_validator('email', 'phone_number')
    def validate_contact_info(cls, v, info):
        # This validator needs access to the entire model, so we use root_validator in v1
        # In v2, we would use model_validator, but for simplicity, we handle this in the service
        return v

# Properties for receiving via API on creation
class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
        
# Extended user create schema with verification preference
class UserCreateExtended(UserCreate):
    verification_channel: Optional[str] = "email"  # 'email' or 'sms'

# Properties for receiving via API on update
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

# Properties to return via API
class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

# Properties stored in DB
class User(UserResponse):
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

# For authentication
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    role: str

class TokenData(BaseModel):
    email: Optional[str] = None
