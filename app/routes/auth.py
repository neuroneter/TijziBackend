from fastapi import APIRouter, HTTPException
from app.services.otp_service import OTPService
import httpx
import os

# Router para endpoints de autenticación
auth_router = APIRouter(prefix="/auth", tags=["authentication"])

# Instancia del servicio OTP
otp_service = OTPService()
async def send_whatsapp_otp(phone_number: str, otp_code: str) -> bool:
    """
    Envía código OTP vía WhatsApp adaptando el payload según el template configurado
    """
    try:
        # Obtener credenciales de variables de entorno
        access_token = os.getenv("ACCESS_TOKEN")
        phone_number_id = os.getenv("PHONE_NUMBER_ID")
        template_name = os.getenv("TEMPLATE_NAME", "otp_tijzi")
        
        print(f"🔥 [WhatsApp] Template: {template_name}")
        print(f"🔥 [WhatsApp] Access Token Length: {len(access_token) if access_token else 0}")
        print(f"🔥 [WhatsApp] Phone Number ID: {phone_number_id}")
        
        if not access_token or not phone_number_id:
            print("🔥 [WhatsApp ERROR] Missing credentials")
            return False
        
        # URL base para WhatsApp API v22.0
        base_url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Limpiar número de teléfono (remover +)
        clean_phone = phone_number.replace("+", "")
        
        # Adaptar payload según template
        if template_name == "hello_world":
            # Template de prueba: Sin parámetros
            payload = {
                "messaging_product": "whatsapp",
                "to": clean_phone,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": "en_US"}
                }
            }
            print(f"🔥 [WhatsApp] Using hello_world template")
            
        elif template_name in ["otp_login", "otp_tijzi", "otp_login_whatsapp"]:
            # Templates OTP: Con body y button components
            language_code = "es_CO" if template_name == "otp_tijzi_login" else "es"
            payload = {
                "messaging_product": "whatsapp",
                "to": clean_phone,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": language_code},
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
                            "sub_type": "url",
                            "index": "0",
                            "parameters": [{
                                "type": "text",
                                "text": otp_code
                            }]
                        }
                    ]
                }
            }
            print(f"🔥 [WhatsApp] Using OTP template with components")
            
        else:
            # Template desconocido: estructura básica
            payload = {
                "messaging_product": "whatsapp",
                "to": clean_phone,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": "es"}
                }
            }
            print(f"🔥 [WhatsApp] Using basic template structure")

        print(f"🔥 [WhatsApp] Sending to: {clean_phone}")
        
        # Enviar mensaje vía WhatsApp API
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
    Envía código OTP vía WhatsApp
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
        
        print(f"🔥 [DEBUG] Generated OTP: {code} for {full_phone_number}")
        
        # Enviar vía WhatsApp
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
    Verifica código OTP
    Body: {"countryCode": "+57", "phoneNumber": "3004051582", "otp": "123456"}
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

@auth_router.get("/debug-config")
def debug_config():
    """
    Endpoint útil para verificar configuración de variables de entorno
    """
    access_token = os.getenv("ACCESS_TOKEN")
    phone_number_id = os.getenv("PHONE_NUMBER_ID")
    template_name = os.getenv("TEMPLATE_NAME", "otp_tijzi")
    
    return {
        "access_token_configured": bool(access_token),
        "access_token_length": len(access_token) if access_token else 0,
        "phone_number_id_configured": bool(phone_number_id),
        "phone_number_id": phone_number_id,
        "template_name": template_name,
        "backend_status": "✅ Functional"
    }