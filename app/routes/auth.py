from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.otp import OTPService
from app.services.whatsapp import send_whatsapp_message
from app.config import settings

auth_router = APIRouter()
otp_service = OTPService()

# 🔥 ACTUALIZADO PARA FRONTEND KOTLIN
class SendCodeRequest(BaseModel):
    countryCode: str  # +57
    phoneNumber: str  # 3001234567

class VerifyCodeRequest(BaseModel):
    countryCode: str  # +57  
    phoneNumber: str  # 3001234567
    otp: str         # 123456

@auth_router.post("/send-code")
def send_code(request: SendCodeRequest):
    # 🔥 COMBINAR countryCode + phoneNumber
    full_phone_number = request.countryCode + request.phoneNumber
    
    # 🔥 LOGS PARA DEBUG
    print(f"🔥 [DEBUG] Country Code: {request.countryCode}")
    print(f"🔥 [DEBUG] Phone Number: {request.phoneNumber}")
    print(f"🔥 [DEBUG] Full Number: {full_phone_number}")
    
    code = otp_service.generate_and_store_code(full_phone_number)
    print(f"🔥 [DEBUG] Generated OTP: {code}")
    
    success = send_whatsapp_message(full_phone_number, code)
    
    if not success:
        print(f"🔥 [ERROR] Failed to send WhatsApp to {full_phone_number}")
        raise HTTPException(status_code=500, detail="Failed to send WhatsApp message.")
    
    print(f"🔥 [SUCCESS] OTP sent to {full_phone_number}")
    return {"message": "Code sent successfully"}

@auth_router.post("/verify-code")
def verify_code(request: VerifyCodeRequest):
    # 🔥 COMBINAR countryCode + phoneNumber
    full_phone_number = request.countryCode + request.phoneNumber
    
    print(f"🔥 [DEBUG] Verifying {request.otp} for {full_phone_number}")
    
    if otp_service.verify_code(full_phone_number, request.otp):
        token = otp_service.generate_token(full_phone_number)
        print(f"🔥 [SUCCESS] Token generated for {full_phone_number}")
        return {
            "session_token": token,  # 🔥 FORMATO QUE ESPERA EL FRONTEND
            "user_id": full_phone_number  # opcional
        }
    
    print(f"🔥 [ERROR] Invalid OTP for {full_phone_number}")
    raise HTTPException(status_code=401, detail="Invalid code")