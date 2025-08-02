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

# Añadir este endpoint al archivo app/main.py

@app.post("/test-whatsapp")
async def test_whatsapp_connection(request: dict = None):
    """
    Endpoint para probar la conexión con WhatsApp Business API
    Body: {"phoneNumber": "+573001234567"} (opcional)
    """
    from app.services.whatsapp_service import whatsapp_service
    
    try:
        # 🔥 PASO 1: Verificar credenciales
        if not whatsapp_service.validate_credentials():
            return {
                "status": "error",
                "message": "WhatsApp credentials not properly configured",
                "details": {
                    "access_token": "Missing or invalid" if not whatsapp_service.access_token else "✅ Present",
                    "phone_number_id": "Missing or invalid" if not whatsapp_service.phone_number_id else "✅ Present",
                    "template_name": whatsapp_service.template_name
                }
            }
        
        # 🔥 PASO 2: Test de conectividad
        connection_test = await whatsapp_service.test_connection()
        
        if connection_test["status"] != "success":
            return {
                "status": "error",
                "message": "WhatsApp API connection failed",
                "connection_test": connection_test
            }
        
        # 🔥 PASO 3: Test de envío real (opcional)
        phone_number = None
        send_test_result = None
        
        if request and request.get("phoneNumber"):
            phone_number = request["phoneNumber"]
            test_code = "123456"  # Código de prueba
            
            print(f"🔥 [TEST] Sending test OTP to {phone_number}")
            send_success = await whatsapp_service.send_otp_message(phone_number, test_code)
            
            send_test_result = {
                "attempted": True,
                "phone_number": phone_number,
                "test_code": test_code,
                "success": send_success
            }
        
        return {
            "status": "success",
            "message": "WhatsApp service is working correctly",
            "connection_test": connection_test,
            "credentials": {
                "template_name": whatsapp_service.template_name,
                "phone_number_id": whatsapp_service.phone_number_id,
                "access_token_length": len(whatsapp_service.access_token)
            },
            "send_test": send_test_result,
            "instructions": {
                "message": "To test message sending, include 'phoneNumber' in request body",
                "example": {"phoneNumber": "+573001234567"}
            }
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "message": f"WhatsApp test failed: {str(e)}",
            "type": "exception"
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