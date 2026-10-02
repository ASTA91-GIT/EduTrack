"""
Dashboard & Analytics API — all data from PostgreSQL/SQLite, zero hardcoding.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from .. import models
from ..database import get_db
from ..auth import get_current_user, require_teacher, require_student
from ..services import (
    get_student_overall,
    get_student_subject_stats,
    whatif_attendance,
    classes_needed_to_reach,
    classes_can_miss,
    ATTENDANCE_THRESHOLD,
)

router = APIRouter()


# -------- Student Dashboard --------

@router.get("/student")
def student_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_student),
):
    """Full student dashboard data — attendance, subjects, risk, recovery."""
    overall = get_student_overall(db, current_user.id)
    return {
        "user": {
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role,
        },
        **overall,
    }


@router.get("/student/recovery")
def student_recovery(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_student),
):
    """Attendance Recovery Planner for the logged-in student."""
    stats = get_student_subject_stats(db, current_user.id)
    at_risk = [s for s in stats if s["risk"] in ("AT_RISK", "CRITICAL", "RECOVERING")]
    safe = [s for s in stats if s["risk"] == "SAFE"]
    return {
        "threshold": ATTENDANCE_THRESHOLD,
        "at_risk": at_risk,
        "safe": safe,
        "all_subjects": stats,
    }


@router.get("/student/whatif")
def student_whatif(
    attend_next: int = Query(1, ge=0, le=100),
    subject: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_student),
):
    """What-if attendance simulator."""
    stats = get_student_subject_stats(db, current_user.id)

    results = []
    for s in stats:
        if subject and s["subject"] != subject:
            continue
        projected = whatif_attendance(s["present"], s["total"], attend_next)
        results.append({
            "subject": s["subject"],
            "current_percentage": s["percentage"],
            "projected_percentage": projected,
            "attend_next": attend_next,
            "would_meet_threshold": projected >= s["threshold"],
        })

    return {"results": results}


# -------- Faculty Dashboard --------

@router.get("/faculty")
def faculty_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_teacher),
):
    """Faculty dashboard — sessions created, student counts, defaulters."""
    # Sessions created by this faculty
    sessions = (
        db.query(models.AttendanceSession)
        .filter(models.AttendanceSession.faculty_id == current_user.id)
        .order_by(models.AttendanceSession.created_at.desc())
        .limit(20)
        .all()
    )

    session_data = []
    for s in sessions:
        record_count = (
            db.query(func.count(models.AttendanceSessionRecord.id))
            .filter(models.AttendanceSessionRecord.session_id == s.id)
            .scalar()
        )
        session_data.append({
            "id": s.id,
            "subject": s.subject,
            "class_name": s.class_name,
            "status": s.status,
            "created_at": s.created_at.isoformat(),
            "expires_at": s.expires_at.isoformat(),
            "attendee_count": record_count,
        })

    # Total students
    total_students = db.query(func.count(models.User.id)).filter(models.User.role == "student").scalar()

    return {
        "user": {
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role,
        },
        "total_students": total_students,
        "total_sessions": len(session_data),
        "recent_sessions": session_data,
    }


# -------- Admin Dashboard --------

@router.get("/admin")
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Admin overview — user counts, session counts, risk distribution."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    total_students = db.query(func.count(models.User.id)).filter(models.User.role == "student").scalar()
    total_faculty = db.query(func.count(models.User.id)).filter(models.User.role == "teacher").scalar()
    total_sessions = db.query(func.count(models.AttendanceSession.id)).scalar()
    active_sessions = (
        db.query(func.count(models.AttendanceSession.id))
        .filter(models.AttendanceSession.status == "active")
        .scalar()
    )

    # Risk distribution across all students
    students = db.query(models.User).filter(models.User.role == "student").all()
    risk_counts = {"SAFE": 0, "AT_RISK": 0, "CRITICAL": 0, "RECOVERING": 0}
    for student in students:
        stats = get_student_subject_stats(db, student.id)
        for s in stats:
            risk_counts[s["risk"]] = risk_counts.get(s["risk"], 0) + 1

    return {
        "total_students": total_students,
        "total_faculty": total_faculty,
        "total_sessions": total_sessions,
        "active_sessions": active_sessions,
        "risk_distribution": risk_counts,
    }


# -------- Analytics --------

@router.get("/analytics/attendance-trend")
def attendance_trend(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Daily attendance trend from session records."""
    rows = (
        db.query(
            func.date(models.AttendanceSession.created_at).label("date"),
            func.count(models.AttendanceSessionRecord.id).label("present_count"),
        )
        .join(models.AttendanceSession, models.AttendanceSessionRecord.session_id == models.AttendanceSession.id)
        .group_by(func.date(models.AttendanceSession.created_at))
        .order_by(func.date(models.AttendanceSession.created_at))
        .all()
    )
    return {
        "dates": [str(r.date) for r in rows],
        "counts": [r.present_count for r in rows],
    }
