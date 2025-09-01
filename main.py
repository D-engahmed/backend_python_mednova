import os
import time
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.logging import logger
from db.database import init_db
from routers import ai, healthcheck, auth, dashboard, search
from utils.model_loader import ModelLoader

# Preload models at startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Starting Medical AI API")
    
    try:
        # Initialize database
        init_db()
        
        # Preload models directly from Hugging Face Hub
        logger.info("Preloading AI models from Hugging Face Hub...")
        # ModelLoader.get_text_model()
        # ModelLoader.get_image_model()
        # ModelLoader.get_audio_model()
        logger.info("All models loaded successfully")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
    
    yield
    
    logger.info("Shutting down Medical AI API")
    # ModelLoader.unload_models()

app = FastAPI(
    title="Medical AI API",
    description="API for medical text analysis, image processing, and doctor/medicine search",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include routers
app.include_router(healthcheck.router)
app.include_router(ai.router)
app.include_router(search.router)
app.include_router(auth.router)
app.include_router(dashboard.router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "Medical AI API",
        "version": "1.0.0",
        "status": "online",
        "models": {
            "text": settings.HUGGING_FACE_MODEL_NAME,
            # "image": settings.MEDGEMMA_MODEL,
            # "audio": settings.SPEECH_MODEL
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.1",
        port=5000,
        reload=True,
        workers=1
    )