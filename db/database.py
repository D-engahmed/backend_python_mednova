from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings
import re

# تحديد معاملات الاتصال بناءً على نوع قاعدة البيانات
connect_args = {}

# استخدم تعبير منتظم للتحقق من وجود "sqlite" في DSN
if re.search(r'sqlite', settings.DATABASE_URL, re.IGNORECASE):
    connect_args = {"check_same_thread": False}

# إنشاء محرك قاعدة البيانات
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args=connect_args
)

# إنشاء جلسة قاعدة البيانات
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# القاعدة للنماذج
Base = declarative_base()

def get_db():
    """الحصول على جلسة قاعدة البيانات"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """تهيئة قاعدة البيانات"""
    try:
        # استيراد جميع النماذج
        from models import doctor, user, medicine, multimodal, medical_record
        
        # إنشاء الجداول
        Base.metadata.create_all(bind=engine)
        print("✅ تم إنشاء جداول قاعدة البيانات بنجاح")
        
        # تشغيل الترحيلات إذا لزم الأمر
        run_alembic_upgrade()
        
    except Exception as e:
        print(f"❌ فشل تهيئة قاعدة البيانات: {e}")
        raise

def run_alembic_upgrade():
    """تشغيل ترحيلات Alembic"""
    try:
        from alembic.config import Config
        from alembic import command
        
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("✅ تم تطبيق ترحيلات قاعدة البيانات")
    except Exception as e:
        print(f"⚠️ تم تخطي ترحيلات Alembic: {e}")