from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from .. import database, models, auth

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def list_appeals(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    q = db.query(models.Appeal)
    if current_user.role == "student":
        q = q.filter(models.Appeal.user_id == current_user.id)
    items = q.order_by(models.Appeal.created_at.desc()).all()
    return [{"id": a.id, "status": a.status, "reason": a.reason, "user_id": a.user_id, "attendance_id": a.attendance_id} for a in items]

@router.post("/", response_model=Dict[str, Any])
async def create_appeal(reason: str = Body(...), attendance_id: int | None = Body(None), current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    a = models.Appeal(user_id=current_user.id, attendance_id=attendance_id, reason=reason)
    db.add(a)
    db.commit()
    db.refresh(a)
    return {"id": a.id}

@router.post("/{appeal_id}/approve")
async def approve_appeal(appeal_id: int, _: models.User = Depends(auth.require_teacher), db: Session = Depends(database.get_db)):
    a = db.query(models.Appeal).filter(models.Appeal.id == appeal_id).first()
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appeal not found")
    a.status = "approved"
    db.commit()
    return {"ok": True}

@router.post("/{appeal_id}/reject")
async def reject_appeal(appeal_id: int, _: models.User = Depends(auth.require_teacher), db: Session = Depends(database.get_db)):
    a = db.query(models.Appeal).filter(models.Appeal.id == appeal_id).first()
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appeal not found")
    a.status = "rejected"
    db.commit()
    return {"ok": True}
