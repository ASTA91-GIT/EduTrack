from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

from backend.app.main import app
from backend.app.database import Base, get_db
from backend.app.models import User
from backend.app.auth import get_password_hash

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_api.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Create test users
    admin = User(name="Admin", email="admin@test.com", password=get_password_hash("pass"), role="admin")
    teacher = User(name="Teacher", email="teacher@test.com", password=get_password_hash("pass"), role="teacher")
    student = User(name="Student", email="student@test.com", password=get_password_hash("pass"), role="student")
    
    db.add(admin)
    db.add(teacher)
    db.add(student)
    db.commit()
    
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.pop(get_db, None)

def get_token(email, role):
    response = client.post("/api/v1/auth/login/json", json={
        "email": email,
        "password": "pass",
        "role": role
    })
    if response.status_code != 200:
        print("LOGIN FAILED:", response.json())
        assert False, "Login failed"
    return response.json()["access_token"]

def test_admin_dashboard_access():
    token = get_token("admin@test.com", "admin")
    response = client.get("/api/v1/dashboard/admin", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "total_students" in response.json()

def test_student_dashboard_denied_for_teacher():
    token = get_token("teacher@test.com", "teacher")
    response = client.get("/api/v1/dashboard/student", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403

def test_faculty_create_session():
    token = get_token("teacher@test.com", "teacher")
    response = client.post("/api/v1/attendance_sessions/session", 
                           headers={"Authorization": f"Bearer {token}"},
                           json={"subject": "Math", "class_name": "A", "duration_minutes": 5})
    assert response.status_code == 200
    assert "session_token" in response.json()
