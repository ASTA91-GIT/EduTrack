"""
Database Seed Script for EduTrack.
Inserts realistic development data into the database.
Usage: python -m backend.scripts.seed
"""
import os
import sys
import datetime
import random
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import logging

# Ensure the backend directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.database import SessionLocal, Base, engine
from backend.app.models import User, AttendanceSession, AttendanceSessionRecord, UserProfile
from backend.app.auth import get_password_hash
from backend.app.services import ATTENDANCE_THRESHOLD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).filter(User.email == "admin@edutrack.edu").first():
            logger.info("Database already seeded. Skipping to avoid duplicates.")
            return

        logger.info("Starting database seed...")

        # Create Admin
        admin = User(
            name="Admin User",
            email="admin@edutrack.edu",
            password=get_password_hash("admin123"),
            role="admin"
        )
        db.add(admin)
        
        # Create Faculty
        faculty_users = []
        for i in range(1, 4):
            faculty = User(
                name=f"Professor {chr(64+i)}",
                email=f"prof{i}@edutrack.edu",
                password=get_password_hash("faculty123"),
                role="teacher"
            )
            db.add(faculty)
            faculty_users.append(faculty)

        # Create Students
        students = []
        for i in range(1, 16):
            student = User(
                name=f"Student {i}",
                email=f"student{i}@edutrack.edu",
                password=get_password_hash("student123"),
                role="student"
            )
            db.add(student)
            students.append(student)

        db.commit()
        
        # Refresh objects to get IDs
        for user in faculty_users + students:
            db.refresh(user)

        # Subjects
        subjects = ["Data Structures", "Database Systems", "Operating Systems", "Computer Networks", "Software Engineering", "Machine Learning"]
        classes = ["CS-A", "CS-B"]

        # Create Attendance Sessions and Records
        now = datetime.datetime.utcnow()
        session_token_counter = 1
        
        # Let's create past sessions for the last 30 days
        for day in range(30, 0, -1):
            session_date = now - datetime.timedelta(days=day)
            
            # 2 sessions per day
            for _ in range(2):
                prof = random.choice(faculty_users)
                subject = random.choice(subjects)
                class_name = random.choice(classes)
                
                session = AttendanceSession(
                    faculty_id=prof.id,
                    subject=subject,
                    class_name=class_name,
                    session_token=f"SEED-{session_token_counter:04d}",
                    expires_at=session_date + datetime.timedelta(hours=1),
                    status="closed",
                    created_at=session_date
                )
                db.add(session)
                db.flush() # get session.id
                session_token_counter += 1
                
                # Determine attendance for this session (e.g. 70-95% attendance rate)
                for student in students:
                    # Randomize attendance. Some students are better, some are worse.
                    # Base probability depending on student id to create variance.
                    base_prob = 0.5 + (student.id % 5) * 0.1 # 0.5 to 0.9
                    if random.random() < base_prob:
                        record = AttendanceSessionRecord(
                            session_id=session.id,
                            student_id=student.id,
                            marked_at=session_date + datetime.timedelta(minutes=random.randint(1, 10))
                        )
                        db.add(record)

        # Active session
        prof = faculty_users[0]
        active_session = AttendanceSession(
            faculty_id=prof.id,
            subject="Machine Learning",
            class_name="CS-A",
            session_token=f"SEED-{session_token_counter:04d}",
            expires_at=now + datetime.timedelta(minutes=30),
            status="active",
            created_at=now
        )
        db.add(active_session)

        db.commit()
        logger.info("Database seeding completed successfully.")

    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
