from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.db.base_class import Base

class RecordType(str, enum.Enum):
    GENERAL = "general"
    VACCINATION = "vaccination"
    TREATMENT = "treatment"
    WEIGHT = "weight"

class HealthRecord(Base):
    __tablename__ = "health_records"
    
    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    record_type = Column(Enum(RecordType), nullable=False)
    record_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)
    weight = Column(Float, nullable=True)
    next_reminder_date = Column(DateTime, nullable=True)
    
    # Relationships
    pet = relationship("Pet", back_populates="health_records")
    user = relationship("User", back_populates="created_records")
    media_items = relationship("HealthRecordMedia", back_populates="health_record", cascade="all, delete-orphan")
