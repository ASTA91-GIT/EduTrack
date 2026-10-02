"""
Centralized Test Configuration for EduTrack
Used exclusively for development, QA, and automated test runs.
NEVER enables security bypasses or production backdoors.
"""

import os

# Environment: 'development' or 'production'
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Dedicated Central Test Student Identity
TEST_STUDENT_ID = os.getenv("EDUTRACK_TEST_STUDENT_ID", "TEST_STUDENT_001")
TEST_STUDENT_EMAIL = os.getenv("EDUTRACK_TEST_STUDENT_EMAIL", "student1@edutrack.local")
TEST_STUDENT_PASSWORD = os.getenv("EDUTRACK_TEST_STUDENT_PASSWORD", "student123")

# Dedicated Central Test Faculty Identity
TEST_FACULTY_EMAIL = os.getenv("EDUTRACK_TEST_FACULTY_EMAIL", "faculty@edutrack.local")
TEST_FACULTY_PASSWORD = os.getenv("EDUTRACK_TEST_FACULTY_PASSWORD", "faculty123")
