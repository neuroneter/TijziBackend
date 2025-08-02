from fastapi import FastAPI, HTTPException
import httpx
from app.services.otp_service import OTPService
from app.routes.auth import auth_router

app = FastAPI(title="Tijzi Backend", version="1.0.0")

# Incluir router de autenticación
app.include_router(auth_router)

# Instancia global del servicio OTP
otp_service = OTPService()

@app.get("/")
def read_root():
    return {
        "message": "Tijzi Backend is working!", 
        "status": "OK",
        "version": "1.0.0",
        "endpoints": [
            "/", 
            "/health", 
            "/auth/send-code", 
            "/auth/verify-code"
        ]
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "service": "tijzi-backend",
        "version": "1.0.0"
    }

@app.post("/test-otp")
def test_otp_service(request: dict):
    """
    Test del servicio OTP (útil para desarrollo)
    Body: {"phoneNumber": "+573001234567", "action": "generate|verify|status"}
    """
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