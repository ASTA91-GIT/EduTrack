from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import shutil
import uuid

from .. import models
from ..database import get_db
from ..auth import get_current_user, require_teacher

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "secure_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("")
@router.get("/")
def get_resources(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get a list of all resources (books/documents)"""
    return db.query(models.Resource).all()

@router.post("")
@router.post("/")
async def upload_resource(
    title: str = Form(...),
    description: str = Form(None),
    resource_type: str = Form(...),
    subject: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_teacher)
):
    """Faculty/Admin uploads a new resource"""
    # Create secure filename
    ext = os.path.splitext(file.filename)[1]
    secure_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, secure_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    resource = models.Resource(
        title=title,
        file_type=resource_type,
        file_path=secure_filename,
        subject=subject,
        uploader_id=current_user.id
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource

@router.get("/{resource_id}/download")
def download_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Securely download a resource. Prevents path traversal."""
    resource = db.query(models.Resource).filter(models.Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
        
    file_path = os.path.join(UPLOAD_DIR, resource.file_path)
    if not os.path.exists(file_path) or ".." in resource.file_path or "/" in resource.file_path or "\\" in resource.file_path:
        raise HTTPException(status_code=404, detail="File not found on server")
        
    return FileResponse(path=file_path, filename=f"{resource.title}{os.path.splitext(resource.file_path)[1]}")
