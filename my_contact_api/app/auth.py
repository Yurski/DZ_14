from fastapi import APIRouter, HTTPException, Depends, status, File, UploadFile
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User
from app.security import get_password_hash, verify_password, create_access_token
from pydantic import BaseModel
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
from datetime import timedelta

load_dotenv()

router = APIRouter()

class UserCreate(BaseModel):
    """Модель для створення користувача."""
    email: str
    password: str

async def send_verification_email(email: str, token: str):
    """Відправляє електронний лист для підтвердження адреси."""
    message = MessageSchema(
        subject="Email Verification",
        recipients=[email],
        body=f"Please verify your email by clicking on the link: http://localhost:8000/verify/{token}",
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)

@router.post("/register/", response_model=UserCreate, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: Session = Depends(SessionLocal)):
    """Реєструє нового користувача."""
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    verification_token = create_access_token(data={"sub": db_user.email}, expires_delta=timedelta(hours=1))
    await send_verification_email(user.email, verification_token)

    return db_user

@router.get("/verify/{token}")
async def verify_email(token: str, db: Session = Depends(SessionLocal)):
    """Підтверджує електронну адресу користувача за токеном."""
    payload = decode_token(token)
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = db.query(User).filter(User.email == email).first()
    if user:
        user.is_verified = True
        db.commit()
    return {"msg": "Email verified"}

@router.put("/users/avatar/")
async def update_avatar(avatar: UploadFile = File(...), db: Session = Depends(SessionLocal)):
    """Оновлює аватар користувача."""
    upload_result = cloudinary.uploader.upload(avatar.file)
    user = db.query(User).filter(User.email == get_current_user()).first()
    user.avatar_url = upload_result['secure_url']
    db.commit()
    return {"msg": "Avatar updated", "url": user.avatar_url}
