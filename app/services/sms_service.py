import os
import httpx
import base64

class SMSService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN") 
        self.verify_service_sid = os.getenv("TWILIO_VERIFY_SERVICE_SID")
        self.base_url = f"https://verify.twilio.com/v2/Services/{self.verify_service_sid}"
        
    async def send_verification_code(self, phone_number: str) -> dict:
        """
        Envía código de verificación usando Twilio Verify
        Twilio genera el código automáticamente
        """
        try:
            print(f"🔥 [SMS Verify] Checking credentials...")
            
            if not self.account_sid or not self.auth_token or not self.verify_service_sid:
                print("🔥 [SMS ERROR] Missing Twilio Verify credentials")
                return {"success": False, "error": "Missing credentials"}
            
            print(f"🔥 [SMS] Service SID: {self.verify_service_sid}")
            print(f"🔥 [SMS] To: {phone_number}")
            
            # URL para enviar verificación
            url = f"{self.base_url}/Verifications"
            
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
    
    async def verify_code(self, phone_number: str, code: str) -> dict:
        """
        Verifica el código usando Twilio Verify
        """
        try:
            if not self.verify_service_sid:
                return {"success": False, "error": "Service SID not configured"}
            
            print(f"🔥 [SMS Verify] Checking code {code} for {phone_number}")
            
            # URL para verificar código
            url = f"{self.base_url}/VerificationCheck"
            
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
        """Verifica si SMS Verify está configurado"""
        return bool(self.account_sid and self.auth_token and self.verify_service_sid)
    
    def get_debug_info(self) -> dict:
        """Info de debug para verificar configuración"""
        return {
            "account_sid": self.account_sid,
            "auth_token_configured": bool(self.auth_token),
            "auth_token_length": len(self.auth_token) if self.auth_token else 0,
            "verify_service_sid": self.verify_service_sid,
            "verify_service_configured": bool(self.verify_service_sid),
            "configured": self.is_configured(),
            "service_type": "Twilio Verify API"
        }