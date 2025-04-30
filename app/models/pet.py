from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base

class Pet(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # dog, cat, other
    breed = Column(String(100), nullable=True)
    gender = Column(String(20), nullable=True)  # male, female, unknown
    age = Column(Integer, nullable=True)  # age in months
    description = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    status = Column(String(50), default="available")  # available, adopted, fostered, etc.
    details = Column(Text, nullable=True)  # JSON string for additional details
    
    # Foreign key to user (owner/uploader)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Pet {self.name}, {self.type}, {self.status}>"
