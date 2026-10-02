from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List

from .. import models
from ..database import get_db
from ..auth import get_current_user, require_teacher, require_student

router = APIRouter()

# --- TESTS ---
@router.get("/tests")
def get_tests(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role == "teacher":
        tests = db.query(models.Test).filter(models.Test.faculty_id == current_user.id).all()
        return tests
    else:
        # Students see all tests, optionally joined with their scores
        tests = db.query(models.Test).all()
        scores = db.query(models.TestScore).filter(models.TestScore.student_id == current_user.id).all()
        score_map = {s.test_id: s.score for s in scores}
        
        results = []
        for t in tests:
            results.append({
                "id": t.id,
                "subject": t.subject,
                "title": t.title,
                "max_score": t.max_score,
                "test_date": t.test_date,
                "score": score_map.get(t.id, None)
            })
        return results

@router.post("/tests")
def create_test(
    subject: str, title: str, max_score: float, test_date: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_teacher)
):
    test = models.Test(
        faculty_id=current_user.id,
        subject=subject,
        title=title,
        max_score=max_score,
        test_date=test_date
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    return test

# --- ASSIGNMENTS ---
@router.get("/assignments")
def get_assignments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Both students and teachers can view all assignments for simplicity
    assignments = db.query(models.Assignment).order_by(models.Assignment.due_date.asc()).all()
    return assignments

# --- EVENTS ---
@router.get("/events")
def get_events(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    events = db.query(models.Event).order_by(models.Event.event_date.asc()).all()
    return events
