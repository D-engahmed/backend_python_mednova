from sqlalchemy import Column, Integer, String, Text, Float, Boolean,DateTime
from db.database import Base

class Medicine(Base):
    __tablename__ = "medicines"
    # meta data
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    # classification data
    category = Column(String(100),nullable=False)
    manufacturer = Column(String(100), nullable=True)
    dosage = Column(String(50), nullable=True)
    price = Column(Float, nullable=True)
    # for avoid some thing
    prescription_required = Column(Boolean, default=True)
    is_sponsored = Column(Boolean, default=False)  # Added for sponsored medicines
    is_available = Column(Boolean, default=True,nullable=False)  
    requires_prescription = Column(Boolean, default=False,nullable=False) 
    expiry_date = Column (DateTime,nullable=False)
    # Effects
    side_effects = Column(String(100),default=None)
    contraindications = Column(Text,default=None)
    interactions = Column(String(100),default=None)
     