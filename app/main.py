from fastapi import FastAPI, HTTPException
import httpx
from app.services.otp_service import OTPService
from app.routes.auth import auth_router  # 🔥 NUEVO IMPORT

app = FastAPI(title="Tijzi Backend Basic", version="1.0.0")

# 🔥 INCLUIR ROUTER DE AUTH
app.include_router(auth_router)

# Instancia global del servicio OTP
otp_service = OTPService()

@app.get("/")
def read_root():
    return {
        "message": "Tijzi Backend is working!", 
        "status": "OK",
        "version": "1.0.0",
        "endpoints": ["/", "/health", "/test", "/test-http", "/test-otp", "/auth/send-code", "/auth/verify-code"]
    }

# ... resto de endpoints sin cambios ...
@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "service": "tijzi-backend",
        "version": "1.0.0"
    }

@app.get("/test")
def test_endpoint():
    return {
        "test": "success", 
        "backend": "running",
        "message": "All systems operational"
    }

@app.post("/ping")
def ping_post(data: dict = None):
    return {
        "message": "POST endpoint working",
        "received_data": data,
        "status": "ok"
    }

@app.get("/test-http")
async def test_http():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://httpbin.org/json")
            return {
                "status": "HTTP client working",
                "test_response": response.json(),
                "httpx_version": httpx.__version__
            }
    except Exception as e:
        return {
            "status": "HTTP client error",
            "error": str(e)
        }

@app.post("/test-otp")
def test_otp_service(request: dict):
    """Test del servicio OTP sin WhatsApp"""
    phone_number = request.get("phoneNumber", "+573001234567")
    action = request.get("action", "generate")
    
    if action == "generate":
        code = otp_service.generate_and_store_code(phone_number)
        return {
            "status": "OTP generated",
            "phone_number": phone_number,
            "code": code,
            "message": "Code generated successfully"
        }
    
    elif action == "verify":
        code = request.get("code")
        if not code:
            raise HTTPException(status_code=400, detail="Code is required for verification")
        
        is_valid = otp_service.verify_code(phone_number, code)
        if is_valid:
            token = otp_service.generate_token(phone_number)
            return {
                "status": "verified",
                "valid": True,
                "token": token,
                "phone_number": phone_number
            }
        else:
            return {
                "status": "invalid",
                "valid": False,
                "message": "Invalid or expired code"
            }
    
    elif action == "status":
        stored_codes = otp_service.get_stored_codes()
        return {
            "status": "debug_info",
            "stored_codes": stored_codes,
            "total_codes": len(stored_codes)
        }
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use: generate, verify, or status")