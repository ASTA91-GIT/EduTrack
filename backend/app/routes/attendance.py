from fastapi import APIRouter, Depends, Response, Query
from sqlalchemy.orm import Session
from typing import Dict, Any
import csv
import io
from .. import database, models, auth

router = APIRouter()

@router.get("/stats", response_model=Dict[str, Any])
async def attendance_stats(user_id: str = Query(None), current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    # Simple stats: count by status for current user (or specified user if admin/teacher)
    target_user = current_user
    if user_id and current_user.role in ["teacher", "admin"]:
        target_user = db.query(models.User).filter(models.User.public_id == user_id).first() or current_user
    q = db.query(models.AttendanceRecord).filter(models.AttendanceRecord.user_id == target_user.id)
    total = q.count()
    present = q.filter(models.AttendanceRecord.status == "present").count()
    late = q.filter(models.AttendanceRecord.status == "late").count()
    absent = q.filter(models.AttendanceRecord.status == "absent").count()
    return {"total": total, "present": present, "late": late, "absent": absent}

@router.get("/export")
async def export_attendance(user_id: str = Query(None), current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    target_user = current_user
    if user_id and current_user.role in ["teacher", "admin"]:
        target_user = db.query(models.User).filter(models.User.public_id == user_id).first() or current_user
    records = db.query(models.AttendanceRecord).filter(models.AttendanceRecord.user_id == target_user.id).order_by(models.AttendanceRecord.timestamp.desc()).all()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["timestamp","type","method","confidence","status","location"])
    for r in records:
        writer.writerow([r.timestamp.isoformat(), r.type, r.method, r.confidence_score or "", r.status, r.location or ""])
    csv_bytes = buf.getvalue().encode("utf-8")
    return Response(content=csv_bytes, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=attendance.csv"})
