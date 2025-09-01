from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, Text, Float, DateTime
import json
from db.database import Base

class ImageAnalysis(Base):
    __tablename__ = "image_analyses"
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(50), nullable=True)
    file_hash = Column(String(64), unique=True, index=True)
    embedding = Column(Text, nullable=True)
    prediction = Column(String(255), nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=func.now())  # تم إزالة timezone=True

    def set_embedding(self, embedding_vector):
        self.embedding = json.dumps(embedding_vector)

    def get_embedding(self):
        return json.loads(self.embedding) if self.embedding else None

class AudioTranscription(Base):
    __tablename__ = "audio_transcriptions"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(225), nullable=True)
    content_type = Column(String(50), nullable=True)
    file_hash = Column(String(64), unique=True, index=True)
    transcription = Column(Text, nullable=True)
    language_detected = Column(String(10), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    created_at = Column(DateTime, default=func.now())  # تم إزالة timezone=True