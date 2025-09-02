from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
import shutil
import os
from .. import models, database, schemas
from ..auth import get_current_user
from ..face_recognition import face_service

router = APIRouter()

# Ensure upload directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/mark")
async def mark_attendance(
    file: UploadFile = File(...),
    location: str = Form(None),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Save uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Recognize face
    recognized_faces = face_service.recognize_face(file_path, db)
    
    if not recognized_faces:
        raise HTTPException(status_code=400, detail="No face recognized")
    
    # Get the best match
    best_match = max(recognized_faces, key=lambda x: x["confidence"])
    
    if best_match["confidence"] < 0.6:  # Confidence threshold
        raise HTTPException(status_code=400, detail="Low confidence recognition")
    
    # Create attendance record
    attendance_record = models.AttendanceRecord(
        user_id=best_match["user_id"],
        type="check_in",
        method="facial_recognition",
        confidence_score=best_match["confidence"],
        location=location,
        capture_image_url=file_path,
        status="present"
    )
    
    db.add(attendance_record)
    db.commit()
    db.refresh(attendance_record)
    
    # Get user details
    user = db.query(models.User).filter(models.User.id == best_match["user_id"]).first()
    
    return {
        "status": "success",
        "user_id": user.public_id,
        "user_name": user.full_name,
        "confidence": best_match["confidence"],
        "timestamp": attendance_record.timestamp
    }

@router.get("/history/{user_id}")
def get_attendance_history(
    user_id: str,
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if user is authorized
    if current_user.role != "admin" and current_user.public_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Find user
    user = db.query(models.User).filter(models.User.public_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Build query
    query = db.query(models.AttendanceRecord).filter(models.AttendanceRecord.user_id == user.id)
    
    if start_date:
        query = query.filter(models.AttendanceRecord.timestamp >= start_date)
    if end_date:
        query = query.filter(models.AttendanceRecord.timestamp <= end_date)
    
    records = query.order_by(models.AttendanceRecord.timestamp.desc()).all()
    
    return {
        "user_id": user.public_id,
        "user_name": user.full_name,
        "records": records
    }