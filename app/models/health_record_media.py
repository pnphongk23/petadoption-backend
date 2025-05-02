from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.db.base_class import Base

class MediaType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"

class HealthRecordMedia(Base):
    __tablename__ = "health_record_media"
    
    id = Column(Integer, primary_key=True, index=True)
    health_record_id = Column(Integer, ForeignKey("health_records.id"), nullable=False)
    file_path = Column(String, nullable=False)
    media_type = Column(Enum(MediaType), nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    health_record = relationship("HealthRecord", back_populates="media_items")
