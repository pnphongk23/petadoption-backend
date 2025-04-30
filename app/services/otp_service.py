import random
import string
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.otp import OTP
from app.schemas.otp import OTPRequest, OTPResponse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

# Thời gian hết hạn của OTP (phút)
OTP_EXPIRY_MINUTES = 10

def generate_otp() -> str:
    """Tạo mã OTP 6 chữ số ngẫu nhiên"""
    return ''.join(random.choices(string.digits, k=6))

def create_otp(db: Session, user_id: int, purpose: str, channel: str) -> OTP:
    """
    Tạo một mã OTP mới cho người dùng.
    Nếu đã tồn tại OTP chưa xác thực, sẽ vô hiệu hóa và tạo mã mới.
    """
    # Vô hiệu hóa các OTP cũ cùng mục đích và kênh
    db.query(OTP).filter(
        OTP.user_id == user_id,
        OTP.purpose == purpose,
        OTP.channel == channel,
        OTP.is_verified == False,
        OTP.expires_at > datetime.utcnow()
    ).update({
        "expires_at": datetime.utcnow()
    })
    
    # Tạo OTP mới
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    otp_code = generate_otp()
    
    otp = OTP(
        user_id=user_id,
        code=otp_code,
        purpose=purpose,
        channel=channel,
        is_verified=False,
        expires_at=expires_at
    )
    
    db.add(otp)
    db.commit()
    db.refresh(otp)
    
    return otp

def verify_otp(db: Session, user_id: int, code: str, purpose: str) -> bool:
    """Xác thực mã OTP của người dùng"""
    otp = db.query(OTP).filter(
        OTP.user_id == user_id,
        OTP.code == code,
        OTP.purpose == purpose,
        OTP.is_verified == False,
        OTP.expires_at > datetime.utcnow()
    ).first()
    
    if not otp:
        return False
    
    # Đánh dấu OTP đã được xác thực
    otp.is_verified = True
    db.commit()
    
    return True

def send_otp_via_email(email: str, otp: str) -> bool:
    """Gửi mã OTP qua email"""
    try:
        # Tạo nội dung email
        message = MIMEMultipart()
        message["From"] = settings.MAIL_FROM
        message["To"] = email
        message["Subject"] = "Mã xác thực Hanoi Pet Adoption"
        
        body = f"""
        <html>
        <body>
            <h2>Xin chào từ Hanoi Pet Adoption!</h2>
            <p>Mã xác thực của bạn là: <strong>{otp}</strong></p>
            <p>Mã này sẽ hết hạn sau {OTP_EXPIRY_MINUTES} phút.</p>
            <p>Nếu bạn không yêu cầu mã này, vui lòng bỏ qua email này.</p>
        </body>
        </html>
        """
        
        message.attach(MIMEText(body, "html"))
        
        # Thiết lập kết nối SMTP
        with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
            if settings.MAIL_TLS:
                server.starttls()
            
            if settings.MAIL_USERNAME and settings.MAIL_PASSWORD:
                server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            
            server.send_message(message)
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_otp_via_sms(phone_number: str, otp: str) -> bool:
    """
    Gửi mã OTP qua SMS
    
    Ghi chú: Đây là hàm giả định - trong môi trường thực tế, 
    bạn sẽ tích hợp với một nhà cung cấp dịch vụ SMS như Twilio, Vonage, v.v.
    """
    try:
        # Đây là dữ liệu mô phỏng cho việc gửi SMS
        print(f"[MOCK SMS] To: {phone_number}, Message: Your Hanoi Pet Adoption verification code is: {otp}")
        
        # Trong thực tế, bạn sẽ sử dụng API của nhà cung cấp dịch vụ SMS, ví dụ:
        # import twilio
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(
        #    body=f"Your Hanoi Pet Adoption verification code is: {otp}",
        #    from_="YOUR_TWILIO_NUMBER",
        #    to=phone_number
        # )
        
        return True
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False

def send_otp(db: Session, user: User, channel: str, purpose: str) -> Optional[OTPResponse]:
    """
    Tạo và gửi mã OTP cho người dùng thông qua kênh chỉ định
    """
    try:
        # Tạo OTP mới
        otp_record = create_otp(db, user.id, purpose, channel)
        
        # Gửi OTP qua kênh thích hợp
        sent_successfully = False
        
        if channel == "email" and user.email:
            sent_successfully = send_otp_via_email(user.email, otp_record.code)
        elif channel == "sms" and user.phone_number:
            sent_successfully = send_otp_via_sms(user.phone_number, otp_record.code)
        else:
            return OTPResponse(
                success=False,
                message=f"Không thể gửi OTP: {channel} không hợp lệ hoặc thiếu thông tin người dùng",
                expires_in=0
            )
            
        if sent_successfully:
            # Tính thời gian còn lại tính bằng giây
            expires_in = int((otp_record.expires_at - datetime.utcnow()).total_seconds())
            
            return OTPResponse(
                success=True,
                message=f"Mã xác thực đã được gửi qua {channel}",
                expires_in=expires_in
            )
        else:
            return OTPResponse(
                success=False,
                message=f"Không thể gửi mã xác thực qua {channel}",
                expires_in=0
            )
    
    except Exception as e:
        return OTPResponse(
            success=False,
            message=f"Lỗi khi xử lý OTP: {str(e)}",
            expires_in=0
        )
