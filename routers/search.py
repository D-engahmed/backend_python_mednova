from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from db.database import get_db
from services.search import SearchService
from schemas.doctor import DoctorOut
from schemas.medicine import MedicineOut
from core.logging import logger

router = APIRouter()

@router.get("/doctor", response_model=List[DoctorOut])
async def search_doctors(
    lat: float = Query(..., description="Latitude of search location"),
    lng: float = Query(..., description="Longitude of search location"),
    specialty: Optional[str] = Query(None, description="Medical specialty filter"),
    limit: int = Query(5, description="Maximum number of results", ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Find doctors near a location with optional specialty filter"""
    try:
        logger.info(f"Searching for doctors near ({lat}, {lng}) with specialty '{specialty}'")
        doctors = SearchService.find_doctors(db, lat, lng, specialty, limit)
        return doctors
    except Exception as e:
        logger.error(f"Doctor search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Doctor search failed: {str(e)}")

@router.get("/medicine", response_model=List[MedicineOut])
async def search_medicines(
    name: str = Query(..., description="Medicine name (partial match)"),
    limit: int = Query(10, description="Maximum number of results", ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Find medicines by name"""
    try:
        logger.info(f"Searching for medicines matching '{name}'")
        medicines = SearchService.find_medicines(db, name, limit)
        return medicines
    except Exception as e:
        logger.error(f"Medicine search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Medicine search failed: {str(e)}")

@router.get("/doctor/{doctor_id}", response_model=DoctorOut)
async def get_doctor_details(doctor_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific doctor"""
    from models.doctor import Doctor
    
    try:
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            raise HTTPException(status_code=404, detail=f"Doctor with ID {doctor_id} not found")
        
        # Convert to dict for response
        doctor_dict = {
            "id": doctor.id,
            "name": doctor.name,
            "specialty": doctor.specialty,
            "hospital": doctor.hospital,
            "lat": doctor.lat,
            "lng": doctor.lng,
            "address": doctor.address,
            "phone": doctor.phone,
            "email": doctor.email,
            "rating": doctor.rating,
            "distance": None  # No distance calculation when looking up by ID
        }
        
        return doctor_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Doctor details error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get doctor details: {str(e)}")

@router.get("/medicine/{medicine_id}", response_model=MedicineOut)
async def get_medicine_details(medicine_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific medicine"""
    from models.medicine import Medicine
    
    try:
        medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
        if not medicine:
            raise HTTPException(status_code=404, detail=f"Medicine with ID {medicine_id} not found")
        return medicine
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Medicine details error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get medicine details: {str(e)}")