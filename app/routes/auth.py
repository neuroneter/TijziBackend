from fastapi import APIRouter, HTTPException
from app.services.otp_service import OTPService
from app.services.sms_service import SMSService
from app.services.telegram_service import TelegramService
import httpx
import os


# Instancia del servicio Telegram
telegram_service = TelegramService()

# Router para endpoints de autenticación
auth_router = APIRouter(prefix="/auth", tags=["authentication"])

# Instancia del servicio SMS
sms_service = SMSService()

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

@auth_router.post("/send-sms")
async def send_sms_code(request: dict):
    """
    Envío SMS usando Twilio Verify (genera código automáticamente)
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
        
        print(f"🔥 [SMS TEST] Sending Twilio Verify to: {full_phone_number}")
        
        # Enviar usando Twilio Verify (ellos generan el código)
        result = await sms_service.send_verification_code(full_phone_number)
        
        if not result["success"]:
            print(f"🔥 [SMS ERROR] {result.get('error')}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to send SMS: {result.get('error')}"
            )
        
        print(f"🔥 [SMS SUCCESS] Verification sent to {full_phone_number}")
        
        return {
            "message": "SMS verification sent successfully",
            "phone_number": full_phone_number,
            "method": "Twilio Verify API",
            "status": result.get("status"),
            "sid": result.get("sid")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"🔥 [SMS ERROR] Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"SMS error: {str(e)}")

@auth_router.post("/verify-sms")
async def verify_sms_code(request: dict):
    """
    Verificación SMS usando Twilio Verify
    Body: {"countryCode": "+57", "phoneNumber": "3004051582", "code": "123456"}
    """
    try:
        country_code = request.get("countryCode")
        phone_number = request.get("phoneNumber")
        code = request.get("code")
        
        if not country_code or not phone_number or not code:
            raise HTTPException(
                status_code=400,
                detail="countryCode, phoneNumber and code are required"
            )
        
        # Combinar código de país + número
        full_phone_number = country_code + phone_number
        
        print(f"🔥 [SMS Verify] Checking {code} for {full_phone_number}")
        
        # Verificar usando Twilio Verify
        result = await sms_service.verify_code(full_phone_number, code)
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Verification error: {result.get('error')}"
            )
        
        if result["valid"]:
            # Generar token de sesión (usando nuestro sistema)
            token = otp_service.generate_token(full_phone_number)
            
            print(f"🔥 [SMS SUCCESS] Code verified for {full_phone_number}")
            
            return {
                "message": "Code verified successfully",
                "session_token": token,
                "user_id": full_phone_number,
                "method": "Twilio Verify",
                "status": result.get("status")
            }
        else:
            print(f"🔥 [SMS ERROR] Invalid code for {full_phone_number}")
            raise HTTPException(
                status_code=401, 
                detail=result.get("error", "Invalid or expired code")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"🔥 [SMS ERROR] Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"SMS verification error: {str(e)}")

@auth_router.get("/sms-debug")
def sms_debug():
    """
    Debug info para SMS/Twilio Verify
    """
    debug_info = sms_service.get_debug_info()
    
    return {
        "sms_service": "Twilio Verify API",
        "configuration": debug_info,
        "status": "✅ Ready" if debug_info["configured"] else "❌ Not configured",
        "endpoints": {
            "send": "/auth/send-sms",
            "verify": "/auth/verify-sms"
        }
    }

@auth_router.post("/send-telegram")
async def send_telegram_code(request: dict):
    """
    Envío OTP vía Telegram
    Body: {"telegramUser": "@usuario"} o {"telegramUser": "chat_id"}
    """
    try:
        telegram_user = request.get("telegramUser")
        
        if not telegram_user:
            raise HTTPException(
                status_code=400, 
                detail="telegramUser is required"
            )
        
        print(f"🔥 [Telegram TEST] Sending to: {telegram_user}")
        
        # Generar código OTP usando nuestro sistema
        code = otp_service.generate_and_store_code(telegram_user)
        
        print(f"🔥 [Telegram TEST] Generated OTP: {code}")
        
        # Enviar vía Telegram
        success = await telegram_service.send_otp_telegram(telegram_user, code)
        
        if not success:
            print(f"🔥 [Telegram ERROR] Failed to send message to {telegram_user}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to send Telegram message. Check bot configuration and user interaction."
            )
        
        print(f"🔥 [Telegram SUCCESS] Message sent to {telegram_user}")
        
        return {
            "message": "Telegram message sent successfully",
            "telegram_user": telegram_user,
            "method": "Telegram Bot API",
            "note": "User must have started chat with bot first"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"🔥 [Telegram ERROR] Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Telegram error: {str(e)}")

@auth_router.post("/verify-telegram")
async def verify_telegram_code(request: dict):
    """
    Verificación código Telegram
    Body: {"telegramUser": "@usuario", "otp": "123456"}
    """
    try:
        telegram_user = request.get("telegramUser")
        otp = request.get("otp")
        
        if not telegram_user or not otp:
            raise HTTPException(
                status_code=400,
                detail="telegramUser and otp are required"
            )
        
        print(f"🔥 [Telegram Verify] Checking {otp} for {telegram_user}")
        
        # Verificar código usando nuestro sistema OTP
        if otp_service.verify_code(telegram_user, otp):
            token = otp_service.generate_token(telegram_user)
            print(f"🔥 [Telegram SUCCESS] Code verified for {telegram_user}")
            
            return {
                "message": "Code verified successfully",
                "session_token": token,
                "user_id": telegram_user,
                "method": "Telegram Bot"
            }
        else:
            print(f"🔥 [Telegram ERROR] Invalid OTP for {telegram_user}")
            raise HTTPException(status_code=401, detail="Invalid or expired code")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"🔥 [Telegram ERROR] Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Telegram verification error: {str(e)}")

@auth_router.get("/telegram-debug")
async def telegram_debug():
    """
    Debug info para Telegram Bot
    """
    debug_info = telegram_service.get_debug_info()
    bot_info = await telegram_service.get_bot_info()
    
    return {
        "telegram_service": "Telegram Bot API",
        "configuration": debug_info,
        "bot_info": bot_info,
        "status": "✅ Ready" if debug_info["configured"] else "❌ Not configured",
        "endpoints": {
            "send": "/auth/send-telegram",
            "verify": "/auth/verify-telegram"
        },
        "requirements": [
            "User must send /start to bot first",
            "Bot must have TELEGRAM_BOT_TOKEN configured"
        ]
    }