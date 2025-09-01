from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import psutil
import torch
import time
import asyncio
import httpx
from typing import Dict, Any, List
from core.logging import logger
from core.config import settings
import socket
import os
from fastapi import Request

router = APIRouter()

# نقاط النهاية التي سيتم فحصها
API_ENDPOINTS = [
    {"path": "/health", "method": "GET"},
    {"path": "/search/doctor", "method": "GET"},
    {"path": "/search/medicine", "method": "GET"},
    {"path": "/ai/text", "method": "POST", "payload": {"text": "Test health check", "task": "analysis"}},
    {"path": "/ai/recommend", "method": "POST", "payload": {"user_id": 1}},
    {"path": "/auth/login", "method": "POST", "payload": {"username": "healthcheck", "password": "healthcheck"}},
    {"path": "/dashboard/user", "method": "GET"},
]

async def check_endpoint_speed(client: httpx.AsyncClient, base_url: str, endpoint: Dict) -> Dict[str, Any]:
    """قياس سرعة استجابة نقطة النهاية"""
    path = endpoint["path"]
    method = endpoint["method"]
    payload = endpoint.get("payload", {})
    url = f"{base_url}{path}"
    
    try:
        start_time = time.time()
        if method == "GET":
            response = await client.get(url, timeout=0.01)
        else:  # POST
            response = await client.post(url, json=payload, timeout=0.01)
        
        elapsed_time = time.time() - start_time
        status_code = response.status_code
        
        return {
            "endpoint": path,
            "method": method,
            "status": "ok" if status_code < 400 else "error",
            "status_code": status_code,
            "response_time": round(elapsed_time * 1000, 2),  # بالملي ثانية
            "user_experience": get_user_experience_rating(elapsed_time)
        }
    except Exception as e:
        return {
            "endpoint": path,
            "method": method,
            "status": "error",
            "error": str(e),
            "user_experience": "poor"
        }

def get_user_experience_rating(response_time: float) -> str:
    """تقييم تجربة المستخدم بناءً على وقت الاستجابة"""
    if response_time < 0.1:
        return "excellent"  # ممتاز - أقل من 100 ملي ثانية
    elif response_time < 0.3:
        return "very good"  # جيد جداً - أقل من 300 ملي ثانية
    elif response_time < 0.5:
        return "good"       # جيد - أقل من 500 ملي ثانية
    elif response_time < 1.0:
        return "fair"       # مقبول - أقل من ثانية واحدة
    elif response_time < 2.0:
        return "poor"       # ضعيف - أقل من ثانيتين
    else:
        return "very poor"  # ضعيف جداً - أكثر من ثانيتين

def get_system_disk_usage():
    """الحصول على استخدام القرص بطريقة متوافقة مع نظام التشغيل"""
    try:
        if os.name == 'nt':  # نظام ويندوز
            return psutil.disk_usage('C:\\').percent
        else:  # لينكس/ماك
            return psutil.disk_usage('/').percent
    except Exception as e:
        logger.error(f"فشل الحصول على استخدام القرص: {str(e)}")
        return -1

@router.get("/health")
async def health_check():
    """فحص صحة النظام الأساسي وقياس أداء API"""
    try:
        # معلومات النظام الأساسية
        health_data = {
            "status": "ok",
            "timestamp": time.time(),
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": get_system_disk_usage(),
            "gpu_available": torch.cuda.is_available(),
        }
        
        # معلومات GPU إذا كانت متوفرة
        if torch.cuda.is_available():
            health_data["gpu_count"] = torch.cuda.device_count()
            health_data["gpu_name"] = torch.cuda.get_device_name(0)
            health_data["gpu_memory"] = {
                "allocated": round(torch.cuda.memory_allocated(0) / (1024 ** 3), 2),  # بالجيجابايت
                "reserved": round(torch.cuda.memory_reserved(0) / (1024 ** 3), 2)     # بالجيجابايت
            }
        
        return health_data
    except Exception as e:
        logger.error(f"فشل فحص الصحة الأساسي: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@router.get("/health/detailed")
async def detailed_health_check(request: Request):
    """فحص صحة مفصل يتضمن سرعة نقاط النهاية وتقييم تجربة المستخدم"""
    try:
        # فحص الصحة الأساسي
        basic_health = await health_check()
        
        # الحصول على عنوان الخادم الأساسي
        host = request.headers.get("host", "localhost:8000")
        base_url = f"http://{host}"
        
        # فحص جميع نقاط النهاية
        endpoint_results = []
        async with httpx.AsyncClient() as client:
            tasks = [check_endpoint_speed(client, base_url, endpoint) for endpoint in API_ENDPOINTS]
            endpoint_results = await asyncio.gather(*tasks)
        
        # حساب متوسط وقت الاستجابة
        valid_times = [result["response_time"] for result in endpoint_results if result["status"] == "ok" and "response_time" in result]
        avg_response_time = sum(valid_times) / len(valid_times) if valid_times else 0
        
        # ملخص النتائج
        result = {
            **basic_health,
            "endpoints": endpoint_results,
            "performance_summary": {
                "average_response_time": round(avg_response_time, 2),
                "overall_user_experience": get_user_experience_rating(avg_response_time / 1000),
                "endpoints_ok": sum(1 for result in endpoint_results if result["status"] == "ok"),
                "endpoints_error": sum(1 for result in endpoint_results if result["status"] == "error"),
                "fastest_endpoint": min(valid_times) if valid_times else None,
                "slowest_endpoint": max(valid_times) if valid_times else None
            },
            "network": {
                "hostname": socket.gethostname(),
                "ip": socket.gethostbyname(socket.gethostname())
            }
        }
        
        return result
    except Exception as e:
        logger.error(f"فشل فحص الصحة المفصل: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )