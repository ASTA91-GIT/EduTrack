from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, get_db
from . import models
from .routes import users, attendance, auth

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="EduTrack API", description="API for Automated Attendance System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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