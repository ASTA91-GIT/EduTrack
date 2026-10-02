"""
Attendance Recovery Planner & Priority Engine

Deterministic calculations — no LLM involved.
All math is performed here; the chatbot only explains results.
"""
import math
import os
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from .. import models

# Configurable threshold (default 75%)
ATTENDANCE_THRESHOLD = float(os.getenv("ATTENDANCE_THRESHOLD", "75"))


# --------------- Core math ---------------

def classes_needed_to_reach(present: int, total: int, target_pct: float) -> int:
    """
    Solve: (present + N) / (total + N) >= target_pct/100
    N = ceil((target_pct * total - 100 * present) / (100 - target_pct))
    Returns 0 if already at or above target.
    Returns -1 if target is 100% and student has absences (impossible).
    """
    if total == 0:
        return 0
    current_pct = (present / total) * 100
    if current_pct >= target_pct:
        return 0
    if target_pct >= 100:
        return -1  # impossible unless 0 absences
    numerator = target_pct * total - 100 * present
    denominator = 100 - target_pct
    n = math.ceil(numerator / denominator)
    return max(n, 0)


def classes_can_miss(present: int, total: int, target_pct: float) -> int:
    """
    How many *future* classes a student can skip and still stay >= target_pct.
    Solve: present / (total + M) >= target_pct/100
    M = floor((100*present / target_pct) - total)
    """
    if total == 0 or target_pct <= 0:
        return 999  # effectively unlimited
    current_pct = (present / total) * 100
    if current_pct < target_pct:
        return 0
    max_total = (100 * present) / target_pct
    m = math.floor(max_total - total)
    return max(m, 0)


def whatif_attendance(present: int, total: int, attend_next: int) -> float:
    """Project attendance if student attends the next `attend_next` classes."""
    new_total = total + attend_next
    if new_total == 0:
        return 0.0
    return round(((present + attend_next) / new_total) * 100, 2)


def classify_risk(present: int, total: int, target_pct: float, trend: str = "stable") -> str:
    """
    CRITICAL  — > 10% below threshold
    AT_RISK   — below threshold
    RECOVERING — below threshold but improving
    SAFE      — at or above threshold
    """
    if total == 0:
        return "SAFE"
    current_pct = (present / total) * 100
    if current_pct >= target_pct:
        return "SAFE"
    if trend == "improving" and current_pct >= target_pct - 5:
        return "RECOVERING"
    if current_pct < target_pct - 10:
        return "CRITICAL"
    return "AT_RISK"


# --------------- DB helpers ---------------

def get_student_subject_stats(db: Session, student_id: int, threshold: float = None):
    """
    Return per-subject attendance stats for a student from AttendanceSessionRecord + AttendanceSession.
    """
    if threshold is None:
        threshold = ATTENDANCE_THRESHOLD

    # Get all sessions (total conducted) grouped by subject
    subject_totals = (
        db.query(
            models.AttendanceSession.subject,
            func.count(models.AttendanceSession.id).label("total")
        )
        .filter(models.AttendanceSession.status.in_(["active", "closed"]))
        .group_by(models.AttendanceSession.subject)
        .all()
    )

    # Get sessions this student attended grouped by subject
    subject_present = (
        db.query(
            models.AttendanceSession.subject,
            func.count(models.AttendanceSessionRecord.id).label("present")
        )
        .join(models.AttendanceSession, models.AttendanceSessionRecord.session_id == models.AttendanceSession.id)
        .filter(models.AttendanceSessionRecord.student_id == student_id)
        .group_by(models.AttendanceSession.subject)
        .all()
    )

    present_map = {row.subject: row.present for row in subject_present}

    results = []
    for row in subject_totals:
        subject = row.subject
        total = row.total
        present = present_map.get(subject, 0)
        absent = total - present
        pct = round((present / total) * 100, 2) if total > 0 else 0
        needed = classes_needed_to_reach(present, total, threshold)
        missable = classes_can_miss(present, total, threshold)
        risk = classify_risk(present, total, threshold)

        results.append({
            "subject": subject,
            "present": present,
            "total": total,
            "absent": absent,
            "percentage": pct,
            "threshold": threshold,
            "classes_needed": needed,
            "classes_missable": missable,
            "risk": risk,
            "trend": "stable",  # can be enhanced with historical data
        })

    return results


def get_student_overall(db: Session, student_id: int, threshold: float = None):
    """Overall attendance summary for a student."""
    stats = get_student_subject_stats(db, student_id, threshold)
    total_classes = sum(s["total"] for s in stats)
    total_present = sum(s["present"] for s in stats)
    overall_pct = round((total_present / total_classes) * 100, 2) if total_classes > 0 else 0
    at_risk = [s for s in stats if s["risk"] in ("AT_RISK", "CRITICAL")]
    safe = [s for s in stats if s["risk"] == "SAFE"]
    critical = sorted(at_risk, key=lambda x: x["percentage"])[:1]

    return {
        "overall_percentage": overall_pct,
        "total_classes": total_classes,
        "total_present": total_present,
        "total_absent": total_classes - total_present,
        "subjects_at_risk": len(at_risk),
        "subjects_safe": len(safe),
        "most_critical": critical[0] if critical else None,
        "subjects": stats,
    }


def build_student_context(db: Session, student: models.User, threshold: float = None):
    """Build the structured context object sent to the AI chatbot (no secrets)."""
    overall = get_student_overall(db, student.id, threshold)
    return {
        "student": {
            "name": student.name,
            "email": student.email,
            "role": student.role,
        },
        "attendance": {
            "overall_percentage": overall["overall_percentage"],
            "total_classes": overall["total_classes"],
            "present": overall["total_present"],
            "absent": overall["total_absent"],
            "subjects_at_risk": overall["subjects_at_risk"],
            "subjects_safe": overall["subjects_safe"],
        },
        "subjects": overall["subjects"],
        "most_critical": overall["most_critical"],
    }
