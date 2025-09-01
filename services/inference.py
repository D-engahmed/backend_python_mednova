import time
import torch
from PIL import Image
from typing import Dict, Any
import numpy as np
import librosa

from utils.model_loader import ModelLoader
from core.logging import logger
from core.config import settings

class InferenceService:
    """Service for running AI inference on text, images, and audio"""
    
    @staticmethod
    def text(prompt: str, max_length: int = 512) -> Dict[str, Any]:
        """Run text-to-text inference using BiMediX2"""
        start_time = time.time()
        try:
            model, tokenizer = ModelLoader.get_text_model()
            
            inputs = tokenizer(
                prompt,
                return_tensors="pt",
                max_length=512,
                truncation=True
            ).to(model.device)
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_length=max_length,
                    num_beams=4,
                    no_repeat_ngram_size=3,
                    early_stopping=True
                )
                
            result = tokenizer.decode(
                outputs[0],
                skip_special_tokens=True
            )
            
            processing_time = time.time() - start_time
            logger.info(f"Text inference completed in {processing_time:.2f}s")
            
            return {
                "text": result,
                "processing_time": processing_time,
                "model_used": settings.HUGGING_FACE_MODEL_NAME
            }
        except Exception as e:
            logger.error(f"Text inference error: {str(e)}")
            raise
    
    @staticmethod
    def image(file_path: str) -> Dict[str, Any]:
        """Run image inference using MedGemma"""
        start_time = time.time()
        try:
            model, processor = ModelLoader.get_image_model()
            
            # Load and process image
            image = Image.open(file_path).convert("RGB")
            inputs = processor(
                images=image,
                return_tensors="pt"
            ).to(model.device)
            
            # Generate predictions
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                predicted_class_idx = logits.argmax(-1).item()
                confidence = torch.softmax(logits, dim=-1)[0, predicted_class_idx].item()
                
                # Get label (simplified)
                labels = ["Normal", "Abnormal"]
                prediction = labels[predicted_class_idx] if predicted_class_idx < len(labels) else "Unknown"
            
            processing_time = time.time() - start_time
            logger.info(f"Image inference completed in {processing_time:.2f}s")
            
            return {
                "prediction": prediction,
                "confidence": confidence,
                "processing_time": processing_time,
                "model_used": settings.MEDGEMMA_MODEL
            }
        except Exception as e:
            logger.error(f"Image inference error: {str(e)}")
            raise
    
    @staticmethod
    def audio(file_path: str) -> Dict[str, Any]:
        """Transcribe audio using Whisper Medical Arabic"""
        start_time = time.time()
        try:
            model, processor = ModelLoader.get_audio_model()
            
            # Load audio file
            audio, sr = librosa.load(file_path, sr=16000)
            duration = librosa.get_duration(y=audio, sr=sr)
            
            # Process audio
            inputs = processor(
                audio,
                sampling_rate=sr,
                return_tensors="pt"
            ).to(model.device)
            
            # Generate transcription
            with torch.no_grad():
                outputs = model.generate(**inputs)
                transcription = processor.batch_decode(
                    outputs, 
                    skip_special_tokens=True
                )[0]
            
            processing_time = time.time() - start_time
            logger.info(f"Audio transcription completed in {processing_time:.2f}s")
            
            return {
                "transcript": transcription,
                "language_detected": "ar",
                "duration_seconds": duration,
                "processing_time": processing_time,
                "model_used": settings.SPEECH_MODEL
            }
        except Exception as e:
            logger.error(f"Audio inference error: {str(e)}")
            raise