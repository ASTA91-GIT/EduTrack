from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String(36), unique=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True)
    full_name = Column(String(255))
    hashed_password = Column(String(255))
    role = Column(String(50), default="student")  # student, teacher, admin
    face_encoding = Column(JSON, nullable=True)  # Store facial encoding
    profile_image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    type = Column(String(50))  # check_in, check_out, lecture
    method = Column(String(50), default="facial_recognition")
    confidence_score = Column(Float, nullable=True)
    location = Column(String(255), nullable=True)
    capture_image_url = Column(String(500), nullable=True)
    status = Column(String(50), default="present")  # present, late, absent
    created_at = Column(DateTime, default=datetime.utcnow)