from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .database import engine, get_db
from . import models
from .routes import users, auth
import os
from dotenv import load_dotenv
import time

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

# Simple in-memory rate limiting (per IP, per window)
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW_SEC = int(os.getenv("RATE_LIMIT_WINDOW_SEC", "60"))
_rate_store = {}

@app.middleware("http")
async def error_and_rate_middleware(request: Request, call_next):
    try:
        # Rate limit
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = int(now // RATE_LIMIT_WINDOW_SEC)
        key = f"{ip}:{window}"
        count = _rate_store.get(key, 0)
        if count >= RATE_LIMIT_REQUESTS:
            return JSONResponse(status_code=429, content={"detail": "Too Many Requests"})
        _rate_store[key] = count + 1

        response = await call_next(request)
        return response
    except Exception as exc:
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

# Include routers with API versioning
API_V1_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=f"{API_V1_PREFIX}/auth", tags=["Authentication"])
# users router kept under v1 for consistency if exists
try:
    app.include_router(users.router, prefix=f"{API_V1_PREFIX}/users", tags=["Users"])
except Exception:
    pass

# Placeholder includes for new route modules if present
try:
    from .routes import notifications, reports, attendance, students, appeals
    app.include_router(attendance.router, prefix=f"{API_V1_PREFIX}/attendance", tags=["Attendance"])
    app.include_router(notifications.router, prefix=f"{API_V1_PREFIX}/notifications", tags=["Notifications"])
    app.include_router(reports.router, prefix=f"{API_V1_PREFIX}/reports", tags=["Reports"])
    app.include_router(students.router, prefix=f"{API_V1_PREFIX}/students", tags=["Students"])
    app.include_router(appeals.router, prefix=f"{API_V1_PREFIX}/appeals", tags=["Appeals"])
except Exception:
    pass

@app.get("/")
def read_root():
    return {"message": "Welcome to EduTrack API"}

@app.get(f"{API_V1_PREFIX}/health")
def health_check(db=Depends(get_db)):
    return {"status": "healthy", "database": "connected"}