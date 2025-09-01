from sqlalchemy import Column, Float, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from db.database import Base
import datetime
from core.config import settings

class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(
        String(settings.USER_NAME_MAX_LENGTH),
        unique=True,
        nullable=False
    )
    gender = Column(String(50),nullable=False,default="male")
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    license_number = Column(String(100), nullable=False)
    specialty = Column(String(100), nullable=False)
    hospital_affiliation = Column(String(200), nullable=False)
    
    # to be changes for nullable= False
    lng = Column(Float, nullable=True)
    lat = Column(Float, nullable=True)
    address = Column(Text, nullable=True)
    
    years_of_experience = Column(Integer,nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    whatsapp = Column(String(20), nullable=True)
    rating = Column(Float, default=0.0, nullable=False)
    
    
    certifications = Column(String(300), nullable=False)
    education = Column(String(200), nullable=False)
    
    languages_spoken=Column(String(100),default="العربية",nullable=False)
    
    consultation_fee = Column(Float, default=0.0, nullable=False)

    is_active = Column(Boolean, default=True)

    created_at = Column(
        DateTime,
        default=datetime.datetime.now,
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
    )

    patients = relationship(
        "User",
        secondary="user_doctor",
        back_populates="doctors"
    )
    medical_records = relationship(
        "MedicalRecord",
        back_populates="doctor"
    )