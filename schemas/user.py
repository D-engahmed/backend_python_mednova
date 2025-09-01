from pydantic import BaseModel
from typing import Optional,List,Dict,Any
from datetime import datetime ,date

class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    
class UserCreate(UserBase):
    password: str
    date_of_birth: Optional[date] = None
    phone_number: Optional[str] = None
    gender: Optional[str] = None
    address: Optional [str] = None
    medical_history: Optional[str] = None
    
class UserUpdate(BaseModel):
    full_name: Optional[str] =None
    phone_number: Optional[str] = None
    address: Optional [str] = None
    medical_history: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
        
class UserOut(UserBase):
    id:int
    data_of_birth: Optional[date] = None
    phone_number:Optional[str] = None
    address: Optional[str] = None
    medical_history: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
        
        
class UserLogin(UserBase):
    username: str
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    email: Optional[str] = None  # Changed from username to email
    user_type: Optional[str] = None
class MedicalRecordBase(BaseModel):
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    notes: Optional[str] = None
    
class MedicalRecordCreate(MedicalRecordBase):
    user_id: int
    
class MedicalRecordOut(MedicalRecordBase):
    id: int
    user_id: int
    doctor_id: int
    record_data: datetime

class Config:
    from_attributes = True
    
class UserDashboard(BaseModel):
    user: UserOut
    doctors: List[Dict[str, Any]]
    medical_records: List[MedicalRecordOut]
    
    class Config:
        from_attributes = True