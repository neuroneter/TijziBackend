import os
import httpx
import base64

class SMSService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN") 
        self.verify_service_sid = os.getenv("TWILIO_VERIFY_SERVICE_SID")
        self.from_phone = os.getenv("TWILIO_PHONE_NUMBER")  # Nueva variable para SMS básico
        
        # URLs para ambos servicios
        self.verify_base_url = f"https://verify.twilio.com/v2/Services/{self.verify_service_sid}"
        self.sms_base_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
        
    async def send_verification_code(self, phone_number: str) -> dict:
        """
        Envía código usando Twilio Verify (método original - sin idioma)
        MANTIENE COMPATIBILIDAD CON CÓDIGO EXISTENTE
        """
        try:
            print(f"🔥 [SMS Verify] Checking credentials...")
            
            if not self.account_sid or not self.auth_token or not self.verify_service_sid:
                print("🔥 [SMS ERROR] Missing Twilio Verify credentials")
                return {"success": False, "error": "Missing credentials"}
            
            print(f"🔥 [SMS] Service SID: {self.verify_service_sid}")
            print(f"🔥 [SMS] To: {phone_number}")
            
            # URL para enviar verificación
            url = f"{self.verify_base_url}/Verifications"
            
            # Payload para Twilio Verify
            payload = {
                "To": phone_number,
                "Channel": "sms"
            }
            
            # Autenticación básica
            credentials = f"{self.account_sid}:{self.auth_token}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            print(f"🔥 [SMS] Sending verification request to Twilio...")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    data=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                print(f"🔥 [SMS] Status: {response.status_code}")
                print(f"🔥 [SMS] Response: {response.text}")
                
                if response.status_code == 201:
                    result = response.json()
                    print(f"🔥 [SMS SUCCESS] Verification sent to {phone_number}")
                    return {
                        "success": True,
                        "sid": result.get("sid"),
                        "status": result.get("status"),
                        "to": result.get("to")
                    }
                else:
                    error_detail = response.text
                    print(f"🔥 [SMS ERROR] Failed with status {response.status_code}: {error_detail}")
                    return {"success": False, "error": f"Twilio error: {error_detail}"}
                    
        except Exception as e:
            print(f"🔥 [SMS EXCEPTION] {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def send_sms_multilingual(self, phone_number: str, otp_code: str, language: str, supported_languages: dict) -> dict:
        """
        NUEVO: Envía SMS con mensaje personalizado según idioma usando Twilio SMS básico
        """
        try:
            print(f"🔥 [SMS Multi] Checking credentials...")
            
            if not self.account_sid or not self.auth_token or not self.from_phone:
                print("🔥 [SMS ERROR] Missing Twilio SMS credentials")
                return {"success": False, "error": "Missing SMS credentials (need TWILIO_PHONE_NUMBER)"}
            
            # Verificar idioma soportado
            if language not in supported_languages:
                print(f"🔥 [SMS ERROR] Unsupported language: {language}")
                return {"success": False, "error": f"Unsupported language: {language}"}
            
            lang_config = supported_languages[language]
            
            print(f"🔥 [SMS] Language: {language} ({lang_config['name']})")
            print(f"🔥 [SMS] From: {self.from_phone}")
            print(f"🔥 [SMS] To: {phone_number}")
            
            # Crear mensaje personalizado en el idioma correcto
            message_template = lang_config["sms_message"]
            personalized_message = message_template.replace("{code}", otp_code)
            
            print(f"🔥 [SMS] Message: {personalized_message}")
            
            # Payload para Twilio SMS básico
            payload = {
                "To": phone_number,
                "From": self.from_phone,
                "Body": personalized_message
            }
            
            # Autenticación básica
            credentials = f"{self.account_sid}:{self.auth_token}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            print(f"🔥 [SMS] Sending message...")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.sms_base_url,
                    data=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                print(f"🔥 [SMS] Status: {response.status_code}")
                print(f"🔥 [SMS] Response: {response.text}")
                
                if response.status_code == 201:  # Twilio SMS retorna 201
                    result = response.json()
                    print(f"🔥 [SMS SUCCESS] Message sent in {language} to {phone_number}")
                    return {
                        "success": True,
                        "sid": result.get("sid"),
                        "status": result.get("status"),
                        "to": result.get("to"),
                        "language": language,
                        "language_name": lang_config["name"],
                        "message": personalized_message
                    }
                else:
                    error_detail = response.text
                    print(f"🔥 [SMS ERROR] Failed with status {response.status_code}: {error_detail}")
                    return {"success": False, "error": f"Twilio error: {error_detail}"}
                    
        except Exception as e:
            print(f"🔥 [SMS EXCEPTION] {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def verify_code(self, phone_number: str, code: str) -> dict:
        """
        Verifica código usando Twilio Verify (método original)
        MANTIENE COMPATIBILIDAD CON CÓDIGO EXISTENTE
        """
        try:
            if not self.verify_service_sid:
                return {"success": False, "error": "Service SID not configured"}
            
            print(f"🔥 [SMS Verify] Checking code {code} for {phone_number}")
            
            # URL para verificar código
            url = f"{self.verify_base_url}/VerificationCheck"
            
            # Payload para verificación
            payload = {
                "To": phone_number,
                "Code": code
            }
            
            # Autenticación básica
            credentials = f"{self.account_sid}:{self.auth_token}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    data=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                print(f"🔥 [SMS Verify] Status: {response.status_code}")
                print(f"🔥 [SMS Verify] Response: {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    status = result.get("status")
                    
                    if status == "approved":
                        print(f"🔥 [SMS SUCCESS] Code verified for {phone_number}")
                        return {
                            "success": True,
                            "valid": True,
                            "status": status
                        }
                    else:
                        print(f"🔥 [SMS ERROR] Code verification failed: {status}")
                        return {
                            "success": True,
                            "valid": False,
                            "status": status,
                            "error": "Invalid or expired code"
                        }
                else:
                    error_detail = response.text
                    print(f"🔥 [SMS ERROR] Verification failed: {error_detail}")
                    return {"success": False, "error": f"Verification error: {error_detail}"}
                    
        except Exception as e:
            print(f"🔥 [SMS Verify EXCEPTION] {str(e)}")
            return {"success": False, "error": str(e)}
    
    def is_configured(self) -> bool:
        """Verifica si SMS está configurado (Verify o SMS básico)"""
        verify_configured = bool(self.account_sid and self.auth_token and self.verify_service_sid)
        sms_configured = bool(self.account_sid and self.auth_token and self.from_phone)
        return verify_configured or sms_configured
    
    def is_multilingual_configured(self) -> bool:
        """Verifica si SMS multi-idioma está configurado"""
        return bool(self.account_sid and self.auth_token and self.from_phone)
    
    def get_debug_info(self) -> dict:
        """Info de debug para verificar configuración"""
        return {
            "account_sid": self.account_sid,
            "auth_token_configured": bool(self.auth_token),
            "auth_token_length": len(self.auth_token) if self.auth_token else 0,
            "verify_service_sid": self.verify_service_sid,
            "verify_service_configured": bool(self.verify_service_sid),
            "from_phone": self.from_phone,
            "from_phone_configured": bool(self.from_phone),
            "twilio_verify_available": bool(self.account_sid and self.auth_token and self.verify_service_sid),
            "twilio_sms_multilingual_available": bool(self.account_sid and self.auth_token and self.from_phone),
            "configured": self.is_configured(),
            "service_type": "Twilio Verify + SMS Multi-language"
        }