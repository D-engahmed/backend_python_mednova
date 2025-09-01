# prediction.py
from pydantic import BaseModel
from typing import Optional,List,Dict,Any

class TextResponse(BaseModel):
    text:str
    processing_time: float
    model_used:str
    
class ImageResponse(BaseModel):
    embedding: Optional[List[float]] = None
    prediction: Optional[str] = None
    confidence: Optional[float] = None
    processing_time: float
    model_used: str
    
class AudioResponse(BaseModel):
    transcript: str
    language_detected: Optional[str] = None
    duration_seconds: Optional[str] = None
    duration_seconds: float
    model_used: str
    
class ErrorResponse(BaseModel):
    error: str
    details: Optional[Dict[str,Any]] = None