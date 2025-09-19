from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
import csv
from io import StringIO
from .. import database, models, auth

router = APIRouter()

@router.post("/bulk-upload")
async def bulk_upload_students(file: UploadFile = File(...), _: models.User = Depends(auth.require_teacher), db: Session = Depends(database.get_db)):
    if file.content_type not in ("text/csv", "application/vnd.ms-excel"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CSV file required")
    content = (await file.read()).decode("utf-8", errors="ignore")
    reader = csv.DictReader(StringIO(content))
    created = 0
    for row in reader:
        name = (row.get("name") or "").strip()
        email = (row.get("email") or "").strip()
        if not name or not email:
            continue
        existing = db.query(models.User).filter(models.User.email == email).first()
        if existing:
            continue
        u = models.User(name=name, email=email, password="", role="student")
        db.add(u)
        created += 1
    db.commit()
    return {"created": created}
