from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

from backend.app.main import app
from backend.app.database import Base, get_db
from backend.app.models import User
from backend.app.auth import get_password_hash

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
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
    
    # Add a test student
    if not db.query(User).filter(User.email == "test@student.com").first():
        user = User(
            name="Test Student",
            email="test@student.com",
            password=get_password_hash("password123"),
            role="student"
        )
        db.add(user)
        db.commit()
    
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.pop(get_db, None)

def test_login_success():
    response = client.post("/api/v1/auth/login/json", json={
        "email": "test@student.com",
        "password": "password123",
        "role": "student"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "student"

def test_login_invalid_password():
    response = client.post("/api/v1/auth/login/json", json={
        "email": "test@student.com",
        "password": "wrongpassword",
        "role": "student"
    })
    assert response.status_code == 401

def test_login_unified_role():
    # Unified login detects actual database role
    response = client.post("/api/v1/auth/login/json", json={
        "email": "test@student.com",
        "password": "password123",
        "role": "teacher"
    })
    assert response.status_code == 200
    assert response.json()["role"] == "student"

