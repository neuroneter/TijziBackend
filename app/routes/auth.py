from fastapi import APIRouter, HTTPException
from app.services.otp_service import OTPService
import httpx
import os

# Router para endpoints de autenticación
auth_router = APIRouter(prefix="/auth", tags=["authentication"])

# Instancia del servicio OTP
otp_service = OTPService()

# 🔥 WHATSAPP SERVICE INLINE - Evitamos import problemático
async def send_whatsapp_otp(phone_number: str, otp_code: str) -> bool:
    """
    Función standalone para enviar OTP vía WhatsApp
    """
    try:
        # Obtener credenciales de variables de entorno
        access_token = os.getenv("ACCESS_TOKEN")
        phone_number_id = os.getenv("PHONE_NUMBER_ID")
        template_name = os.getenv("TEMPLATE_NAME", "otp_login")
        
        print(f"🔥 [WhatsApp] Access Token Length: {len(access_token) if access_token else 0}")
        print(f"🔥 [WhatsApp] Phone Number ID: {phone_number_id}")
        print(f"🔥 [WhatsApp] Template: {template_name}")
        
        if not access_token or not phone_number_id:
            print("🔥 [WhatsApp ERROR] Missing credentials")
            print(f"🔥 [DEBUG] ACCESS_TOKEN exists: {bool(access_token)}")
            print(f"🔥 [DEBUG] PHONE_NUMBER_ID exists: {bool(phone_number_id)}")
            return False
        
        # URL base para WhatsApp API
        base_url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Limpiar número de teléfono (remover +)
        clean_phone = phone_number.replace("+", "")
        
        # Payload para WhatsApp
        payload = {
            "messaging_product": "whatsapp",
            "to": clean_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "es"}, 
                "components": [
                    {
                        "type": "body",
                        "parameters": [{
                            "type": "text", 
                            "text": otp_code
                        }]
                    },
                    {
                        "type": "button",
                        "sub_type": "copy_code",
                        "index": "0",
                        "parameters": [{
                            "type": "copy_code",
                            "copy_code": otp_code
                        }]
                    }
                ]
            }
        }

        print(f"🔥 [WhatsApp] Sending to: {clean_phone}")
        print(f"🔥 [WhatsApp] Code: {otp_code}")
        print(f"🔥 [WhatsApp] URL: {base_url}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                base_url,
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            print(f"🔥 [WhatsApp] Status: {response.status_code}")
            print(f"🔥 [WhatsApp] Response: {response.text}")
            
            if response.status_code == 200:
                print(f"🔥 [WhatsApp SUCCESS] Message sent to {phone_number}")
                return True
            else:
                print(f"🔥 [WhatsApp ERROR] Failed with status {response.status_code}")
                return False
            
    except Exception as e:
        print(f"🔥 [WhatsApp EXCEPTION] {str(e)}")
        return False

@auth_router.post("/send-code")
async def send_code(request: dict):
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
        
        print(f"🔥 [DEBUG] Country Code: {country_code}")
        print(f"🔥 [DEBUG] Phone Number: {phone_number}")
        print(f"🔥 [DEBUG] Full Number: {full_phone_number}")
        print(f"🔥 [DEBUG] Generated OTP: {code}")
        
        # 🔥 USAR FUNCIÓN INLINE
        success = await send_whatsapp_otp(full_phone_number, code)
        
        if not success:
            print(f"🔥 [ERROR] Failed to send WhatsApp to {full_phone_number}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to send WhatsApp message. Check logs for details."
            )
        
        print(f"🔥 [SUCCESS] OTP sent to {full_phone_number}")
        
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

# 🔥 ENDPOINT DE DEBUG PARA VERIFICAR VARIABLES
@auth_router.get("/debug-config")
def debug_config():
    """
    Endpoint para verificar que las variables de entorno estén configuradas
    """
    access_token = os.getenv("ACCESS_TOKEN")
    phone_number_id = os.getenv("PHONE_NUMBER_ID")
    template_name = os.getenv("TEMPLATE_NAME", "otp_login")
    
    return {
        "access_token_configured": bool(access_token),
        "access_token_length": len(access_token) if access_token else 0,
        "phone_number_id_configured": bool(phone_number_id),
        "phone_number_id": phone_number_id,
        "template_name": template_name,
        "all_env_vars": {
            key: value for key, value in os.environ.items() 
            if key in ["ACCESS_TOKEN", "PHONE_NUMBER_ID", "TEMPLATE_NAME"]
        }
    }