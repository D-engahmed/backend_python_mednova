import datetime
from db.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Table, Boolean

# Association table for user-doctor relationship
user_doctor = Table(
    "user_doctor",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("doctor_id", Integer, ForeignKey("doctors.id"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(150), nullable=False, unique=True)
    hashed_password = Column(String(128), nullable=False)
    full_name = Column(String(100), nullable=False)
    gender = Column(String(50),nullable=False,default="male")
    date_of_birth = Column(DateTime, nullable=False)
    phone = Column(String(20), nullable=False, unique=True)
    gender = Column(String(7))

    address = Column(Text, nullable=True)
    medical_history = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now
    )
    
    doctors = relationship(
        "Doctor",
        secondary=user_doctor,
        back_populates="patients"
    )
    medical_records = relationship(
        "MedicalRecord",
        back_populates="user"
    )