from fastapi import APIRouter, UploadFile, HTTPException, BackgroundTasks, Depends, status, File, Form, Request
from typing import Optional, List
from sqlalchemy.orm import Session
import hashlib
import time
import os
from pathlib import Path
import aiofiles
from typing import Dict,Any
from db.database import get_db
from services.inference import InferenceService
from schemas.prediction import TextResponse, ImageResponse, AudioResponse
from models.multimodal import ImageAnalysis, AudioTranscription
from core.logging import logger
from core.security import get_current_active_user
from core.config import settings
from core.cache import redis_client, get_cache, set_cache

router = APIRouter(prefix="/ai", tags=["AI"])

CHUNK_SIZE = 1024 * 1024  # 1MB chunks

async def save_upload_file(file: UploadFile, file_hash: str) -> str:
    """Save uploaded file in chunks"""
    file_ext = os.path.splitext(file.filename)[1]
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    file_path = temp_dir / f"{file_hash}{file_ext}"
    
    async with aiofiles.open(file_path, 'wb') as f:
        while chunk := await file.read(CHUNK_SIZE):
            await f.write(chunk)
            
    return str(file_path)

@router.post("/text", response_model=TextResponse)
async def ai_text(
    request: Request,
    prompt: str = Form(...),
    max_length: Optional[int] = Form(512),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Process text input and return AI-generated medical advice"""
    try:
        # Create unique cache key
        cache_key = f"ai:text:{current_user['user'].email}:{hash(prompt)}:{max_length}"
        
        # Check cache first
        cached_result = get_cache(cache_key)
        if cached_result:
            logger.info(f"Using cached response for {current_user['user'].email}")
            return cached_result
            
        logger.info(f"Processing text request from {current_user['user'].email}")
        
        result = InferenceService.text(prompt, max_length)
        
        # Add recommendation system during chat
        if "recommend" in prompt.lower():
            from services.recommendation import RecommendationService
            recommendations = RecommendationService.recommend_from_chat(prompt)
            result["text"] += f"\n\nRecommendations:\n{recommendations}"
        
        # Cache result for 5 minutes
        set_cache(cache_key, result, 300)
        
        return result
    except Exception as e:
        logger.error(f"Text processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal processing error"
        )

@router.post("/image", response_model=ImageResponse)
async def ai_image(
    file: UploadFile = File(...),
    return_features: Optional[bool] = Form(True),
    analyze: Optional[bool] = Form(True),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Process medical image and return feature vector and/or analysis"""
    try:
        start_time = time.time()
        
        # Read and hash the image file in chunks
        file_hash = hashlib.sha256()
        while chunk := await file.read(CHUNK_SIZE):
            file_hash.update(chunk)
        file_hash = file_hash.hexdigest()
        await file.seek(0)  # Reset file pointer
        
        # Check if we already have this image analyzed
        cache_key = f"ai:image:{file_hash}"
        cached_result = get_cache(cache_key)
        if cached_result:
            logger.info(f"Using cached analysis for image {file_hash[:8]}")
            return cached_result
        
        # Check database cache
        existing_analysis = db.query(ImageAnalysis).filter(ImageAnalysis.file_hash == file_hash).first()
        if existing_analysis:
            logger.info(f"Using database analysis for image {file_hash[:8]}")
            result = {
                "embedding": existing_analysis.get_embedding() if return_features else None,
                "prediction": existing_analysis.prediction if analyze else None,
                "confidence": existing_analysis.confidence if analyze else None,
                "processing_time": time.time() - start_time,
                "model_used": "cache",
                "cached": True
            }
            set_cache(cache_key, result, 3600)  # Cache for 1 hour
            return result
        
        # Save the file in chunks
        file_path = await save_upload_file(file, file_hash)
        
        # Process the image
        result = InferenceService.image(file_path)
        result["processing_time"] = time.time() - start_time
        
        # Store analysis in database in background
        def save_analysis():
            try:
                analysis = ImageAnalysis(
                    filename=file.filename,
                    content_type=file.content_type,
                    file_hash=file_hash,
                    prediction=result.get("prediction"),
                    confidence=result.get("confidence")
                )
                if result.get("embedding"):
                    analysis.set_embedding(result["embedding"])
                db.add(analysis)
                db.commit()
                logger.info(f"Saved image analysis for {file_hash[:8]}")
                set_cache(cache_key, result, 86400)  # Cache for 24 hours
            except Exception as e:
                logger.error(f"Failed to save image analysis: {str(e)}")
                db.rollback()
        
        if background_tasks:
            background_tasks.add_task(save_analysis)
        else:
            save_analysis()
        
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)
            
        return result
    except Exception as e:
        logger.error(f"Image processing error:{str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image processing failed: {str(e)}"
        )

@router.post("/audio", response_model=AudioResponse)
async def ai_audio(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Process audio file and return transcription"""
    try:
        start_time = time.time()
        
        # Read and hash the audio file in chunks
        file_hash = hashlib.sha256()
        while chunk := await file.read(CHUNK_SIZE):
            file_hash.update(chunk)
        file_hash = file_hash.hexdigest()
        await file.seek(0)  # Reset file pointer
        
        # Check cache first
        cache_key = f"ai:audio:{file_hash}"
        cached_result = get_cache(cache_key)
        if cached_result:
            logger.info(f"Using cached transcription for audio {file_hash[:8]}")
            return cached_result
        
        # Check database cache
        existing_transcription = db.query(AudioTranscription).filter(
            AudioTranscription.file_hash == file_hash
        ).first()
        
        if existing_transcription:
            logger.info(f"Using database transcription for audio {file_hash[:8]}")
            result = {
                "transcript": existing_transcription.transcription,
                "language_detected": existing_transcription.language_detected,
                "duration_seconds": existing_transcription.duration_seconds,
                "processing_time": time.time() - start_time,
                "model_used": "cache",
            }
            set_cache(cache_key, result, 3600)  # Cache for 1 hour
            return result
        
        # Save the file in chunks
        file_path = await save_upload_file(file, file_hash)
        
        # Process the audio
        result = InferenceService.audio(file_path)
        result["processing_time"] = time.time() - start_time
        
        # Store transcription in database in background
        def save_transcription():
            try:
                transcription = AudioTranscription(
                    filename=file.filename,
                    content_type=file.content_type,
                    file_hash=file_hash,
                    transcription=result["transcript"],
                    language_detected=result.get("language_detected", "ar"),
                    duration_seconds=result.get("duration_seconds")
                )
                db.add(transcription)
                db.commit()
                logger.info(f"Saved audio transcription for {file_hash[:8]}")
                set_cache(cache_key, result, 86400)  # Cache for 24 hours
            except Exception as e:
                logger.error(f"Failed to save audio transcription: {str(e)}")
                db.rollback()
        
        if background_tasks:
            background_tasks.add_task(save_transcription)
        else:
            save_transcription()
        
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)
            
        return result
    except Exception as e:
        logger.error(f"Audio processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio processing failed: {str(e)}"
        )

@router.post("/recommend")
async def recommend_doctors(
    symptoms: str = Form(...),
    lat: float = Form(...),
    lng: float = Form(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Recommend doctors based on symptoms and location"""
    try:
        cache_key = f"ai:recommend:{current_user['user'].email}:{hash(symptoms)}:{lat}:{lng}"
        cached_result = get_cache(cache_key)
        if cached_result:
            return cached_result
            
        from services.recommendation import RecommendationService
        recommendations = RecommendationService.recommend_doctors(db, symptoms, lat, lng)
        
        # Cache for 1 hour
        set_cache(cache_key, recommendations, 3600)
        
        return recommendations
    except Exception as e: 
        logger.error(f"Recommendation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation failed: {str(e)}"
        )