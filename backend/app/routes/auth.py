from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Dict, Any
import uuid

from .. import database, models, auth
from ..auth import get_password_hash, verify_password, create_tokens, refresh_access_token

router = APIRouter()

@router.post("/register", response_model=Dict[str, Any])
async def register_user(
    name: str = Body(...),
    email: str = Body(...),
    password: str = Body(...),
    role: str = Body(...),
    db: Session = Depends(database.get_db)
):
    # Check if user already exists
    existing_user = db.query(models.User).filter(models.User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate role
    if role not in ["teacher", "student"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be 'teacher' or 'student'"
        )
    
    # Create new user
    hashed_password = get_password_hash(password)
    public_id = str(uuid.uuid4())
    
    new_user = models.User(
        public_id=public_id,
        name=name,
        email=email,
        password=hashed_password,
        role=role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create tokens
    tokens = create_tokens({"sub": public_id})
    
    return {
        "user": {
            "id": new_user.public_id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role
        },
        **tokens
    }

@router.post("/login", response_model=Dict[str, Any])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    role: str = Body(...),
    db: Session = Depends(database.get_db)
):
    # Find user by email
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # Verify user exists, password is correct, and role matches
    if not user or not verify_password(form_data.password, user.password) or user.role != role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email, password, or role",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    tokens = create_tokens({"sub": user.public_id})
    
    return {
        "user": {
            "id": user.public_id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        },
        **tokens
    }

@router.post("/refresh", response_model=Dict[str, Any])
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    db: Session = Depends(database.get_db)
):
    # Use the refresh token to get a new access token
    try:
        new_token = refresh_access_token(refresh_token, db)
        return new_token
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not refresh token: {str(e)}"
        )

@router.get("/me", response_model=Dict[str, Any])
async def get_user_info(current_user: models.User = Depends(auth.get_current_user)):
    # Return current user info
    return {
        "id": current_user.public_id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role
    }