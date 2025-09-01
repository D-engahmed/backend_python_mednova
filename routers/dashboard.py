from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List, Dict

from db.database import get_db
from models.user import User
from models.medical_record import MedicalRecord
from models.doctor import Doctor
from schemas.user import UserOut, MedicalRecordOut, UserDashboard, MedicalRecordCreate
from schemas.doctor import DoctorOut, DoctorDashboard
from core.security import get_current_active_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/user", response_model=UserDashboard)
async def get_user_dashboard(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    الحصول على لوحة تحكم المستخدم
    """
    if current_user["user_type"] != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ليس لديك الصلاحية للوصول إلى لوحة تحكم المستخدم"
        )
    
    user: User = current_user["user"]
    
    # الحصول على قائمة الأطباء المتابعين للمستخدم
    doctors = []
    for doctor in user.doctors:
        doctors.append({
            "id": doctor.id,
            "name": doctor.name,
            "specialty": doctor.specialty,
            "hospital": doctor.hospital,
            "phone": doctor.phone,
            "email": doctor.email
        })
    
    # الحصول على السجلات الطبية للمستخدم
    medical_records = db.query(MedicalRecord).filter(MedicalRecord.user_id == user.id).all()
    
    return {
        "user": user,
        "doctors": doctors,
        "medical_records": medical_records
    }

@router.get("/doctor", response_model=DoctorDashboard)
async def get_doctor_dashboard(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    الحصول على لوحة تحكم الطبيب
    """
    if current_user["user_type"] != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ليس لديك الصلاحية للوصول إلى لوحة تحكم الطبيب"
        )
    
    doctor: Doctor = current_user["user"]
    
    # الحصول على قائمة المرضى
    patients = []
    for patient in doctor.patients:
        patients.append({
            "id": patient.id,
            "username": patient.username,
            "full_name": patient.full_name,
            "email": patient.email,
            "date_of_birth": patient.date_of_birth,
            "phone_number": patient.phone_number,
            "medical_history": patient.medical_history
        })
    
    # الحصول على السجلات الطبية التي يشرف عليها الطبيب
    medical_records = []
    db_records = db.query(MedicalRecord).filter(MedicalRecord.doctor_id == doctor.id).all()
    for record in db_records:
        user = db.query(User).filter(User.id == record.user_id).first()
        medical_records.append({
            "id": record.id,
            "user_id": record.user_id,
            "patient_name": user.full_name if user else "غير معروف",
            "record_date": record.record_date,
            "diagnosis": record.diagnosis,
            "treatment": record.treatment,
            "notes": record.notes
        })
    
    return {
        "doctor": doctor,
        "patients": patients,
        "medical_records": medical_records
    }

@router.get("/user/{user_id}", response_model=UserDashboard)
async def get_user_dashboard_by_doctor(
    user_id: int,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    الحصول على لوحة تحكم المستخدم من قبل الطبيب
    """
    if current_user["user_type"] != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ليس لديك الصلاحية للوصول إلى لوحة تحكم المستخدم"
        )
    
    doctor: Doctor = current_user["user"]
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    # التحقق مما إذا كان الطبيب مخول بالوصول إلى بيانات هذا المستخدم
    if user not in doctor.patients:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ليس لديك الصلاحية للوصول إلى بيانات هذا المستخدم"
        )
    
    # الحصول على قائمة الأطباء المتابعين للمستخدم
    doctors = []
    for user_doctor in user.doctors:
        doctors.append({
            "id": user_doctor.id,
            "name": user_doctor.name,
            "specialty": user_doctor.specialty,
            "hospital": user_doctor.hospital,
            "phone": user_doctor.phone,
            "email": user_doctor.email
        })
    
    # الحصول على السجلات الطبية للمستخدم
    medical_records = db.query(MedicalRecord).filter(MedicalRecord.user_id == user.id).all()
    
    return {
        "user": user,
        "doctors": doctors,
        "medical_records": medical_records
    }

@router.post("/medical-record", response_model=MedicalRecordOut)
async def create_medical_record(
    record_data: MedicalRecordCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    إنشاء سجل طبي جديد
    """
    if current_user["user_type"] != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ليس لديك الصلاحية لإنشاء سجل طبي"
        )
    
    doctor: Doctor = current_user["user"]
    user = db.query(User).filter(User.id == record_data.user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    # التحقق مما إذا كان الطبيب مخول بالوصول إلى بيانات هذا المستخدم
    if user not in doctor.patients:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ليس لديك الصلاحية للوصول إلى بيانات هذا المستخدم"
        )
    
    # إنشاء سجل طبي جديد
    medical_record = MedicalRecord(
        user_id=record_data.user_id,
        doctor_id=doctor.id,
        diagnosis=record_data.diagnosis,
        treatment=record_data.treatment,
        notes=record_data.notes
    )
    
    db.add(medical_record)
    db.commit()
    db.refresh(medical_record)
    
    return medical_record 