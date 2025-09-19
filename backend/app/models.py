from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON, ForeignKey, Index, Text
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
    
    # Relationships
    profile = relationship("UserProfile", uselist=False, back_populates="user")
    attendance_records = relationship("AttendanceRecord", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    appeals = relationship("Appeal", back_populates="user")
    logs = relationship("Log", back_populates="user")
    password_resets = relationship("PasswordReset", back_populates="user")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_user_email', email),
        Index('idx_user_public_id', public_id),
        Index('idx_user_role', role),
    )

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    phone = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True)
    preferences = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    user = relationship("User", back_populates="profile")

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    type = Column(String(50), nullable=False)  # check_in, check_out, lecture
    method = Column(String(50), default="manual", nullable=False)  # QR, face, manual
    confidence_score = Column(Float, nullable=True)
    location = Column(String(255), nullable=True)
    capture_image_url = Column(String(500), nullable=True)
    status = Column(String(50), default="present", nullable=False)  # present, late, absent
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="attendance_records")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_attendance_user_timestamp', user_id, timestamp),
        Index('idx_attendance_status', status),
    )

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="info", nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    user = relationship("User", back_populates="notifications")

class Appeal(Base):
    __tablename__ = "appeals"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    attendance_id = Column(Integer, ForeignKey("attendance_records.id", ondelete="SET NULL"), nullable=True)
    reason = Column(Text, nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    user = relationship("User", back_populates="appeals")

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    user = relationship("User", back_populates="logs")

class PasswordReset(Base):
    __tablename__ = "password_resets"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    user = relationship("User", back_populates="password_resets")