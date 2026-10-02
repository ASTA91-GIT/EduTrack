from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from .. import models
from ..database import get_db
from ..auth import require_teacher, get_current_user

router = APIRouter()

@router.get("/students")
def get_all_students(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_teacher)
):
    """Teachers/Admins can get a list of all students."""
    students = db.query(models.User).filter(models.User.role == "student").all()
    results = []
    for s in students:
        results.append({
            "id": s.id,
            "public_id": s.public_id,
            "name": s.name,
            "email": s.email,
            "is_active": s.is_active,
            "created_at": s.created_at.isoformat()
        })
    return results

@router.get("/notifications")
def get_notifications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get notifications for the logged in user."""
    notifs = db.query(models.Notification).filter(
        models.Notification.user_id == current_user.id
    ).order_by(models.Notification.created_at.desc()).limit(20).all()
    
    return [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "type": n.type,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat()
        } for n in notifs
    ]
