from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from .database import engine, get_db, Base
from . import models
import os
import json
import time
import logging

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Parse CORS origins
cors_origins_raw = os.getenv(
    "BACKEND_CORS_ORIGINS",
    '["http://localhost:8080","http://localhost:3000","http://127.0.0.1:5500","http://localhost:5500","http://127.0.0.1:8000"]'
)
try:
    cors_origins = json.loads(cors_origins_raw)
except Exception:
    cors_origins = ["*"]

app = FastAPI(
    title="EduTrack API",
    description="Automated Student Attendance Monitoring & Analytics",
    version="2.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Rate limiter ----------
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "200"))
RATE_LIMIT_WINDOW_SEC = int(os.getenv("RATE_LIMIT_WINDOW_SEC", "60"))
_rate_store: dict = {}

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    try:
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = int(now // RATE_LIMIT_WINDOW_SEC)
        key = f"{ip}:{window}"
        count = _rate_store.get(key, 0)
        if count >= RATE_LIMIT_REQUESTS:
            return JSONResponse(status_code=429, content={"detail": "Too Many Requests"})
        _rate_store[key] = count + 1
        return await call_next(request)
    except Exception:
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

# ---------- Routers ----------
API_V1_PREFIX = "/api/v1"

# Auth is mandatory
from .routes import auth as auth_routes
app.include_router(auth_routes.router, prefix=f"{API_V1_PREFIX}/auth", tags=["Authentication"])

# Optional routers — each loaded independently so one broken file doesn't break everything
_optional_routers = [
    ("dashboard",           "dashboard",            "Dashboard"),
    ("ai",                  "ai",                   "AI Chatbot"),
    ("attendance",          "attendance",           "Attendance"),
    ("attendance_sessions", "attendance_sessions",  "Attendance Sessions"),
    ("academic",            "academic",             "Academic"),
    ("users",               "users",                "Users"),
    ("resources",           "resources",            "Resources"),
]

for module_name, prefix, tag in _optional_routers:
    try:
        mod = __import__(f"backend.app.routes.{module_name}", fromlist=["router"])
        app.include_router(mod.router, prefix=f"{API_V1_PREFIX}/{prefix}", tags=[tag])
        logger.info(f"Loaded router: {module_name}")
    except Exception as e:
        logger.warning(f"Could not load router '{module_name}': {e}")

# ---------- Root ----------
# Root is handled by StaticFiles index.html

@app.get(f"{API_V1_PREFIX}/health")
def health_check(db=Depends(get_db)):
    return {"status": "healthy", "database": "connected"}

# ---------- Serve frontend static files (must be last) ----------
_frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public")
if os.path.isdir(_frontend_dir):
    app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="frontend")
    logger.info(f"Serving frontend from {_frontend_dir}")