import sys
import os

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)

from sqlalchemy.orm import Session
from db.database import SessionLocal, engine
from models import User, Doctor, Medicine, MedicalRecord, AudioTranscription, ImageAnalysis, UserDoctor
from passlib.context import CryptContext
from datetime import datetime, timedelta
import json
import hashlib

# إعداد التشفير
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_sample_data():
    db = SessionLocal()
    
    try:
        # # إنشاء المستخدمين
        # print("إنشاء المستخدمين...")
        # users = [
        #     User(
        #         username="ahmed_ali",
        #         email="ahmed@example.com",
        #         hashed_password=hash_password("password123"),
        #         full_name="أحمد علي محمد",
        #         phone="01234567890",
        #         date_of_birth=datetime(1990, 5, 15),
        #         gender="male",
        #         address="القاهرة، مصر",
        #         is_active=True
        #     ),
        #     User(
        #         username="fatima_hassan",
        #         email="fatima@example.com",
        #         hashed_password=hash_password("password123"),
        #         full_name="فاطمة حسن أحمد",
        #         phone="01234567891",
        #         date_of_birth=datetime(1985, 3, 22),
        #         gender="female",
        #         address="الإسكندرية، مصر",
        #         is_active=True
        #     ),
        #     User(
        #         username="omar_ibrahim",
        #         email="omar@example.com",
        #         hashed_password=hash_password("password123"),
        #         full_name="عمر إبراهيم محمود",
        #         phone="01234567892",
        #         date_of_birth=datetime(1992, 8, 10),
        #         gender="male",
        #         address="الجيزة، مصر",
        #         is_active=True
        #     ),
        #     User(
        #         username="sara_mohamed",
        #         email="sara@example.com",
        #         hashed_password=hash_password("password123"),
        #         full_name="سارة محمد عبدالله",
        #         phone="01234567893",
        #         date_of_birth=datetime(1988, 12, 5),
        #         gender="female",
        #         address="المنصورة، مصر",
        #         is_active=True
        #     ),
        #     User(
        #         username="khalid_ahmed",
        #         email="khalid@example.com",
        #         hashed_password=hash_password("password123"),
        #         full_name="خالد أحمد عبدالرحمن",
        #         phone="01234567894",
        #         date_of_birth=datetime(1995, 7, 18),
        #         gender="male",
        #         address="أسوان، مصر",
        #         is_active=True
        #     )
        # ]
        
        # db.add_all(users)
        # db.commit()
        # db.refresh(users)
        # # إنشاء الأطباء
        print("create doctors .....")
        doctors = [
            Doctor(
                id=1,
                username="dr_smith",
                gender="male",
                email="john.smith@medclinic.com",
                hashed_password="hashed_password_123",
                license_number="MED123456",
                specialty="Cardiology",
                hospital_affiliation="City General Hospital",
                lng=35.2345,
                lat=31.8765,
                address="123 Medical St, Health City",
                years_of_experience=12,
                phone="+1234567890",
                whatsapp="+1234567890",
                rating=4.7,
                certifications="Board Certified Cardiologist, ACLS",
                education="MD, Harvard Medical School",
                languages_spoken="English, Arabic",
                consultation_fee=150.00,
                is_active=True,
                created_at=datetime(2023, 5, 15, 10, 30),
                updated_at=datetime(2024, 1, 20, 14, 15)
            ),
            Doctor(
                id=2,
                username="dr_ali",
                gender="male",
                email="ahmed.ali@medcare.org",
                hashed_password="hashed_password_456",
                license_number="MED654321",
                specialty="Pediatrics",
                hospital_affiliation="Children's Specialist Hospital",
                years_of_experience=8,
                phone="+0987654321",
                rating=4.9,
                certifications="FAAP, Pediatric Advanced Life Support",
                education="MD, Cairo University",
                languages_spoken="Arabic, English, French",
                consultation_fee=120.00
            ),
            # Doctor(
            #     name="د. أحمد صلاح",
            #     specialty="جراحة عامة",
            #     phone="01333333333",
            #     email="dr.ahmed@hospital.com",
            #     license_number="MED003",
            #     hospital_affiliation="مستشفى دار الفؤاد",
            #     years_of_experience=20,
            #     education="بكالوريوس طب وجراحة - جامعة الإسكندرية",
            #     certifications="زمالة الجراحة العامة - الكلية الملكية للجراحين",
            #     languages_spoken="العربية، الإنجليزية",
            #     consultation_fee=250.0,
            #     gender="male",
            #     is_active=True
            # ),
            # Doctor(
            #     name="د. سلمى محمود",
            #     specialty="أمراض نساء وتوليد",
            #     phone="01444444444",
            #     email="dr.salma@hospital.com",
            #     license_number="MED004",
            #     hospital_affiliation="مستشفى الولادة والأطفال",
            #     years_of_experience=18,
            #     education="بكالوريوس طب وجراحة - جامعة المنصورة",
            #     certifications="دكتوراه أمراض النساء والتوليد",
            #     languages_spoken="العربية، الإنجليزية",
            #     consultation_fee=220.0,
            #     gender="female",
            #     is_active=True
            # ),
            # Doctor(
            #     name="د. يوسف حسن",
            #     specialty="طب قلب",
            #     phone="01555555555",
            #     email="dr.youssef@hospital.com",
            #     license_number="MED005",
            #     hospital_affiliation="معهد القلب القومي",
            #     years_of_experience=25,
            #     education="بكالوريوس طب وجراحة - جامعة القاهرة",
            #     certifications="زمالة طب القلب - الجمعية الأوروبية لطب القلب",
            #     languages_spoken="العربية، الإنجليزية، الألمانية",
            #     consultation_fee=300.0,
            #     gender="male",
            #     is_active=True
            # )
        ]
        
        db.add_all(doctors)
        # db.commit(doctors)
        db.refresh(doctors)
        db.close_all()
        # # إنشاء الأدوية
        # print("إنشاء الأدوية...")
        # medicines = [
        #     Medicine(
        #         name="باراسيتامول",
        #         description="مسكن للألم وخافض للحرارة",
        #         category="مسكنات",
        #         dosage="500 مجم",
                
        #         side_effects="غثيان، دوار، طفح جلدي نادر",
        #         contraindications="حساسية للمادة الفعالة، أمراض الكبد الشديدة",
        #         interactions="الوارفارين، الكحول",
        #         price=15.0,#✔
        #         manufacturer="شركة الأدوية المصرية",#✔
        #         expiry_date=datetime(2025, 12, 31),
        #         requires_prescription=False,#✔
        #         is_sponsored=False,#✔
        #         is_available=True#✔
        #     ),
        #     Medicine(
        #         name="أموكسيسيلين",
        #         description="مضاد حيوي واسع المدى",
        #         category="مضادات حيوية",
        #         dosage="500 مجم",
        #         side_effects="إسهال، غثيان، طفح جلدي",
        #         contraindications="حساسية للبنسلين",
        #         interactions="الوارفارين، حبوب منع الحمل",
        #         price=25.0,
        #         manufacturer="فايزر",
        #         expiry_date=datetime(2026, 6, 30),
        #         requires_prescription=True,
        #         is_sponsored=True,
        #         is_available=True
        #     ),
        #     Medicine(
        #         name="إيبوبروفين",
        #         description="مسكن ومضاد للالتهاب",
        #         category="مسكنات",
        #         dosage="400 مجم",
        #         side_effects="آلام المعدة، دوار، صداع",
        #         contraindications="قرحة المعدة، أمراض القلب الشديدة",
        #         interactions="الوارفارين، الأسبرين",
        #         price=20.0,
        #         manufacturer="نوفارتيس",
        #         expiry_date=datetime(2025, 9, 15),
        #         requires_prescription=False,
        #         is_sponsored=False,
        #         is_available=True
        #     ),
        #     Medicine(
        #         name="لوساكور",
        #         description="خافض لضغط الدم",
        #         category="أدوية القلب",
        #         dosage="50 مجم",
        #         side_effects="دوار، إرهاق، سعال جاف",
        #         contraindications="الحمل، أمراض الكلى الشديدة",
        #         interactions="مدرات البول، مضادات الالتهاب",
        #         price=45.0,
        #         manufacturer="سانوفي",
        #         expiry_date=datetime(2026, 3, 20),
        #         requires_prescription=True,
        #         is_sponsored=True,
        #         is_available=True
        #     ),
        #     Medicine(
        #         name="أوميبرازول",
        #         description="مثبط مضخة البروتون لعلاج الحموضة",
        #         category="أدوية الجهاز الهضمي",
        #         dosage="20 مجم",
        #         side_effects="صداع، إسهال، آلام البطن",
        #         contraindications="حساسية للمادة الفعالة",
        #         interactions="كلوبيدوجريل، الوارفارين",
        #         price=30.0,
        #         manufacturer="أسترازينيكا",
        #         expiry_date=datetime(2025, 11, 10),
        #         requires_prescription=False,
        #         is_sponsored=False,
        #         is_available=True
        #     ),
        #     Medicine(
        #         name="سيمفاستاتين",
        #         description="خافض للكوليسترول",
        #         category="أدوية القلب",
        #         dosage="20 مجم",
        #         side_effects="آلام العضلات، صداع، مشاكل هضمية",
        #         contraindications="أمراض الكبد النشطة، الحمل والرضاعة",
        #         interactions="الوارفارين، أدوية القلب الأخرى",
        #         price=35.0,
        #         manufacturer="مرك",
        #         expiry_date=datetime(2026, 1, 25),
        #         requires_prescription=True,
        #         is_sponsored=False,
        #         is_available=True
        #     ),
        #     Medicine(
        #         name="ميتفورمين",
        #         description="دواء لعلاج السكري من النوع الثاني",
        #         category="أدوية السكري",
        #         dosage="850 مجم",
        #         side_effects="غثيان، إسهال، انتفاخ",
        #         contraindications="أمراض الكلى الشديدة، الحموضة اللاكتيكية",
        #         interactions="الكحول، مدرات البول",
        #         price=40.0,
        #         manufacturer="جلاكسو سميث كلاين",
        #         expiry_date=datetime(2025, 8, 30),
        #         requires_prescription=True,
        #         is_sponsored=True,
        #         is_available=True
        #     ),
        #     Medicine(
        #         name="فيتامين د3",
        #         description="مكمل غذائي لتقوية العظام",
        #         category="فيتامينات",
        #         dosage="1000 وحدة دولية",
        #         side_effects="نادرة عند الجرعات الطبيعية",
        #         contraindications="فرط كالسيوم الدم",
        #         interactions="الديجوكسين، مدرات البول",
        #         price=18.0,
        #         manufacturer="إيفا فارما",
        #         expiry_date=datetime(2026, 5, 15),
        #         requires_prescription=False,
        #         is_sponsored=False,
        #         is_available=True
        #     )
        # ]
        
        # db.add_all(medicines)
        # db.commit()
        # db.refresh(medicines)
        # # إنشاء السجلات الطبية
        # print("إنشاء السجلات الطبية...")
        # medical_records = [
        #     MedicalRecord(
        #         user_id=1,
        #         doctor_id=1,
        #         diagnosis="التهاب الحلق الحاد",
        #         treatment="أموكسيسيلين 500 مجم كل 8 ساعات لمدة 7 أيام",
        #         notes="المريض يعاني من التهاب حلق بكتيري، يحتاج للراحة وشرب السوائل",
        #         created_at=datetime(datetime.now() - timedelta(days=5)),
        #         symptoms="ألم في الحلق، حمى، صعوبة في البلع",
        #         prescription="أموكسيسيلين، باراسيتامول عند الحاجة",
                
        #         follow_up_date=datetime.now() + timedelta(days=7)
                
        #         # vital_signs={"temperature": 38.2, "blood_pressure": "120/80", "heart_rate": 85},
        #     ),
        #     MedicalRecord(
        #         user_id=2,
        #         doctor_id=2,
        #         diagnosis="التهاب الأذن الوسطى",
        #         symptoms="ألم في الأذن، حمى خفيفة، فقدان سمع مؤقت",
        #         treatment="مضاد حيوي موضعي وقطرات للأذن",
        #         prescription="قطرات أذن مضاد حيوي، باراسيتامول للألم",
        #         notes="التهاب أذن وسطى بسيط، يحتاج لمتابعة خلال أسبوع",
        #         follow_up_date=datetime.now() + timedelta(days=7),
        #         # vital_signs={"temperature": 37.8, "blood_pressure": "115/75", "heart_rate": 78},
        #         created_at=datetime.now() - timedelta(days=3)
        #     ),
        #     MedicalRecord(
        #         user_id=3,
        #         doctor_id=3,
        #         diagnosis="التهاب المرارة الحاد",
        #         symptoms="ألم شديد في الجانب الأيمن العلوي، غثيان، قيء",
        #         treatment="مضادات حيوية وريدية، مسكنات قوية",
        #         prescription="سيبروفلوكساسين، مورفين للألم",
        #         notes="يحتاج لجراحة استئصال المرارة خلال الأسبوع القادم",
        #         follow_up_date=datetime.now() + timedelta(days=2),
        #         # vital_signs={"temperature": 39.1, "blood_pressure": "140/90", "heart_rate": 95},
        #         created_at=datetime.now() - timedelta(days=1)
        #     ),
        #     MedicalRecord(
        #         user_id=4,
        #         doctor_id=4,
        #         diagnosis="متابعة حمل طبيعي",
        #         symptoms="لا توجد أعراض مقلقة",
        #         treatment="فيتامينات الحمل والمتابعة الدورية",
        #         prescription="حمض الفوليك، فيتامينات متعددة للحمل",
        #         notes="الحمل يسير بشكل طبيعي، الجنين في وضع جيد",
        #         follow_up_date=datetime.now() + timedelta(days=30),
        #         # vital_signs={"temperature": 36.8, "blood_pressure": "110/70", "heart_rate": 72},
        #         created_at=datetime.now() - timedelta(days=10)
        #     ),
        #     MedicalRecord(
        #         user_id=5,
        #         doctor_id=5,
        #         diagnosis="ارتفاع ضغط الدم الأساسي",
        #         symptoms="صداع، دوار، خفقان",
        #         treatment="أدوية خافضة لضغط الدم ونظام غذائي",
        #         prescription="لوساكور 50 مجم يومياً، تقليل الملح",
        #         notes="المريض يحتاج لتغيير نمط الحياة والمتابعة الدورية",
        #         follow_up_date=datetime.now() + timedelta(days=14),
        #         # vital_signs={"temperature": 36.9, "blood_pressure": "150/95", "heart_rate": 88},
        #         created_at=datetime.now() - timedelta(days=7)
        #     )
        # ]
        
        # db.add_all(medical_records)
        # db.commit()
        # db.refresh(medical_records)
        # # إنشاء تحليلات الصور
        # # print("إنشاء تحليلات الصور...")
        # # image_analyses = [
        # #     ImageAnalysis(
        # #         user_id=1,
        # #         image_path="/uploads/xray_chest_001.jpg",
        # #         file_hash=hashlib.md5(b"sample_image_1").hexdigest(),
        # #         analysis_result="صورة أشعة صدر طبيعية، لا توجد علامات التهاب أو عدوى",
        # #         confidence_score=0.92,
        # #         model_used="medical_vision_model_v1",
        # #         image_type="أشعة سينية",
        # #         body_part="الصدر",
        # #         findings="رئتان سليمتان، قلب بحجم طبيعي",
        # #         created_at=datetime.now() - timedelta(days=2)
        # #     ),
        # #     ImageAnalysis(
        # #         user_id=2,
        # #         image_path="/uploads/mri_brain_001.jpg",
        # #         file_hash=hashlib.md5(b"sample_image_2").hexdigest(),
        # #         analysis_result="أشعة مقطعية للدماغ تُظهر بنية طبيعية",
        # #         confidence_score=0.88,
        # #         model_used="medical_vision_model_v1",
        # #         image_type="أشعة مقطعية",
        # #         body_part="الدماغ",
        # #         findings="لا توجد آفات أو نزيف، بنية الدماغ طبيعية",
        # #         created_at=datetime.now() - timedelta(days=5)
        # #     ),
        # #     ImageAnalysis(
        # #         user_id=3,
        # #         image_path="/uploads/ultrasound_abdomen_001.jpg",
        # #         file_hash=hashlib.md5(b"sample_image_3").hexdigest(),
        # #         analysis_result="سونار البطن يُظهر التهاب في المرارة",
        # #         confidence_score=0.85,
        # #         model_used="medical_vision_model_v1",
        # #         image_type="موجات فوق صوتية",
        # #         body_part="البطن",
        # #         findings="سماكة جدار المرارة، وجود حصوات",
        # #         created_at=datetime.now() - timedelta(days=1)
        # #     )
        # # ]
        
        # # db.add_all(image_analyses)
        # # db.commit()
        # # db.refresh(image_analyses)
        # # # إنشاء تسجيلات صوتية
        # # print("إنشاء التسجيلات الصوتية...")
        # # audio_transcriptions = [
        # #     AudioTranscription(
        # #         user_id=1,
        # #         audio_path="/uploads/audio_001.wav",
        # #         transcription="أعاني من ألم في الحلق منذ ثلاثة أيام، والألم يزداد عند البلع. كما أعاني من حمى وتعب عام.",
        # #         confidence_score=0.94,
        # #         model_used="whisper-medical-arabic",
        # #         duration=45.2,
        # #         language="ar",
        # #         created_at=datetime.now() - timedelta(days=5)
        # #     ),
        # #     AudioTranscription(
        # #         user_id=2,
        # #         audio_path="/uploads/audio_002.wav",
        # #         transcription="طفلي يعاني من ألم في الأذن ويبكي كثيراً، خاصة في الليل. لاحظت أنه لا يسمع جيداً.",
        # #         confidence_score=0.89,
        # #         model_used="whisper-medical-arabic",
        # #         duration=38.7,
        # #         language="ar",
        # #         created_at=datetime.now() - timedelta(days=3)
        # #     ),
        # #     AudioTranscription(
        # #         user_id=3,
        # #         audio_path="/uploads/audio_003.wav",
        # #         transcription="أشعر بألم شديد في الجانب الأيمن من البطن، والألم بدأ من أمس. كما أعاني من غثيان وقيء.",
        # #         confidence_score=0.91,
        # #         model_used="whisper-medical-arabic",
        # #         duration=42.5,
        # #         language="ar",
        # #         created_at=datetime.now() - timedelta(days=1)
        # #     )
        # # ]
        
        # # db.add_all(audio_transcriptions)
        # # db.commit()
        # # db.refresh(audio_transcriptions)
        
        # # إنشاء علاقات المستخدمين والأطباء
        # print("إنشاء علاقات المستخدمين والأطباء...")
        # user_doctor_relations = [
        #     UserDoctor(user_id=1, doctor_id=1),
        #     UserDoctor(user_id=2, doctor_id=2),
        #     UserDoctor(user_id=3, doctor_id=3),
        #     UserDoctor(user_id=4, doctor_id=4),
        #     UserDoctor(user_id=5, doctor_id=5),
        #     UserDoctor(user_id=1, doctor_id=5),  # مريض يتابع مع طبيبين
        #     UserDoctor(user_id=2, doctor_id=1),  # مريض آخر يتابع مع طبيبين
        # ]
        
        # db.add_all(user_doctor_relations)
        # db.commit()
        # db.refresh(user_doctor_relations)
        
        # print("✅ تم إنشاء جميع البيانات التجريبية بنجاح!")
        print(f"📊 created success")
        # print(f"   - {len(users)} مستخدم")
        print(f"   - {len(doctors)} doctor")
        # print(f"   - {len(medicines)} دواء")
        # print(f"   - {len(medical_records)} سجل طبي")
        # print(f"   - {len(image_analyses)} تحليل صورة")
        # print(f"   - {len(audio_transcriptions)} تسجيل صوتي")
        # print(f"   - {len(user_doctor_relations)} علاقة مريض-طبيب")
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء البيانات: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀data creating start ...")
    create_sample_data()
    print("🎉data creating end ..")