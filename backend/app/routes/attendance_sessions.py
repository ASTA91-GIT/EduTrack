import os
import io
import math
import time
import hmac
import hashlib
from datetime import datetime, timedelta
from secrets import token_urlsafe
from typing import Dict, List, Optional

from fastapi import (
    APIRouter, Depends, HTTPException, status, Body, Query,
    WebSocket, WebSocketDisconnect
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import qrcode

from .. import models, database, auth
from ..auth import require_teacher, require_student, get_current_user

router = APIRouter()

DEFAULT_QR_DURATION = int(os.getenv("QR_SESSION_DURATION_MINUTES", "10"))
SECRET_KEY = os.getenv("SECRET_KEY", "edutrack-super-secure-production-secret-key-2026")
DEFAULT_GEOFENCE_RADIUS = 30.0 # 30 meters as required
MAX_ALLOWED_ACCURACY = 60.0 # GPS accuracy threshold

# Predefined standard campus classrooms
CAMPUS_CLASSROOMS = [
    {"name": "Room 101 - CS Lab", "latitude": 19.0760, "longitude": 72.8777, "radius": 30.0},
    {"name": "Room 203 - Tech Hall", "latitude": 19.0762, "longitude": 72.8780, "radius": 30.0},
    {"name": "Hall A - Main Auditorium", "latitude": 19.0758, "longitude": 72.8775, "radius": 35.0},
    {"name": "Room 405 - Seminar Room", "latitude": 19.0765, "longitude": 72.8782, "radius": 30.0},
    {"name": "Room 501 - AI & Robotics Lab", "latitude": 19.0770, "longitude": 72.8785, "radius": 30.0},
]

# Haversine distance in meters
def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000.0  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def generate_signed_qr_token(session_token: str, timestamp: int) -> str:
    msg = f"{session_token}:{timestamp}".encode()
    sig = hmac.new(SECRET_KEY.encode(), msg, hashlib.sha256).hexdigest()[:16]
    return f"{session_token}_{timestamp}_{sig}"

def verify_signed_qr_token(qr_token: str, session_token: str, max_age_seconds: int = 60) -> bool:
    try:
        parts = qr_token.split("_")
        if len(parts) != 3:
            return False
        st, ts_str, sig = parts
        if st != session_token:
            return False
        ts = int(ts_str)
        now = int(time.time())
        if abs(now - ts) > max_age_seconds:
            return False
        expected_sig = hmac.new(SECRET_KEY.encode(), f"{session_token}:{ts}".encode(), hashlib.sha256).hexdigest()[:16]
        return hmac.compare_digest(sig, expected_sig)
    except Exception:
        return False

# Real-time WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, session_token: str, websocket: WebSocket):
        await websocket.accept()
        if session_token not in self.active_connections:
            self.active_connections[session_token] = []
        self.active_connections[session_token].append(websocket)

    def disconnect(self, session_token: str, websocket: WebSocket):
        if session_token in self.active_connections:
            if websocket in self.active_connections[session_token]:
                self.active_connections[session_token].remove(websocket)
            if not self.active_connections[session_token]:
                del self.active_connections[session_token]

    async def broadcast(self, session_token: str, data: dict):
        if session_token in self.active_connections:
            for connection in list(self.active_connections[session_token]):
                try:
                    await connection.send_json(data)
                except Exception:
                    pass

manager = ConnectionManager()


@router.get("/classrooms")
def get_classrooms():
    """Return available campus classrooms without exposing exact coordinates to frontend."""
    return [
        {"name": c["name"], "radius": c["radius"]}
        for c in CAMPUS_CLASSROOMS
    ]


@router.post("/session", response_model=dict)
async def create_attendance_session(
    subject: str = Body(...),
    class_name: str = Body(...),
    classroom_name: str = Body("Room 101 - CS Lab"),
    latitude: Optional[float] = Body(None),
    longitude: Optional[float] = Body(None),
    geofence_radius: Optional[float] = Body(30.0),
    duration_minutes: Optional[int] = Body(None),
    current_user: models.User = Depends(require_teacher),
    db: Session = Depends(database.get_db),
):
    """Create a new attendance session with geofence settings."""
    duration = duration_minutes or DEFAULT_QR_DURATION
    token = token_urlsafe(16)
    expires_at = datetime.utcnow() + timedelta(minutes=duration)
    
    # Resolve classroom coordinates
    target_lat = latitude
    target_lon = longitude
    radius = geofence_radius or DEFAULT_GEOFENCE_RADIUS

    if target_lat is None or target_lon is None:
        # Match with campus presets
        matched = next((c for c in CAMPUS_CLASSROOMS if c["name"] == classroom_name), None)
        if matched:
            target_lat = matched["latitude"]
            target_lon = matched["longitude"]
            radius = matched["radius"]
        else:
            # Fallback to campus default
            target_lat = CAMPUS_CLASSROOMS[0]["latitude"]
            target_lon = CAMPUS_CLASSROOMS[0]["longitude"]

    initial_qr_token = generate_signed_qr_token(token, int(time.time()))

    session = models.AttendanceSession(
        faculty_id=current_user.id,
        subject=subject,
        class_name=class_name,
        classroom_name=classroom_name,
        latitude=target_lat,
        longitude=target_lon,
        geofence_radius=radius,
        session_token=token,
        current_qr_token=initial_qr_token,
        expires_at=expires_at,
        status="active",
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "session_token": token,
        "qr_token": initial_qr_token,
        "expires_at": expires_at.isoformat(),
        "geofence_radius": radius,
        "classroom_name": classroom_name,
    }


@router.get("/session/{token}/refresh-qr")
def refresh_qr_token(
    token: str,
    current_user: models.User = Depends(require_teacher),
    db: Session = Depends(database.get_db),
):
    """Generate a refreshed dynamic short-lived token for rotating QR display."""
    session = db.query(models.AttendanceSession).filter(models.AttendanceSession.session_token == token).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session.status != "active" or session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session is not active")
    if session.faculty_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    now_ts = int(time.time())
    new_qr_token = generate_signed_qr_token(token, now_ts)
    session.current_qr_token = new_qr_token
    db.commit()

    return {
        "session_token": token,
        "qr_token": new_qr_token,
        "valid_seconds": 20,
    }


@router.get("/session/{token}/qr")
def get_session_qr(
    token: str,
    t: Optional[str] = None,
    db: Session = Depends(database.get_db),
):
    """Return a PNG QR code containing the verification URL for students to scan."""
    session = db.query(models.AttendanceSession).filter(models.AttendanceSession.session_token == token).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session.status != "active" or session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session is not active")

    qr_token = t or session.current_qr_token or generate_signed_qr_token(token, int(time.time()))
    payload = f"http://localhost:8080/verify.html?session={token}&t={qr_token}"

    img = qrcode.make(payload)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


@router.get("/session/{token}")
def get_session_info(token: str, db: Session = Depends(database.get_db)):
    """Return session state, attendee list and counts. Never exposes classroom coordinates."""
    session = db.query(models.AttendanceSession).filter(models.AttendanceSession.session_token == token).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    records = (
        db.query(models.AttendanceSessionRecord)
        .filter(models.AttendanceSessionRecord.session_id == session.id)
        .order_by(models.AttendanceSessionRecord.marked_at.desc())
        .all()
    )

    attendees = []
    for rec in records:
        student = db.query(models.User).filter(models.User.id == rec.student_id).first()
        if student:
            attendees.append({
                "id": student.public_id,
                "name": student.name,
                "email": student.email,
                "marked_at": rec.marked_at.strftime("%I:%M:%S %p"),
                "distance": rec.distance_meters,
                "accuracy": rec.gps_accuracy,
                "status": rec.status,
            })

    total_registered = db.query(models.User).filter(models.User.role == "student").count()
    present_count = len(attendees)
    absent_count = max(0, total_registered - present_count)

    now = datetime.utcnow()
    remaining = max(0, int((session.expires_at - now).total_seconds()))

    return {
        "session_token": session.session_token,
        "subject": session.subject,
        "class_name": session.class_name,
        "classroom_name": session.classroom_name or "Classroom",
        "status": session.status,
        "expires_at": session.expires_at.isoformat(),
        "remaining_seconds": remaining,
        "geofence_radius": session.geofence_radius or DEFAULT_GEOFENCE_RADIUS,
        "attendees": attendees,
        "present_count": present_count,
        "absent_count": absent_count,
        "total_students": total_registered,
    }


@router.post("/session/verify-gps")
async def verify_student_gps(
    session_token: str = Body(...),
    qr_token: str = Body(...),
    latitude: float = Body(...),
    longitude: float = Body(...),
    accuracy: float = Body(...),
    current_user: models.User = Depends(require_student),
    db: Session = Depends(database.get_db),
):
    """Student GPS-Geofenced Attendance Verification.
    Calculates Haversine distance securely on the backend.
    """
    session = (
        db.query(models.AttendanceSession)
        .filter(models.AttendanceSession.session_token == session_token)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid session token")

    if session.status != "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session has ended")

    if session.expires_at < datetime.utcnow():
        session.status = "closed"
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session has expired")

    # Validate signed dynamic token
    token_valid = verify_signed_qr_token(qr_token, session_token, max_age_seconds=60)
    if not token_valid and session.current_qr_token != qr_token and session_token != qr_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="QR code expired. Please scan again.")

    # Check duplicate attendance
    existing = (
        db.query(models.AttendanceSessionRecord)
        .filter(
            models.AttendanceSessionRecord.session_id == session.id,
            models.AttendanceSessionRecord.student_id == current_user.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Attendance already marked at {existing.marked_at.strftime('%I:%M %p')}"
        )

    # Check GPS accuracy
    if accuracy > MAX_ALLOWED_ACCURACY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"GPS accuracy too poor (±{int(accuracy)}m). Please enable Wi-Fi or move near an open window."
        )

    # Compute Haversine distance from classroom anchor
    room_lat = session.latitude or CAMPUS_CLASSROOMS[0]["latitude"]
    room_lon = session.longitude or CAMPUS_CLASSROOMS[0]["longitude"]
    distance = haversine_distance(latitude, longitude, room_lat, room_lon)
    radius = session.geofence_radius or DEFAULT_GEOFENCE_RADIUS

    if distance > radius:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Outside classroom geofence. You are {round(distance, 1)}m away (max permitted is {int(radius)}m)."
        )

    # Record attendance
    record = models.AttendanceSessionRecord(
        session_id=session.id,
        student_id=current_user.id,
        marked_at=datetime.utcnow(),
        student_lat=latitude,
        student_lon=longitude,
        distance_meters=round(distance, 1),
        gps_accuracy=round(accuracy, 1),
        verification_method="qr_gps",
        status="present",
    )
    db.add(record)
    db.commit()

    total_present = (
        db.query(models.AttendanceSessionRecord)
        .filter(models.AttendanceSessionRecord.session_id == session.id)
        .count()
    )

    # Broadcast live event to Teacher via WebSocket
    marked_time_str = datetime.utcnow().strftime("%I:%M:%S %p")
    payload = {
        "type": "STUDENT_VERIFIED",
        "student": {
            "id": current_user.public_id,
            "name": current_user.name,
            "email": current_user.email,
            "time": marked_time_str,
            "distance": round(distance, 1),
            "accuracy": round(accuracy, 1),
            "status": "Verified",
        },
        "present_count": total_present,
    }
    await manager.broadcast(session_token, payload)

    return {
        "success": True,
        "message": "Attendance Verified Successfully",
        "subject": session.subject,
        "class_name": session.class_name,
        "classroom_name": session.classroom_name,
        "time": marked_time_str,
        "distance": round(distance, 1),
        "accuracy": round(accuracy, 1),
        "status": "Verified",
    }


@router.websocket("/ws/{session_token}")
async def session_websocket(websocket: WebSocket, session_token: str):
    """Real-time WebSocket endpoint for the Teacher Attendance Dashboard."""
    await manager.connect(session_token, websocket)
    try:
        while True:
            # Keep-alive ping/pong
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(session_token, websocket)
    except Exception:
        manager.disconnect(session_token, websocket)


@router.post("/session/{token}/close")
async def close_session(
    token: str,
    current_user: models.User = Depends(require_teacher),
    db: Session = Depends(database.get_db),
):
    session = (
        db.query(models.AttendanceSession)
        .filter(models.AttendanceSession.session_token == token)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session.faculty_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your session")
    session.status = "closed"
    session.closed_at = datetime.utcnow()
    db.commit()

    # Notify WebSocket listeners
    await manager.broadcast(token, {"type": "SESSION_CLOSED", "message": "Attendance session ended."})

    return {"ok": True, "message": "Session closed"}


@router.post("/dev/reset-test-data")
def dev_reset_test_data(db: Session = Depends(database.get_db)):
    """Development-only endpoint: resets attendance records for TEST_STUDENT_001.
    Strictly blocked in production environments.
    """
    from ..test_config import ENVIRONMENT, TEST_STUDENT_ID, TEST_STUDENT_EMAIL

    if ENVIRONMENT == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dev test data reset is disabled in production."
        )

    test_user = (
        db.query(models.User)
        .filter((models.User.public_id == TEST_STUDENT_ID) | (models.User.email == TEST_STUDENT_EMAIL))
        .first()
    )

    if not test_user:
        return {"status": "ok", "deleted": 0, "message": "Test student not found."}

    deleted = (
        db.query(models.AttendanceSessionRecord)
        .filter(models.AttendanceSessionRecord.student_id == test_user.id)
        .delete(synchronize_session=False)
    )
    db.commit()

    return {
        "status": "ok",
        "deleted": deleted,
        "test_student_id": TEST_STUDENT_ID,
        "message": f"Successfully cleared {deleted} test records for {TEST_STUDENT_ID}."
    }

