from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from secrets import token_urlsafe
from fastapi.responses import StreamingResponse
import io
import qrcode

from .. import models, database, auth
from ..auth import require_teacher, require_student

router = APIRouter()

# Environment variable for default session duration (minutes)
import os
DEFAULT_QR_DURATION = int(os.getenv("QR_SESSION_DURATION_MINUTES", "5"))

@router.post("/session", response_model=dict)
async def create_attendance_session(
    subject: str = Body(...),
    class_name: str = Body(...),
    duration_minutes: int = Body(None),
    current_user: models.User = Depends(require_teacher),
    db: Session = Depends(database.get_db),
):
    """Create a new attendance session for a faculty member.
    Returns the session token and expiry.
    """
    duration = duration_minutes or DEFAULT_QR_DURATION
    token = token_urlsafe(16)
    expires_at = datetime.utcnow() + timedelta(minutes=duration)
    session = models.AttendanceSession(
        faculty_id=current_user.id,
        subject=subject,
        class_name=class_name,
        session_token=token,
        expires_at=expires_at,
        status="active",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"session_token": token, "expires_at": expires_at.isoformat()}

@router.get("/session/{token}/qr")
def get_session_qr(token: str, db: Session = Depends(database.get_db)):
    """Return a PNG QR code containing the session token.
    Payload format: `EDUTRACK_ATTENDANCE:<TOKEN>`
    """
    session = db.query(models.AttendanceSession).filter(models.AttendanceSession.session_token == token).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session.status != "active" or session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session is not active")
    payload = f"EDUTRACK_ATTENDANCE:{token}"
    img = qrcode.make(payload)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

@router.get("/session/{token}")
def get_session_info(token: str, db: Session = Depends(database.get_db)):
    session = db.query(models.AttendanceSession).filter(models.AttendanceSession.session_token == token).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    records = (
        db.query(models.AttendanceSessionRecord)
        .filter(models.AttendanceSessionRecord.session_id == session.id)
        .all()
    )
    attendees = []
    for rec in records:
        student = db.query(models.User).filter(models.User.id == rec.student_id).first()
        if student:
            attendees.append({"id": student.public_id, "name": student.name, "marked_at": rec.marked_at.isoformat()})
    return {
        "subject": session.subject,
        "class_name": session.class_name,
        "status": session.status,
        "expires_at": session.expires_at.isoformat(),
        "attendees": attendees,
        "count": len(attendees),
    }

@router.post("/session/scan")
def scan_qr(
    session_token: str = Body(..., embed=True),
    current_user: models.User = Depends(require_student),
    db: Session = Depends(database.get_db),
):
    """Student scans QR and marks attendance.
    Enforces duplicate prevention via unique constraint.
    """
    session = (
        db.query(models.AttendanceSession)
        .filter(models.AttendanceSession.session_token == session_token)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid session token")
    if session.status != "active" or session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session is closed or expired")
    existing = (
        db.query(models.AttendanceSessionRecord)
        .filter(
            models.AttendanceSessionRecord.session_id == session.id,
            models.AttendanceSessionRecord.student_id == current_user.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Attendance already recorded")
    record = models.AttendanceSessionRecord(
        session_id=session.id,
        student_id=current_user.id,
        marked_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    return {"success": True, "message": "Attendance marked successfully"}

@router.post("/session/{token}/close")
def close_session(
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
    db.commit()
    return {"ok": True, "message": "Session closed"}
