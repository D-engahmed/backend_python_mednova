import datetime
from db.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey

class MedicalRecord(Base):
    __tablename__ = "medical_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    
    diagnosis = Column(Text, nullable=True)
    treatment = Column(Text, nullable=True)
    symptoms = Column(Text, nullable=True)
    prescription = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.now)
    follow_up_date = Column(DateTime, default=datetime.datetime.now)
    
 
    
    user = relationship("User", back_populates="medical_records")
    doctor = relationship("Doctor", back_populates="medical_records")