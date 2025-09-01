from .pydantic_settings import BaseSettings, SettingsConfigDict
import os
from urllib.parse import quote_plus

class Settings(BaseSettings):
    # تكوين قاعدة البيانات
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./medical_database.db")
    POSTGRES_USER: str = "medixai"
    POSTGRES_PASSWORD: str = "health1"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_DB: str = "medical_db"
    TEST_MODE : bool = True
    # نماذج الذكاء الاصطناعي
    HUGGING_FACE_MODEL_NAME: str = "MBZUAI/BiMediX2-4B"
    MEDGEMMA_MODEL: str = "google/medgemma-4b-it"
    
    
    # الأمان
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120  # زيادة مدة الصلاحية
    # إعدادات التطبيق
    USER_NAME_MAX_LENGTH: int = 50
    CORS_ORIGINS: list = ["*"]
    
    # تكوين Redis
    REDIS_ENABLED: bool = False  # تعطيل Redis مؤقتاً لحل المشاكل
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    CACHE_TTL_TEXT: int = 300
    CACHE_TTL_IMAGE: int = 86400
    CACHE_TTL_AUDIO: int = 86400
    CACHE_TTL_RECOMMEND: int = 3600
    
    # بناء عنوان PostgreSQL إذا لم يتم تقديمه
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        # إذا كان DSN يحتوي على sqlite، لا تقم ببناء عنوان PostgreSQL
        if "postgres" not in self.DATABASE_URL.lower():
            return self.DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{quote_plus(self.POSTGRES_PASSWORD)}@{self.POSTGRES_HOST}/{self.POSTGRES_DB}"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
        
settings = Settings()