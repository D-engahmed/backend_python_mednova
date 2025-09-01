from sqlalchemy.orm import Session
from db.database import SessionLocal
from models import User, Doctor, Medicine, MedicalRecord, AudioTranscription, ImageAnalysis
from datetime import datetime

def test_database():
    db = SessionLocal()
    
    try:
        print("🔍 اختبار قاعدة البيانات...")
        
        # اختبار المستخدمين
        users = db.query(User).all()
        print(f"📋 عدد المستخدمين: {len(users)}")
        for user in users[:3]:  # عرض أول 3 مستخدمين
            print(f"   - {user.full_name} ({user.username}) - {user.email}")
        
        # اختبار الأطباء
        doctors = db.query(Doctor).all()
        print(f"\n👨‍⚕️ عدد الأطباء: {len(doctors)}")
        for doctor in doctors[:3]:  # عرض أول 3 أطباء
            print(f"   - {doctor.name} - {doctor.specialty}")
        
        # اختبار الأدوية
        medicines = db.query(Medicine).all()
        print(f"\n💊 عدد الأدوية: {len(medicines)}")
        for medicine in medicines[:3]:  # عرض أول 3 أدوية
            print(f"   - {medicine.name} - {medicine.category} - {medicine.price} جنيه")
        
        # اختبار السجلات الطبية
        medical_records = db.query(MedicalRecord).all()
        print(f"\n📝 عدد السجلات الطبية: {len(medical_records)}")
        for record in medical_records[:3]:  # عرض أول 3 سجلات
            user = db.query(User).filter(User.id == record.user_id).first()
            doctor = db.query(Doctor).filter(Doctor.id == record.doctor_id).first()
            print(f"   - {user.full_name} → {doctor.name}: {record.diagnosis}")
        
        # اختبار تحليلات الصور
        image_analyses = db.query(ImageAnalysis).all()
        print(f"\n🖼️ عدد تحليلات الصور: {len(image_analyses)}")
        for analysis in image_analyses:
            user = db.query(User).filter(User.id == analysis.user_id).first()
            print(f"   - {user.full_name}: {analysis.image_type} - {analysis.body_part}")
        
        # اختبار التسجيلات الصوتية
        audio_transcriptions = db.query(AudioTranscription).all()
        print(f"\n🎤 عدد التسجيلات الصوتية: {len(audio_transcriptions)}")
        for transcription in audio_transcriptions:
            user = db.query(User).filter(User.id == transcription.user_id).first()
            preview = transcription.transcription[:50] + "..." if len(transcription.transcription) > 50 else transcription.transcription
            print(f"   - {user.full_name}: {preview}")
        
        # اختبار الأدوية المُرعاة
        sponsored_medicines = db.query(Medicine).filter(Medicine.is_sponsored == True).all()
        print(f"\n⭐ عدد الأدوية المُرعاة: {len(sponsored_medicines)}")
        for medicine in sponsored_medicines:
            print(f"   - {medicine.name} - {medicine.manufacturer}")
        
        # اختبار المستخدمين النشطين
        active_users = db.query(User).filter(User.is_active == True).all()
        print(f"\n✅ عدد المستخدمين النشطين: {len(active_users)}")
        
        # اختبار الأطباء النشطين
        active_doctors = db.query(Doctor).filter(Doctor.is_active == True).all()
        print(f"\n✅ عدد الأطباء النشطين: {len(active_doctors)}")
        
        # اختبار الأدوية المتاحة
        available_medicines = db.query(Medicine).filter(Medicine.is_available == True).all()
        print(f"\n✅ عدد الأدوية المتاحة: {len(available_medicines)}")
        
        # اختبار الأدوية التي تحتاج وصفة طبية
        prescription_medicines = db.query(Medicine).filter(Medicine.requires_prescription == True).all()
        print(f"\n📋 عدد الأدوية التي تحتاج وصفة طبية: {len(prescription_medicines)}")
        
        print("\n✅ اختبار قاعدة البيانات مكتمل بنجاح!")
        
    except Exception as e:
        print(f"❌ خطأ في اختبار قاعدة البيانات: {e}")
        raise
    finally:
        db.close()

def test_specific_queries():
    """اختبار استعلامات محددة"""
    db = SessionLocal()
    
    try:
        print("\n🔍 اختبار استعلامات محددة...")
        
        # البحث عن مستخدم بالاسم
        user = db.query(User).filter(User.username == "ahmed_ali").first()
        if user:
            print(f"🔍 البحث عن مستخدم: {user.full_name} - {user.email}")
        
        # البحث عن طبيب بالتخصص
        cardiologist = db.query(Doctor).filter(Doctor.specialty == "طب قلب").first()
        if cardiologist:
            print(f"🔍 طبيب القلب: {cardiologist.name} - خبرة {cardiologist.years_of_experience} سنة")
        
        # البحث عن دواء بالاسم
        medicine = db.query(Medicine).filter(Medicine.name == "باراسيتامول").first()
        if medicine:
            print(f"🔍 الدواء: {medicine.name} - {medicine.price} جنيه")
        
        # احصائيات متقدمة
        print("\n📊 احصائيات متقدمة:")
        
        # متوسط سعر الأدوية
        avg_price = db.query(Medicine).filter(Medicine.price > 0).all()
        if avg_price:
            total_price = sum(m.price for m in avg_price)
            avg = total_price / len(avg_price)
            print(f"   - متوسط سعر الأدوية: {avg:.2f} جنيه")
        
        # عدد المرضى لكل طبيب
        from sqlalchemy import func
        from db.models import UserDoctor
        
        doctor_patient_counts = db.query(
            Doctor.name,
            func.count(UserDoctor.user_id).label('patient_count')
        ).join(UserDoctor).group_by(Doctor.id, Doctor.name).all()
        
        print("   - عدد المرضى لكل طبيب:")
        for doctor_name, patient_count in doctor_patient_counts:
            print(f"     * {doctor_name}: {patient_count} مريض")
        
        # الأدوية الأكثر تكلفة
        expensive_medicines = db.query(Medicine).order_by(Medicine.price.desc()).limit(3).all()
        print("   - الأدوية الأكثر تكلفة:")
        for medicine in expensive_medicines:
            print(f"     * {medicine.name}: {medicine.price} جنيه")
        
        # السجلات الطبية الأحدث
        recent_records = db.query(MedicalRecord).order_by(MedicalRecord.created_at.desc()).limit(3).all()
        print("   - السجلات الطبية الأحدث:")
        for record in recent_records:
            user = db.query(User).filter(User.id == record.user_id).first()
            print(f"     * {user.full_name}: {record.diagnosis}")
        
        print("\n✅ اختبار الاستعلامات المحددة مكتمل!")
        
    except Exception as e:
        print(f"❌ خطأ في اختبار الاستعلامات: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 بدء اختبار قاعدة البيانات...")
    test_database()
    test_specific_queries()
    print("🎉 انتهى اختبار قاعدة البيانات!")