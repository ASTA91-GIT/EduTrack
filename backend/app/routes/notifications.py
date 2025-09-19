from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from .. import database, models, auth

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def list_notifications(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    items = db.query(models.Notification).filter(models.Notification.user_id == current_user.id).order_by(models.Notification.created_at.desc()).all()
    return [
        {"id": n.id, "title": n.title, "message": n.message, "type": n.type, "is_read": n.is_read, "created_at": n.created_at.isoformat()} for n in items
    ]

@router.post("/", response_model=Dict[str, Any])
async def send_notification(
    user_public_id: str = Body(...),
    title: str = Body(...),
    message: str = Body(...),
    type: str = Body("info"),
    _: models.User = Depends(auth.require_teacher),
    db: Session = Depends(database.get_db)
):
    user = db.query(models.User).filter(models.User.public_id == user_public_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    n = models.Notification(user_id=user.id, title=title, message=message, type=type)
    db.add(n)
    db.commit()
    db.refresh(n)
    return {"id": n.id}

@router.post("/{notification_id}/read")
async def mark_read(notification_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    n = db.query(models.Notification).filter(models.Notification.id == notification_id, models.Notification.user_id == current_user.id).first()
    if not n:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    n.is_read = True
    db.commit()
    return {"ok": True}
