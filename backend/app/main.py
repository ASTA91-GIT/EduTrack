from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, get_db
from . import models
from .routes import users, attendance, auth
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Parse CORS origins from environment variable
cors_origins = os.getenv("BACKEND_CORS_ORIGINS", "[\"http://localhost:8080\",\"http://localhost:3000\"]")
try:
    import json
    cors_origins = json.loads(cors_origins)
except:
    cors_origins = ["http://localhost:8080", "http://localhost:3000"]

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="EduTrack API", description="API for Automated Attendance System", version="1.0.0")

# CORS middleware with improved security using environment variables
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # Use origins from environment variable
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Restrict to specific methods
    allow_headers=["Content-Type", "Authorization", "Accept"],  # Restrict to specific headers
    expose_headers=["Content-Length"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])

@app.get("/")
def read_root():
    return {"message": "Welcome to EduTrack API"}

@app.get("/api/health")
def health_check(db=Depends(get_db)):
    return {"status": "healthy", "database": "connected"}