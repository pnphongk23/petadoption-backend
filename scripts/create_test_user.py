"""
Tạo tài khoản test cho hệ thống Hanoi Pet Adoption.
Chạy script này để tạo nhanh tài khoản test mà không cần thông qua API.
"""
import sys
import os

# Thêm thư mục gốc vào sys.path để import các modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.user_service import create_user
from app.schemas.user import UserCreate

def create_test_account():
    """Tạo tài khoản test với thông tin mặc định"""
    print("Đang tạo tài khoản test...")
    
    # Khởi tạo session để tương tác với database
    db = SessionLocal()
    try:
        # Tạo đối tượng user data
        user_data = UserCreate(
            username="user1",
            email="user1@gmail.com",
            password="12345678",  # Mật khẩu đơn giản cho tài khoản test
            full_name="Test User",
            role="user"
        )
        
        # Tạo tài khoản
        user = create_user(db, user_data)
        
        print(f"Đã tạo thành công tài khoản test:")
        print(f"- Username: {user.username}")
        print(f"- Email: {user.email}")
        print(f"- Password: 12345678")
        print(f"- Role: {user.role}")
        
    except ValueError as e:
        print(f"Lỗi: {str(e)}")
        print("Tài khoản có thể đã tồn tại, hãy kiểm tra database hoặc sử dụng thông tin khác.")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_account()
