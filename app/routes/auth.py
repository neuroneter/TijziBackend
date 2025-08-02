from fastapi import APIRouter, HTTPException
from app.services.otp_service import OTPService
from app.services.sms_service import SMSService
import httpx
import os

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

# ==========================================
# PASO 1: AÑADIR AL FINAL DE auth.py
# Configuración de idiomas soportados
# ==========================================
# ==========================================
# MENSAJES SMS OPTIMIZADOS PARA AUTO-DETECCIÓN
# Reemplazar en tu diccionario SUPPORTED_LANGUAGES
# ==========================================

SUPPORTED_LANGUAGES = {
    "es": {
        "name": "Español",
        "whatsapp_template": "otp_tijzi_es",
        "whatsapp_language_code": "es",
        # ✅ FORMATO OPTIMIZADO - código al inicio + palabra clave
        "sms_message": "{code} es tu código de verificación de Tijzi. Válido por 5 minutos."
    },
    "en": {
        "name": "English", 
        "whatsapp_template": "otp_tijzi_en",
        "whatsapp_language_code": "en",
        # ✅ FORMATO OPTIMIZADO - formato que iOS/Android reconocen
        "sms_message": "{code} is your Tijzi verification code. Valid for 5 minutes."
    },
    "pt": {
        "name": "Português",
        "whatsapp_template": "otp_tijzi_pt", 
        "whatsapp_language_code": "pt_BR",
        # ✅ FORMATO OPTIMIZADO
        "sms_message": "{code} é seu código de verificação Tijzi. Válido por 5 minutos."
    },
    "it": {
        "name": "Italiano",
        "whatsapp_template": "otp_tijzi_it",
        "whatsapp_language_code": "it",
        # ✅ FORMATO OPTIMIZADO
        "sms_message": "{code} è il tuo codice di verifica Tijzi. Valido per 5 minuti."
    },
    "fr": {
        "name": "Français",
        "whatsapp_template": "otp_tijzi_fr",
        "whatsapp_language_code": "fr",
        # ✅ FORMATO OPTIMIZADO
        "sms_message": "{code} est votre code de vérification Tijzi. Valide 5 minutes."
    }
}

# ==========================================
# PASO 2: AÑADIR DESPUÉS DEL PASO 1
# Función WhatsApp multi-idioma
# ==========================================

async def send_whatsapp_otp_multilingual(phone_number: str, otp_code: str, language: str) -> bool:
    """
    Envía código OTP vía WhatsApp con template según idioma
    """
    try:
        # Verificar idioma soportado
        if language not in SUPPORTED_LANGUAGES:
            print(f"🔥 [WhatsApp ERROR] Unsupported language: {language}")
            return False
        
        lang_config = SUPPORTED_LANGUAGES[language]
        
        # Obtener credenciales
        access_token = os.getenv("ACCESS_TOKEN")
        phone_number_id = os.getenv("PHONE_NUMBER_ID")
        template_name = lang_config["whatsapp_template"]
        language_code = lang_config["whatsapp_language_code"]
        
        print(f"🔥 [WhatsApp] Language: {language} ({lang_config['name']})")
        print(f"🔥 [WhatsApp] Template: {template_name}")
        print(f"🔥 [WhatsApp] Language Code: {language_code}")
        
        if not access_token or not phone_number_id:
            print("🔥 [WhatsApp ERROR] Missing credentials")
            return False
        
        # URL para WhatsApp API
        base_url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Limpiar número de teléfono
        clean_phone = phone_number.replace("+", "")
        
        # Payload con template específico del idioma
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
        
        print(f"🔥 [WhatsApp] Sending to: {clean_phone}")
        
        # Enviar mensaje
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
                print(f"🔥 [WhatsApp SUCCESS] Message sent in {language} to {phone_number}")
                return True
            else:
                print(f"🔥 [WhatsApp ERROR] Failed with status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"🔥 [WhatsApp EXCEPTION] {str(e)}")
        return False

# ==========================================
# PASO 3: AÑADIR DESPUÉS DEL PASO 2
# Endpoint multi-idioma
# ==========================================

@auth_router.post("/send-otp-multilingual")
async def send_otp_multilingual(request: dict):
    """
    Sistema OTP multi-idioma - WhatsApp + SMS
    
    Body: {
        "channel": "whatsapp|sms",
        "countryCode": "+57", 
        "phoneNumber": "3004051582",
        "language": "es|en|pt|it|fr"
    }
    """
    try:
        # Obtener parámetros
        channel = request.get("channel", "whatsapp").lower()
        country_code = request.get("countryCode")
        phone_number = request.get("phoneNumber")
        language = request.get("language", "es").lower()
        
        # Validaciones
        if not all([country_code, phone_number, language]):
            raise HTTPException(
                status_code=400,
                detail="countryCode, phoneNumber and language are required"
            )
        
        if channel not in ["whatsapp", "sms"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid channel. Options: whatsapp, sms"
            )
        
        if language not in SUPPORTED_LANGUAGES:
            supported = ", ".join(SUPPORTED_LANGUAGES.keys())
            raise HTTPException(
                status_code=400,
                detail=f"Invalid language. Supported: {supported}"
            )
        
        full_phone_number = country_code + phone_number
        lang_config = SUPPORTED_LANGUAGES[language]
        
        print(f"🔥 [OTP Multi] Channel: {channel}, Language: {language} ({lang_config['name']}), Phone: {full_phone_number}")
        
        # === WHATSAPP MULTI-IDIOMA ===
        if channel == "whatsapp":
            if not (os.getenv("ACCESS_TOKEN") and os.getenv("PHONE_NUMBER_ID")):
                raise HTTPException(status_code=503, detail="WhatsApp service not configured")
            
            # Generar código
            code = otp_service.generate_and_store_code(full_phone_number)
            
            # Enviar con template específico del idioma
            success = await send_whatsapp_otp_multilingual(full_phone_number, code, language)
            
            if not success:
                raise HTTPException(status_code=500, detail=f"Failed to send WhatsApp message in {language}")
            
            return {
                "success": True,
                "message": "OTP sent successfully",
                "channel": "whatsapp",
                "language": language,
                "language_name": lang_config["name"],
                "template": lang_config["whatsapp_template"],
                "recipient": full_phone_number,
                "expires_in": "5 minutes"
            }
        
        # === SMS MULTI-IDIOMA ===
        elif channel == "sms":
            # Verificar si SMS multi-idioma está configurado
            if not sms_service.is_multilingual_configured():
                raise HTTPException(
                    status_code=503, 
                    detail="SMS multilingual service not configured. Missing TWILIO_PHONE_NUMBER."
                )
            
            # Generar código OTP usando nuestro sistema
            code = otp_service.generate_and_store_code(full_phone_number)
            
            # Enviar SMS con mensaje personalizado según idioma
            result = await sms_service.send_sms_multilingual(full_phone_number, code, language, SUPPORTED_LANGUAGES)
            
            if not result["success"]:
                raise HTTPException(status_code=500, detail=f"Failed to send SMS: {result.get('error')}")
            
            return {
                "success": True,
                "message": "OTP sent successfully",
                "channel": "sms",
                "language": language,
                "language_name": lang_config["name"],
                "recipient": "***" + full_phone_number[-4:],
                "sms_sid": result.get("sid"),
                "expires_in": "5 minutes",
                "method": "Twilio SMS Multi-language"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"🔥 [OTP Multi ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@auth_router.get("/supported-languages")
def get_supported_languages():
    """
    Lista de idiomas soportados para OTP
    """
    languages = []
    
    for code, config in SUPPORTED_LANGUAGES.items():
        languages.append({
            "code": code,
            "name": config["name"],
            "whatsapp_template": config["whatsapp_template"],
            "whatsapp_language_code": config["whatsapp_language_code"],
            "sms_sample": config["sms_message"].replace("{code}", "123456")
        })
    
    return {
        "supported_languages": languages,
        "total_languages": len(languages),
        "default_language": "es",
        "channels": ["whatsapp", "sms"],
        "notes": [
            "WhatsApp requires specific templates for each language",
            "SMS messages use Twilio Verify standard format",
            "All languages support both WhatsApp and SMS channels"
        ]
    }