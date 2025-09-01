from pydantic import BaseModel,validator
from typing import Optional,List,Dict,Any
from datetime import datetime

class DoctorBase(BaseModel):
    username: str
    email:str
    name:str
    specialty: str
    lat: float
    lng: float

class DoctorCreate(DoctorBase):
    password:str
    hospital: Optional[str] = None
    address : Optional[str] = None
    phone : Optional[str] = None
    whatsapp : Optional[str] = None
    
    @validator("lat")
    def validate_latitude(cls,v):
        if v < -90 or v > 90:
            raise ValueError("Latitude must be between -90 and 90")
        return v
    @validator("lng")
    def validate_longitude(cls,v):
        if v < -180 or v > 180:
            raise ValueError ('Longitude must be between -180 and 180')
        return v

class DoctorUpdate(BaseModel):
    name: Optional[str] = None
    specialty : Optional[str] = None
    
    hospital: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    
class DoctorOut(DoctorBase):
    id :int
    hospital:Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    rating: Optional[float] = None
    distance: Optional[float] = None   # Distance in km from search location
    create_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # Updated for Pydantic v2

class DoctorLogin(BaseModel):
    username: str
    password: str
    # verification:

class DoctorDashboard(BaseModel):
    doctor:DoctorOut
    patients: List[Dict[str,Any]]
    medical_records: List[Dict[str,Any]]
    
    class Config:
        form_attributes =True