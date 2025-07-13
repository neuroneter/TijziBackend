from fastapi import APIRouter, HTTPException
from app.services.otp import OTPService
from app.services.whatsapp import send_whatsapp_message
from app.config import settings

auth_router = APIRouter()
otp_service = OTPService()

@auth_router.post("/send-code")
def send_code(request: dict):  # 🔥 DICT en lugar de BaseModel
    country_code = request.get("countryCode")
    phone_number = request.get("phoneNumber")
    
    full_phone_number = country_code + phone_number
    
    print(f"🔥 [DEBUG] Full Number: {full_phone_number}")
    
    code = otp_service.generate_and_store_code(full_phone_number)
    print(f"🔥 [DEBUG] Generated OTP: {code}")
    
    success = send_whatsapp_message(full_phone_number, code)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send WhatsApp message.")
    
    return {"message": "Code sent successfully"}

@auth_router.post("/verify-code")
def verify_code(request: dict):  # 🔥 DICT en lugar de BaseModel
    country_code = request.get("countryCode")
    phone_number = request.get("phoneNumber") 
    otp = request.get("otp")
    
    full_phone_number = country_code + phone_number
    
    if otp_service.verify_code(full_phone_number, otp):
        token = otp_service.generate_token(full_phone_number)
        return {
            "session_token": token,
            "user_id": full_phone_number
        }
    
    raise HTTPException(status_code=401, detail="Invalid code")