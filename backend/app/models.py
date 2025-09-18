from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    public_id = Column(String(36), unique=True, default=generate_uuid, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)  # Changed from full_name to match auth implementation
    password = Column(String(255), nullable=False)  # Changed from hashed_password to match auth implementation
    role = Column(String(50), default="student", nullable=False)  # student, teacher, admin
    face_encoding = Column(JSON, nullable=True)  # Store facial encoding
    profile_image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_user_email', email),
        Index('idx_user_public_id', public_id),
        Index('idx_user_role', role),
    )

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    type = Column(String(50), nullable=False)  # check_in, check_out, lecture
    method = Column(String(50), default="facial_recognition", nullable=False)
    confidence_score = Column(Float, nullable=True)
    location = Column(String(255), nullable=True)
    capture_image_url = Column(String(500), nullable=True)
    status = Column(String(50), default="present", nullable=False)  # present, late, absent
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", backref="attendance_records")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_attendance_user_timestamp', user_id, timestamp),
        Index('idx_attendance_status', status),
    )