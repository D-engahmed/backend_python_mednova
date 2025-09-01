from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import math
from models.doctor import Doctor
from models.medicine import Medicine
from core.logging import logger
from core.config import settings

class SearchService:
    """Service for searching doctors and medicines"""
    
    @staticmethod
    def _calculate_distance(
        lat1: float,
        lng1: float,
        lat2: float,
        lng2: float
    ) -> float:
        """Calculate Haversine distance between two points in kilometers"""
        R = 6371  # Earth radius in km
        
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlng/2) * math.sin(dlng/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    @staticmethod
    def find_doctors(
        db: Session,
        lat: float,
        lng: float,
        specialty: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Find doctors nearest to the given coordinates"""
        try:
            query = db.query(Doctor)
            
            if specialty:
                query = query.filter(Doctor.specialty.ilike(f"%{specialty}%"))
                
            doctors = query.all()
            
            results = []
            for doctor in doctors:
                distance = SearchService._calculate_distance(
                    lat, lng, doctor.lat, doctor.lng
                )
                
                results.append({
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
                    "distance": round(distance, 2)
                })
            
            # Sort by distance and rating
            results.sort(key=lambda x: (x["distance"], -x["rating"]))
            return results[:limit]
        except Exception as e:
            logger.error(f"Error searching for doctors: {str(e)}")
            return []
    
    @staticmethod
    def find_medicines(
        db: Session, 
        name: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Find medicines by name with sponsored first"""
        try:
            # Get sponsored medicines first
            sponsored = db.query(Medicine).filter(
                Medicine.is_sponsored == True,
                Medicine.name.ilike(f"%{name}%")
            ).all()
            
            # Get non-sponsored medicines
            non_sponsored = db.query(Medicine).filter(
                Medicine.is_sponsored == False,
                Medicine.name.ilike(f"%{name}%")
            ).limit(limit - len(sponsored)).all()
            
            # Combine results with sponsored first
            results = [
                {**m.__dict__, "is_sponsored": True} 
                for m in sponsored
            ] + [
                {**m.__dict__, "is_sponsored": False} 
                for m in non_sponsored
            ]
            
            return results[:limit]
        except Exception as e:
            logger.error(f"Error searching for medicines: {str(e)}")
            return []