from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from core.config import settings
from models.user import User
from models.doctor import Doctor
from db.database import get_db
from schemas.user import TokenData
from core.cache import get_cache, set_cache
import json

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    # التحقق من وجود التخزين المؤقت إذا كان مفعلاً
    if settings.REDIS_ENABLED:
        try:
            cached_user = get_cache(f"user:{email}")
            if cached_user:
                # تحويل البيانات المخزنة (سلسلة JSON) إلى قاموس ثم إلى كائن User
                user_dict = json.loads(cached_user)
                
                # تحويل التواريخ من سلسلة ISO إلى كائنات datetime
                if user_dict.get('date_of_birth'):
                    user_dict['date_of_birth'] = datetime.fromisoformat(user_dict['date_of_birth'])
                if user_dict.get('created_at'):
                    user_dict['created_at'] = datetime.fromisoformat(user_dict['created_at'])
                if user_dict.get('updated_at'):
                    user_dict['updated_at'] = datetime.fromisoformat(user_dict['updated_at'])
                    
                return User(**user_dict)
        except Exception as e:
            print(f"خطأ في فك تشفير التخزين المؤقت للمستخدم {email}: {e}")
    
    # إذا لم يكن في التخزين المؤقت أو حدث خطأ، استعلم من قاعدة البيانات
    user = db.query(User).filter(User.email == email).first()
    
    if user and settings.REDIS_ENABLED:
        try:
            # تحويل كائن User إلى قاموس للتخزين
            user_dict = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "hashed_password": user.hashed_password,
                "full_name": user.full_name,
                "date_of_birth": user.date_of_birth.isoformat() if user.date_of_birth else None,
                "phone_number": user.phone_number,
                "address": user.address,
                "medical_history": user.medical_history,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }
            set_cache(f"user:{email}", json.dumps(user_dict), 300)
        except Exception as e:
            print(f"خطأ في تخزين بيانات المستخدم {email}: {e}")
            
    return user

def get_doctor_by_email(db: Session, email: str) -> Optional[Doctor]:
    # التحقق من وجود التخزين المؤقت إذا كان مفعلاً
    if settings.REDIS_ENABLED:
        try:
            cached_doctor = get_cache(f"doctor:{email}")
            if cached_doctor:
                doctor_dict = json.loads(cached_doctor)
                
                # تحويل التواريخ من سلسلة ISO إلى كائنات datetime
                if doctor_dict.get('created_at'):
                    doctor_dict['created_at'] = datetime.fromisoformat(doctor_dict['created_at'])
                if doctor_dict.get('updated_at'):
                    doctor_dict['updated_at'] = datetime.fromisoformat(doctor_dict['updated_at'])
                if doctor_dict.get('graduated_at'):
                    doctor_dict['graduated_at'] = datetime.fromisoformat(doctor_dict['graduated_at'])
                    
                return Doctor(**doctor_dict)
        except Exception as e:
            print(f"خطأ في فك تشفير التخزين المؤقت للطبيب {email}: {e}")
    
    doctor = db.query(Doctor).filter(Doctor.email == email).first()
    
    if doctor and settings.REDIS_ENABLED:
        try:
            # تحويل كائن Doctor إلى قاموس للتخزين
            doctor_dict = {
                "id": doctor.id,
                "username": doctor.username,
                "email": doctor.email,
                "hashed_password": doctor.hashed_password,
                "name": doctor.name,
                "specialty": doctor.specialty,
                "hospital": doctor.hospital,
                "lat": doctor.lat,
                "lng": doctor.lng,
                "address": doctor.address,
                "phone": doctor.phone,
                "whatsapp": doctor.whatsapp,
                "rating": doctor.rating,
                "created_at": doctor.created_at.isoformat() if doctor.created_at else None,
                "updated_at": doctor.updated_at.isoformat() if doctor.updated_at else None,
                "is_active": doctor.is_active,
                "graduated_at": doctor.graduated_at.isoformat() if doctor.graduated_at else None,
                "verification_files": doctor.verification_files
            }
            set_cache(f"doctor:{email}", json.dumps(doctor_dict), 300)
        except Exception as e:
            print(f"خطأ في تخزين بيانات الطبيب {email}: {e}")
    
    return doctor

def authenticate_user(
    db: Session,
    email: str,
    password: str
) -> Optional[Dict[str, Any]]:
    user = get_user_by_email(db, email)
    if user and verify_password(password, user.hashed_password):
        return {"user": user, "user_type": "user"}
    
    doctor = get_doctor_by_email(db, email)
    if doctor and verify_password(password, doctor.hashed_password):
        return {"user": doctor, "user_type": "doctor"}
    
    return None

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="تعذر التحقق من بيانات الاعتماد",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        user_type: str = payload.get("user_type")
        if email is None or user_type is None:
            raise credentials_exception
        token_data = TokenData(email=email, user_type=user_type)  # Use email here
    except JWTError:
        raise credentials_exception
    
    if token_data.user_type == "user":
        user = get_user_by_email(db, token_data.email)
        if user is None:
            raise credentials_exception
        return {"user": user, "user_type": "user"}
    elif token_data.user_type == "doctor":
        doctor = get_doctor_by_email(db, token_data.email)
        if doctor is None:
            raise credentials_exception
        return {"user": doctor, "user_type": "doctor"}
    else:
        raise credentials_exception 
async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    # التأكد من أن هذه الدالة لا ترجع خطأ "Inactive user" بدون سبب
    if current_user['user'].is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user