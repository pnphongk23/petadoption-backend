from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func

from app.db.session import Base

class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code = Column(String(6), nullable=False)  # 6-chữ số OTP
    purpose = Column(String(50), nullable=False)  # 'registration', 'password_reset', 'login_verification'
    channel = Column(String(20), nullable=False)  # 'sms' hoặc 'email'
    is_verified = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<OTP for user_id={self.user_id}, purpose={self.purpose}>"
