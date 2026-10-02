from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON, ForeignKey, Index, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .database import Base

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

# Attendance Session models
class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"
    id = Column(Integer, primary_key=True)
    faculty_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject = Column(String(255), nullable=False)  # could be FK to subjects
    class_name = Column(String(255), nullable=False)  # could be FK to classes
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    status = Column(String(50), default="active", nullable=False)  # active, closed
    
    # Geofence & QR Fields
    classroom_name = Column(String(100), default="Room 101", nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    geofence_radius = Column(Float, default=30.0, nullable=True)
    current_qr_token = Column(String(255), nullable=True)

    # EduPulse Fields
    verification_mode = Column(String(50), default="qr", nullable=False) # edupulse, qr, manual
    pulse_nonce = Column(String(255), nullable=True)
    challenge_seed = Column(String(255), nullable=True)
    challenge_interval = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    closed_at = Column(DateTime, nullable=True)
    # Relationships
    faculty = relationship("User", backref="attendance_sessions")
    __table_args__ = (
        Index('idx_attendance_session_token', 'session_token'),
    )

class AttendanceSessionRecord(Base):
    __tablename__ = "attendance_session_records"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("attendance_sessions.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    marked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Geofence validation fields
    student_lat = Column(Float, nullable=True)
    student_lon = Column(Float, nullable=True)
    distance_meters = Column(Float, nullable=True)
    gps_accuracy = Column(Float, nullable=True)

    # EduPulse Fields
    verification_method = Column(String(50), default="qr_gps", nullable=False)
    verification_latency = Column(Float, nullable=True)
    challenge_verified = Column(Boolean, default=False, nullable=False)
    pulse_verified = Column(Boolean, default=False, nullable=False)
    confidence_score = Column(Float, nullable=True)
    status = Column(String(50), default="present", nullable=False) # present, late, manual
    
    __table_args__ = (
        Index('uq_student_session', 'student_id', 'session_id', unique=True),
    )
    # Relationships
    session = relationship("AttendanceSession", backref="records")
    student = relationship("User", backref="attendance_session_records")

# Academic Models (Tests, Grades, Assignments, Events)
class Test(Base):
    __tablename__ = "tests"
    id = Column(Integer, primary_key=True)
    faculty_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    max_score = Column(Float, nullable=False)
    test_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    faculty = relationship("User", backref="created_tests")

class TestScore(Base):
    __tablename__ = "test_scores"
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, nullable=False)
    
    test = relationship("Test", backref="scores")
    student = relationship("User", backref="test_scores")
    __table_args__ = (
        Index('uq_student_test', 'student_id', 'test_id', unique=True),
    )

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    event_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True)
    faculty_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    due_date = Column(DateTime, nullable=False)
    
    faculty = relationship("User", backref="created_assignments")

class Timetable(Base):
    __tablename__ = "timetables"
    id = Column(Integer, primary_key=True)
    day = Column(String(20), nullable=False)
    start_time = Column(String(10), nullable=False)
    end_time = Column(String(10), nullable=False)
    subject = Column(String(255), nullable=False)
    faculty_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    class_name = Column(String(255), nullable=False)
    room = Column(String(100), nullable=True)
    
    faculty = relationship("User", backref="timetables")

class Lecture(Base):
    __tablename__ = "lectures"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    faculty_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    class_name = Column(String(255), nullable=False)
    lecture_date = Column(DateTime, nullable=False)
    description = Column(Text, nullable=True)
    
    faculty = relationship("User", backref="lectures")

class Resource(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=True)
    subject = Column(String(255), nullable=False)
    uploader_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    uploader = relationship("User", backref="uploaded_resources")
