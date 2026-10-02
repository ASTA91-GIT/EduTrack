#!/usr/bin/env python
"""
Development-Only Script: Reset TEST_STUDENT_001 attendance test data.
Safety checks:
1. Verifies ENVIRONMENT != 'production'
2. Targets ONLY records associated with TEST_STUDENT_001 (or student1@edutrack.local)
3. Never deletes user accounts or production data
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import SessionLocal
from backend.app.models import User, AttendanceSessionRecord
from backend.app.test_config import ENVIRONMENT, TEST_STUDENT_ID, TEST_STUDENT_EMAIL

def reset_test_student_records():
    if ENVIRONMENT == "production":
        print("ERROR: Test data reset is strictly prohibited in PRODUCTION environment.")
        sys.exit(1)

    db = SessionLocal()
    try:
        # Find test student user
        test_student = (
            db.query(User)
            .filter((User.public_id == TEST_STUDENT_ID) | (User.email == TEST_STUDENT_EMAIL))
            .first()
        )

        if not test_student:
            print(f"Notice: Test student '{TEST_STUDENT_ID}' not found in database. Nothing to clean.")
            return

        # Count records before deletion
        records_query = db.query(AttendanceSessionRecord).filter(
            AttendanceSessionRecord.student_id == test_student.id
        )
        count = records_query.count()

        if count == 0:
            print(f"Zero attendance records found for test student '{TEST_STUDENT_ID}'. Clean slate ready.")
            return

        # Safely remove only TEST_STUDENT_001 attendance session records
        deleted = records_query.delete(synchronize_session=False)
        db.commit()

        print(f"SUCCESS: Removed {deleted} test attendance record(s) for '{TEST_STUDENT_ID}' ({test_student.email}).")
        print("Production users and general database records remain untouched.")
    except Exception as e:
        db.rollback()
        print(f"Failed to reset test student data: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    reset_test_student_records()
