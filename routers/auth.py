from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status,Form
from fastapi.security import OAuth2PasswordRequestForm 
from sqlalchemy.orm import Session
from typing import Any,Optional

from db.database import get_db
from models.user import User
from models.doctor import Doctor
from schemas.user import UserCreate, UserOut, Token
from schemas.doctor import DoctorCreate, DoctorOut
from core.security import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_user_by_email,  # Updated function name
    get_doctor_by_email  # Updated function nam
)
from core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register/user", response_model=UserOut)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)) -> Any:
    # Check for existing email (not username)
    existing_user = get_user_by_email(db, user_data.email)  # Updated to email
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="البريد الإلكتروني مستخدم بالفعل"  # Updated message
        )
    
    user = User(
        email=user_data.email,  # Use email as primary identifier
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        date_of_birth=user_data.date_of_birth,
        phone_number=user_data.phone_number,
        address=user_data.address,
        medical_history=user_data.medical_history
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/register/doctor", response_model=DoctorOut)
def register_doctor(doctor_data: DoctorCreate, db: Session = Depends(get_db)) -> Any:
    # Check for existing email (not username)
    existing_doctor = get_doctor_by_email(db, doctor_data.email)  # Updated to email
    if existing_doctor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="البريد الإلكتروني مستخدم بالفعل"  # Updated message
        )
    
    doctor = Doctor(
        email=doctor_data.email,  # Use email as primary identifier
        hashed_password=get_password_hash(doctor_data.password),
        name=doctor_data.name,
        specialty=doctor_data.specialty,
        hospital=doctor_data.hospital,
        lat=doctor_data.lat,
        lng=doctor_data.lng,
        address=doctor_data.address,
        phone=doctor_data.phone
    )
    
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor

class CustomOAuth2PasswordRequestForm:
    def __init__(
        self,
        username: str = Form(...),
        password: str = Form(...),
        grant_type: Optional[str] = Form("password"),  # Default to "password"
        scope: str = Form(""),
        client_id: Optional[str] = Form(None),
        client_secret: Optional[str] = Form(None),
    ):
        self.username = username
        self.password = password
        self.grant_type = grant_type
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret

# Update the login endpoint
@router.post("/login", response_model=Token)
def login(
    form_data: CustomOAuth2PasswordRequestForm = Depends(),  # Use custom form
    db: Session = Depends(get_db)
) -> Any:
    """
    تسجيل الدخول واستلام رمز الوصول
    """
    user_data = authenticate_user(db, form_data.username, form_data.password)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="البريد الإلكتروني أو كلمة المرور غير صحيحة",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_data["user"].email, "user_type": user_data["user_type"]},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}