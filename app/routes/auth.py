from fastapi import APIRouter, HTTPException
from app.services.otp_service import OTPService
import httpx
import os

# Router para endpoints de autenticación
auth_router = APIRouter(prefix="/auth", tags=["authentication"])

# Instancia del servicio OTP
otp_service = OTPService()

# REEMPLAZA la función send_whatsapp_otp en app/routes/auth.py
async def send_whatsapp_otp(phone_number: str, otp_code: str) -> bool:
    """
    Función standalone para enviar OTP vía WhatsApp
    VERSIÓN SIMPLIFICADA - Sin Copy Code Button
    """
    try:
        # Obtener credenciales de variables de entorno
        access_token = os.getenv("ACCESS_TOKEN")
        phone_number_id = os.getenv("PHONE_NUMBER_ID")
        template_name = os.getenv("TEMPLATE_NAME", "otp_login_whatsapp")
        
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
        
        # 🔥 PAYLOAD SIMPLIFICADO - SOLO BODY, SIN BOTÓN
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
                    }
                    # 🔥 SIN COPY CODE BUTTON POR AHORA
                ]
            }
        }

        print(f"🔥 [WhatsApp] Sending to: {clean_phone}")
        print(f"🔥 [WhatsApp] Code: {otp_code}")
        print(f"🔥 [WhatsApp] URL: {base_url}")
        print(f"🔥 [WhatsApp] Simplified Payload: {payload}")
        
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

# AÑADIR ESTE ENDPOINT TEMPORAL a app/routes/auth.py

@auth_router.post("/debug-whatsapp-call")
async def debug_whatsapp_call(request: dict):
    """
    Endpoint de debug para ver exactamente qué responde Facebook/WhatsApp
    """
    try:
        country_code = request.get("countryCode", "+57")
        phone_number = request.get("phoneNumber", "3054401383")
        
        # Obtener credenciales
        access_token = os.getenv("ACCESS_TOKEN")
        phone_number_id = os.getenv("PHONE_NUMBER_ID")
        template_name = os.getenv("TEMPLATE_NAME", "otp_login_whatsapp")
        
        print(f"🔥 [DEBUG] Using ACCESS_TOKEN length: {len(access_token) if access_token else 0}")
        print(f"🔥 [DEBUG] Using PHONE_NUMBER_ID: {phone_number_id}")
        print(f"🔥 [DEBUG] Using TEMPLATE_NAME: {template_name}")
        
        if not access_token or not phone_number_id:
            return {
                "error": "Missing credentials",
                "access_token_present": bool(access_token),
                "phone_number_id_present": bool(phone_number_id)
            }
        
        # URL y headers
        base_url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Payload
        clean_phone = (country_code + phone_number).replace("+", "")
        test_code = "123456"  # Código de prueba
        
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
                            "text": test_code
                        }]
                    },
                    {
                        "type": "button",
                        "sub_type": "copy_code",
                        "index": "0",
                        "parameters": [{
                            "type": "copy_code",
                            "copy_code": test_code
                        }]
                    }
                ]
            }
        }
        
        print(f"🔥 [DEBUG] Sending to: {clean_phone}")
        print(f"🔥 [DEBUG] URL: {base_url}")
        print(f"🔥 [DEBUG] Payload: {payload}")
        
        # Hacer la llamada real a Facebook
        async with httpx.AsyncClient() as client:
            response = await client.post(
                base_url,
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            print(f"🔥 [DEBUG] Facebook Status: {response.status_code}")
            print(f"🔥 [DEBUG] Facebook Response: {response.text}")
            
            # Parsear respuesta
            try:
                response_json = response.json()
            except:
                response_json = {"raw_text": response.text}
            
            return {
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "facebook_response": response_json,
                "request_details": {
                    "url": base_url,
                    "to_number": clean_phone,
                    "template": template_name,
                    "payload": payload
                },
                "headers_used": {
                    "authorization_length": len(headers["Authorization"]),
                    "content_type": headers["Content-Type"]
                }
            }
            
    except Exception as e:
        return {
            "error": "Exception occurred",
            "exception_message": str(e),
            "exception_type": type(e).__name__
        }
    
# AÑADIR ESTE ENDPOINT a app/routes/auth.py
@auth_router.post("/debug-real-function")
async def debug_real_function(request: dict):
    """
    Debug que usa la MISMA función send_whatsapp_otp que usa /auth/send-code
    """
    try:
        country_code = request.get("countryCode", "+57")
        phone_number = request.get("phoneNumber", "3054401383")
        
        # Combinar código de país + número
        full_phone_number = country_code + phone_number
        test_code = "999888"  # Código de prueba diferente
        
        print(f"🔥 [DEBUG REAL] Testing with: {full_phone_number}")
        print(f"🔥 [DEBUG REAL] Test code: {test_code}")
        
        # 🔥 USAR LA MISMA FUNCIÓN QUE USA /auth/send-code
        success = await send_whatsapp_otp(full_phone_number, test_code)
        
        return {
            "test_type": "Using REAL send_whatsapp_otp function",
            "full_phone_number": full_phone_number,
            "test_code": test_code,
            "function_returned": success,
            "message": "SUCCESS: Function returned True" if success else "FAILED: Function returned False"
        }
        
    except Exception as e:
        return {
            "error": "Exception in debug",
            "exception": str(e),
            "type": type(e).__name__
        }