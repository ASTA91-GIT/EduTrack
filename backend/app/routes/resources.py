from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..auth import get_current_user

router = APIRouter()

@router.get("/")
def get_resources(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get a list of all resources (books)"""
    return db.query(models.Resource).all()

# Endpoint to download securely can be added later by checking permissions
# and serving from a secure, non-public directory.
