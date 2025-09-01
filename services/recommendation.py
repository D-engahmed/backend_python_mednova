from typing import Dict, Any, List
from sqlalchemy.orm import Session
from services.inference import InferenceService
from services.search import SearchService
from core.logging import logger

class RecommendationService:
    """Service for generating recommendations based on AI analysis"""
    
    @staticmethod
    def recommend_from_chat(chat_history: str) -> str:
        """Generate recommendations from chat context"""
        try:
            prompt = f"""
            Based on the following medical conversation, provide recommendations for the patient:
            {chat_history}
            
            Recommendations should include:
            1. Suggested doctors if needed
            2. Recommended medicines if applicable
            3. Lifestyle advice
            4. Follow-up instructions
            
            Keep the response concise and professional.
            """
            
            response = InferenceService.text(prompt, max_length=512)
            return response["text"]
        except Exception as e:
            logger.error(f"Recommendation from chat error: {str(e)}")
            return "I recommend consulting with a healthcare professional for personalized advice."
    
    @staticmethod
    def recommend_doctors(
        db: Session,
        symptoms: str,
        lat: float,
        lng: float,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Recommend doctors based on symptom description and location"""
        try:
            # First, determine the specialty needed
            specialty = RecommendationService._recommend_specialty(symptoms)
            
            # Then find doctors with that specialty
            doctors = SearchService.find_doctors(db, lat, lng, specialty, limit)
            
            return {
                "specialty": specialty,
                "doctors": doctors,
            }
        except Exception as e:
            logger.error(f"Error in doctor recommendation: {str(e)}")
            return {
                "specialty": "General Medicine",
                "doctors": []
            }
    
    @staticmethod
    def _recommend_specialty(text_description: str) -> str:
        """Extract medical specialty from symptom description"""
        try:
            prompt = f"""
            Based on the following patient symptoms, identify the most relevant medical specialty:
            Symptoms: {text_description}
            
            Return only the name of the medical specialty.
            """
            
            response = InferenceService.text(prompt, max_length=128)
            return response["text"].strip()
        except Exception as e:
            logger.error(f"Error recommending specialty: {str(e)}")
            return "General Medicine"