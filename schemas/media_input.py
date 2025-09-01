from pydantic import BaseModel ,Field
from typing import Optional

class TextInput(BaseModel):
    prompt: str =Field(...,
                       description="The medical text query or description of symptoms")
    max_length: Optional[int]= Field(512,
                                     description="Maximum length of response")
    
class AudioInput(BaseModel):
    language: Optional[str] =Field(...,
                                   description= "Expected language of the audio")
    
class ImageInput(BaseModel):
    return_features: Optional[bool] = Field(True,
                                            description="Whether to return feature embeddings")
    analyze: Optional[bool] = Field(True,
                                    description="Whether to analyze the image")