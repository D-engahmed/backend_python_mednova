from pydantic import BaseModel
from typing import Optional

class MedicineBase(BaseModel):
    name: str
    description: Optional[str] = None
    
class MedicineCreate(MedicineBase):
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    manufacturer: Optional[str] =None
    price: Optional[float] = None
    prescription_required: Optional[bool] = True
    
class MedicineOut(MedicineBase):
    id:int
    dosage_form: Optional[str] = None
    strength : Optional[str] = None
    manufacturer: Optional[str] = None
    price: Optional[float] = None
    prescription_required:Optional[bool] =True
    
    class Config:
        from_attributes = True  # Updated for Pydantic v2