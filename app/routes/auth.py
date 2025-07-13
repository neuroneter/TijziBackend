from fastapi import APIRouter, HTTPException
from app.services.otp_service import OTPService

# Router para endpoints de autenticación
auth_router = APIRouter(prefix="/auth", tags=["authentication"])

# Instancia del servicio OTP
otp_service = OTPService()

@auth_router.post("/send-code")
def send_code(request: dict):
    """
    Endpoint que espera el frontend Kotlin
    Body: {"countryCode": "+57", "phoneNumber": "3004051582"}
    """
    try:
        country_code = request.get("countryCode")
        phone_number = request.get("phoneNumber")
        
        if not country_code or not phone_number:
            raise HTTPException(
                status_code=400, 
                detail="countryCode and phoneNumber are required"
            )
        
        # Combinar código de país + número
        full_phone_number = country_code + phone_number
        
        # Generar código OTP
        code = otp_service.generate_and_store_code(full_phone_number)
        
        # 🔥 LOGS PARA DEBUG (como en el backend original)
        print(f"🔥 [DEBUG] Country Code: {country_code}")
        print(f"🔥 [DEBUG] Phone Number: {phone_number}")
        print(f"🔥 [DEBUG] Full Number: {full_phone_number}")
        print(f"🔥 [DEBUG] Generated OTP: {code}")
        
        # TODO: Aquí iría el envío real a WhatsApp
        # success = send_whatsapp_message(full_phone_number, code)
        
        # Por ahora simulamos éxito
        success = True
        
        if not success:
            print(f"🔥 [ERROR] Failed to send WhatsApp to {full_phone_number}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to send WhatsApp message."
            )
        
        print(f"🔥 [SUCCESS] OTP sent to {full_phone_number}")
        
        # Respuesta que espera el frontend
        return {"message": "Code sent successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"🔥 [ERROR] Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@auth_router.post("/verify-code")
def verify_code(request: dict):
    """
    Endpoint que espera el frontend Kotlin
    Body: {"countryCode": "+57", "phoneNumber": "3004051582", "otp": "547344"}
    """
    try:
        country_code = request.get("countryCode")
        phone_number = request.get("phoneNumber")
        otp = request.get("otp")
        
        if not country_code or not phone_number or not otp:
            raise HTTPException(
                status_code=400,
                detail="countryCode, phoneNumber and otp are required"
            )
        
        # Combinar código de país + número
        full_phone_number = country_code + phone_number
        
        print(f"🔥 [DEBUG] Verifying {otp} for {full_phone_number}")
        
        # Verificar código
        if otp_service.verify_code(full_phone_number, otp):
            token = otp_service.generate_token(full_phone_number)
            print(f"🔥 [SUCCESS] Token generated for {full_phone_number}")
            
            # Respuesta en el formato que espera el frontend
            return {
                "session_token": token,
                "user_id": full_phone_number
            }
        else:
            print(f"🔥 [ERROR] Invalid OTP for {full_phone_number}")
            raise HTTPException(status_code=401, detail="Invalid or expired code")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"🔥 [ERROR] Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")