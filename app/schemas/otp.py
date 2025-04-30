from typing import Optional
from pydantic import BaseModel, constr
from datetime import datetime

# Schema cho việc gửi OTP
class OTPRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None 
    phone_number: Optional[str] = None
    channel: str  # 'sms' or 'email'

# Schema cho việc xác thực OTP
class OTPVerify(BaseModel):
    username: str
    code: constr(min_length=6, max_length=6)  # 6-chữ số OTP

# Schema cho response khi gửi OTP
class OTPResponse(BaseModel):
    success: bool
    message: str
    expires_in: int  # thời gian hết hạn tính bằng giây
    
class OTPInDB(BaseModel):
    id: int
    user_id: int
    code: str
    purpose: str
    channel: str
    is_verified: bool
    expires_at: datetime
    created_at: datetime
    
    class Config:
        orm_mode = True
