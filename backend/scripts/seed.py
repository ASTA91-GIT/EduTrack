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
from backend.app.models import User, AttendanceSession, AttendanceSessionRecord, Timetable, Lecture, Event, Resource
from backend.app.auth import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).filter(User.email == "admin@edutrack.local").first():
            logger.info("Database already seeded. Skipping to avoid duplicates.")
            return

        logger.info("Starting database seed...")

        # Create Admin
        admin = User(
            name="Admin User",
            email="admin@edutrack.local",
            password=get_password_hash("admin123"),
            role="admin"
        )
        db.add(admin)
        
        # Create Primary Faculty (requested by user)
        primary_faculty = User(
            name="Primary Faculty",
            email="faculty@edutrack.local",
            password=get_password_hash("faculty123"),
            role="teacher"
        )
        db.add(primary_faculty)

        # Create Other Faculty
        faculty_users = [primary_faculty]
        for i in range(1, 3):
            faculty = User(
                name=f"Professor {chr(64+i)}",
                email=f"prof{i}@edutrack.local",
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
                email=f"student{i}@edutrack.local",
                password=get_password_hash("student123"),
                role="student"
            )
            db.add(student)
            students.append(student)

        db.commit()
        
        # Refresh objects to get IDs
        db.refresh(admin)
        for user in faculty_users + students:
            db.refresh(user)

        # Subjects
        subjects = ["Data Structures", "Database Systems", "Operating Systems", "Computer Networks", "Software Engineering", "Machine Learning"]
        classes = ["CS-A", "CS-B"]

        # Seed Timetable
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        for day in days:
            db.add(Timetable(day=day, start_time="09:00", end_time="10:00", subject="Data Structures", class_name="CS-A", room="Room 301", faculty_id=primary_faculty.id))
            db.add(Timetable(day=day, start_time="10:00", end_time="11:00", subject="Database Systems", class_name="CS-A", room="Room 302", faculty_id=faculty_users[1].id))
            db.add(Timetable(day=day, start_time="11:30", end_time="12:30", subject="Machine Learning", class_name="CS-B", room="Lab 1", faculty_id=primary_faculty.id))

        # Seed Lectures
        now = datetime.datetime.utcnow()
        for i in range(5):
            db.add(Lecture(
                title=f"Lecture {i+1}: Advanced Concepts",
                subject="Machine Learning",
                faculty_id=primary_faculty.id,
                class_name="CS-A",
                lecture_date=now + datetime.timedelta(days=i),
                description="Please read chapters 4-5 before attending."
            ))

        # Seed Events
        db.add(Event(title="Hackathon 2026", description="Annual 48-hour coding marathon", event_date=now + datetime.timedelta(days=7)))
        db.add(Event(title="Guest Lecture: AI Trends", description="Industry experts discuss the future of AI", event_date=now + datetime.timedelta(days=14)))

        # Seed Resources
        db.add(Resource(title="Machine Learning Syllabus", author="Faculty Board", subject="Machine Learning", uploader_id=primary_faculty.id, file_path="/fake/path/ml_syllabus.pdf", file_type="pdf"))
        db.add(Resource(title="Database Design Patterns", author="O'Reilly", subject="Database Systems", uploader_id=faculty_users[1].id, file_path="/fake/path/db_patterns.pdf", file_type="pdf"))

        # Create Attendance Sessions and Records
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
                    session_token=f"SEED-{session_token_counter:04d}-{random.randint(1000, 9999)}",
                    expires_at=session_date + datetime.timedelta(hours=1),
                    status="closed",
                    created_at=session_date
                )
                db.add(session)
                db.flush() # get session.id
                session_token_counter += 1
                
                # Determine attendance for this session (e.g. 70-95% attendance rate)
                for student in students:
                    base_prob = 0.5 + (student.id % 5) * 0.1 # 0.5 to 0.9
                    if random.random() < base_prob:
                        record = AttendanceSessionRecord(
                            session_id=session.id,
                            student_id=student.id,
                            marked_at=session_date + datetime.timedelta(minutes=random.randint(1, 10))
                        )
                        db.add(record)

        db.commit()
        logger.info("Database seeding completed successfully.")

    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
