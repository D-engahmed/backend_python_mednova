import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    AutoProcessor,
    WhisperForConditionalGeneration,
    WhisperProcessor
)
import time
from pathlib import Path
from core.config import settings
from core.logging import logger

class ModelLoader:
    """Singleton class to load and cache AI models"""
    
    _instances = {}
    _device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Determine project root dynamically and point to local_ai/bimedx2_local_
    _project_root = Path(__file__).resolve().parents[1]
    _text_model_path = _project_root / "local_ai" / "bimedx2_local_"
    
    @classmethod
    def _get_model_path(cls) -> str:
        """Get base model path"""
        return str(cls._text_model_path)

    @classmethod
    def _load_model(cls, model_name, model_type="text"):
        """Load a model directly from Hugging Face Hub"""
        if model_type not in cls._instances:
            logger.info(f"Loading {model_type} model: {model_name}")
            start_time = time.time()
            
            try:
                if model_type == "text":
                    if settings.TEST_MODE:
                        model_name = cls._get_model_path()
                    
                    tokenizer = AutoTokenizer.from_pretrained(
                        model_name,
                        trust_remote_code=True,
                        local_files_only=True,
                        use_fast=True,
                    )
                    model = AutoModelForCausalLM.from_pretrained(
                        model_name,
                        torch_dtype=torch.float16 if cls._device == "cuda" else torch.float32,
                        trust_remote_code=True,
                        local_files_only=True,
                        device_map="auto" if cls._device == "cuda" else None
                    )
                    if cls._device != "cuda":
                        model = model.to(cls._device)
                    cls._instances[model_type] = (model, tokenizer)
                
                elif model_type == "image":
                    # Load image model directly from Hugging Face Hub
                    processor = AutoProcessor.from_pretrained(
                        model_name,
                        trust_remote_code=True
                    )
                    model = AutoModelForCausalLM.from_pretrained(
                        model_name,
                        torch_dtype=torch.float16 if cls._device == "cuda" else torch.float32,
                        trust_remote_code=True,
                        device_map="auto" if cls._device == "cuda" else None
                    )
                    if cls._device != "cuda":
                        model = model.to(cls._device)
                    cls._instances[model_type] = (model, processor)
                
                # elif model_type == "audio":
                #     # Load audio model directly from Hugging Face Hub
                #     processor = WhisperProcessor.from_pretrained(model_name)
                #     model = WhisperForConditionalGeneration.from_pretrained(
                #         model_name,
                #         torch_dtype=torch.float16 if cls._device == "cuda" else torch.float32
                #     ).to(cls._device)
                #     model.config.forced_decoder_ids = None
                #     cls._instances[model_type] = (model, processor)
                
                # load_time = time.time() - start_time
                # logger.info(f"{model_type.capitalize()} model loaded in {load_time:.2f}s")
            
            except Exception as e:
                logger.error(f"Error loading {model_type} model: {str(e)}")
                raise
        
        return cls._instances[model_type]
    
    @classmethod
    def get_text_model(cls):
        return cls._load_model(settings.HUGGING_FACE_MODEL_NAME, "text")
    
    @classmethod
    def get_image_model(cls):
        return cls._load_model(settings.MEDGEMMA_MODEL, "image")
    
    # @classmethod
    # def get_audio_model(cls):
    #     return cls._load_model(settings.SPEECH_MODEL, "audio")
    
    @classmethod
    def unload_models(cls):
        """Unload all models to free memory"""
        for model_type, model_tuple in cls._instances.items():
            if model_tuple and len(model_tuple) >= 1:
                model = model_tuple[0]
                if hasattr(model, 'cpu'):
                    model.cpu()
                del model_tuple
        cls._instances = {}
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("All models unloaded")