from fastapi import FastAPI
from .routes import attendance
from .database import engine
from .models import Base

# Initialize FastAPI app
app = FastAPI(title="EduTrack API")

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(attendance.router)