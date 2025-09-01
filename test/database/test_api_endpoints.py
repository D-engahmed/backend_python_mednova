import requests
import json
from datetime import datetime

# تكوين API
BASE_URL = "http://localhost:8000"
API_VERSION = "/api/v1"
FULL_URL = BASE_URL + API_VERSION

def test_api_endpoints():
    """اختبار جميع API endpoints"""
    print("🚀 بدء اختبار API endpoints...")
    
    # متغيرات لحفظ tokens والبيانات
    access_token = None
    user_id = None
    
    try:
        # 1. اختبار تسجيل مستخدم جديد
        print("\n1️⃣ اختبار تسجيل مستخدم جديد...")
        register_data = {
            "username": "test_user",
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "مستخدم تجريبي",
            "phone": "01234567890"
        }
        
        response = requests.post(f"{FULL_URL}/users/register", json=register_data)
        if response.status_code == 201:
            print("✅ تسجيل المستخدم نجح")
            user_data = response.json()
            user_id = user_data.get("id")
        else:
            print(f"❌ فشل تسجيل المستخدم: {response.status_code}")
            print(response.text)
        
        # 2. اختبار تسجيل الدخول
        print("\n2️⃣ اختبار تسجيل الدخول...")
        login_data = {
            "username": "ahmed_ali",  # مستخدم من البيانات التجريبية
            "password": "password123"
        }
        
        response = requests.post(f"{FULL_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            print("✅ تسجيل الدخول نجح")
            token_data = response.json()
            access_token = token_data.get("access_token")
            print(f"Token: {access_token[:50]}...")
        else:
            print(f"❌ فشل تسجيل الدخول: {response.status_code}")
            print(response.text)
        
        # إعداد headers للطلبات المحمية
        headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}
        
        # 3. اختبار الحصول على بيانات المستخدم الحالي
        print("\n3️⃣ اختبار الحصول على بيانات المستخدم...")
        response = requests.get(f"{FULL_URL}/users/me", headers=headers)
        if response.status_code == 200:
            print("✅ الحصول على بيانات المستخدم نجح")
            user_data = response.json()
            print(f"مرحباً {user_data.get('full_name')}")
        else:
            print(f"❌ فشل الحصول على بيانات المستخدم: {response.status_code}")
        
        # 4. اختبار الحصول على قائمة الأطباء
        print("\n4️⃣ اختبار الحصول على قائمة الأطباء...")
        response = requests.get(f"{FULL_URL}/doctors", headers=headers)
        if response.status_code == 200:
            print("✅ الحصول على قائمة الأطباء نجح")
            doctors = response.json()
            print(f"عدد الأطباء: {len(doctors)}")
            for doctor in doctors[:3]:
                print(f"   - {doctor.get('name')} - {doctor.get('specialty')}")
        else:
            print(f"❌ فشل الحصول على قائمة الأطباء: {response.status_code}")
        
        # 5. اختبار الحصول على قائمة الأدوية
        print("\n5️⃣ اختبار الحصول على قائمة الأدوية...")
        response = requests.get(f"{FULL_URL}/medicines", headers=headers)
        if response.status_code == 200:
            print("✅ الحصول على قائمة الأدوية نجح")
            medicines = response.json()
            print(f"عدد الأدوية: {len(medicines)}")
            for medicine in medicines[:3]:
                print(f"   - {medicine.get('name')} - {medicine.get('price')} جنيه")
        else:
            print(f"❌ فشل الحصول على قائمة الأدوية: {response.status_code}")
        
        # 6. اختبار البحث في الأدوية
        print("\n6️⃣ اختبار البحث في الأدوية...")
        search_params = {"q": "باراسيتامول"}
        response = requests.get(f"{FULL_URL}/medicines/search", params=search_params, headers=headers)
        if response.status_code == 200:
            print("✅ البحث في الأدوية نجح")
            results = response.json()
            print(f"نتائج البحث: {len(results)}")
            for result in results:
                print(f"   - {result.get('name')} - {result.get('description')}")
        else:
            print(f"❌ فشل البحث في الأدوية: {response.status_code}")
        
        # 7. اختبار الحصول على السجلات الطبية
        print("\n7️⃣ اختبار الحصول على السجلات الطبية...")
        response = requests.get(f"{FULL_URL}/medical-records", headers=headers)
        if response.status_code == 200:
            print("✅ الحصول على السجلات الطبية نجح")
            records = response.json()
            print(f"عدد السجلات: {len(records)}")
            for record in records:
                print(f"   - {record.get('diagnosis')} - {record.get('created_at')}")
        else:
            print(f"❌ فشل الحصول على السجلات الطبية: {response.status_code}")
        
        # 8. اختبار إنشاء سجل طبي جديد
        print("\n8️⃣ اختبار إنشاء سجل طبي جديد...")
        medical_record_data = {
            "doctor_id": 1,
            "diagnosis": "فحص دوري",
            "symptoms": "لا توجد أعراض",
            "treatment": "فحص وقائي",
            "prescription": "فيتامينات",
            "notes": "فحص دوري شامل"
        }
        
        response = requests.post(f"{FULL_URL}/medical-records", json=medical_record_data, headers=headers)
        if response.status_code == 201:
            print("✅ إنشاء السجل الطبي نجح")
            record_data = response.json()
            print(f"السجل الجديد: {record_data.get('diagnosis')}")
        else:
            print(f"❌ فشل إنشاء السجل الطبي: {response.status_code}")
            print(response.text)
        
        # 9. اختبار الحصول على الأدوية المُرعاة
        print("\n9️⃣ اختبار الحصول على الأدوية المُرعاة...")
        response = requests.get(f"{FULL_URL}/medicines/sponsored", headers=headers)
        if response.status_code == 200:
            print("✅ الحصول على الأدوية المُرعاة نجح")
            sponsored = response.json()
            print(f"عدد الأدوية المُرعاة: {len(sponsored)}")
            for medicine in sponsored:
                print(f"   - {medicine.get('name')} - {medicine.get('manufacturer')}")
        else:
            print(f"❌ فشل الحصول على الأدوية المُرعاة: {response.status_code}")
        
        # 10. اختبار الحصول على تحليلات الصور
        print("\n🔟 اختبار الحصول على تحليلات الصور...")
        response = requests.get(f"{FULL_URL}/image-analyses", headers=headers)
        if response.status_code == 200:
            print("✅ الحصول على تحليلات الصور نجح")
            analyses = response.json()
            print(f"عدد التحليلات: {len(analyses)}")
            for analysis in analyses:
                print(f"   - {analysis.get('image_type')} - {analysis.get('body_part')}")
        else:
            print(f"❌ فشل الحصول على تحليلات الصور: {response.status_code}")
        
        print("\n✅ اختبار جميع API endpoints مكتمل!")
        
    except requests.exceptions.ConnectionError:
        print("❌ خطأ في الاتصال: تأكد من تشغيل الخادم على http://localhost:8000")
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")

def test_file_upload():
    """اختبار رفع الملفات"""
    print("\n📁 اختبار رفع الملفات...")
    
    # إنشاء ملف تجريبي
    test_file_content = b"This is a test file content"
    files = {"file": ("test.txt", test_file_content, "text/plain")}
    
    try:
        # أولاً نحتاج للحصول على token
        login_data = {
            "username": "ahmed_ali",
            "password": "password123"
        }
        
        response = requests.post(f"{FULL_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # اختبار رفع ملف صوتي
            print("🎤 اختبار رفع ملف صوتي...")
            audio_files = {"audio": ("test_audio.wav", test_file_content, "audio/wav")}
            response = requests.post(f"{FULL_URL}/audio/upload", files=audio_files, headers=headers)
            if response.status_code == 200:
                print("✅ رفع الملف الصوتي نجح")
            else:
                print(f"❌ فشل رفع الملف الصوتي: {response.status_code}")
            
            # اختبار رفع صورة
            print("🖼️ اختبار رفع صورة...")
            image_files = {"image": ("test_image.jpg", test_file_content, "image/jpeg")}
            response = requests.post(f"{FULL_URL}/images/upload", files=image_files, headers=headers)
            if response.status_code == 200:
                print("✅ رفع الصورة نجح")
            else:
                print(f"❌ فشل رفع الصورة: {response.status_code}")
                
        else:
            print("❌ فشل في الحصول على token للاختبار")
            
    except Exception as e:
        print(f"❌ خطأ في اختبار رفع الملفات: {e}")

def test_health_check():
    """اختبار فحص صحة الخادم"""
    print("\n🏥 اختبار فحص صحة الخادم...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ الخادم يعمل بشكل صحيح")
            health_data = response.json()
            print(f"الحالة: {health_data.get('status')}")
            print(f"الوقت: {health_data.get('timestamp')}")
        else:
            print(f"❌ مشكلة في الخادم: {response.status_code}")
            
    except Exception as e:
        print(f"❌ خطأ في فحص صحة الخادم: {e}")

if __name__ == "__main__":
    print("🚀 بدء اختبار النظام الكامل...")
    test_health_check()
    test_api_endpoints()
    test_file_upload()
    print("🎉 انتهى اختبار النظام الكامل!")