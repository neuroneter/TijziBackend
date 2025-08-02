import httpx
import os

class WhatsAppService:
    def __init__(self):
        # 🔥 CREDENCIALES - Obtener de variables de entorno de RENDER
        self.access_token = os.getenv("ACCESS_TOKEN")
        self.phone_number_id = os.getenv("PHONE_NUMBER_ID") 
        self.template_name = os.getenv("TEMPLATE_NAME", "otp_login")
        
        # 🔥 VALIDACIÓN CRÍTICA para RENDER
        if not self.access_token:
            print("🚨 [RENDER ERROR] ACCESS_TOKEN not found in environment variables")
        if not self.phone_number_id:
            print("🚨 [RENDER ERROR] PHONE_NUMBER_ID not found in environment variables")
        
        # 🔥 BASE URL para WhatsApp Cloud API
        if self.phone_number_id:
            self.base_url = f"https://graph.facebook.com/v19.0/{self.phone_number_id}/messages"
        else:
            self.base_url = None
        
        print(f"🔥 [WhatsApp] Initialized with template: {self.template_name}")
        print(f"🔥 [WhatsApp] Phone Number ID: {self.phone_number_id}")
        print(f"🔥 [WhatsApp] Access Token Length: {len(self.access_token) if self.access_token else 0}")

    async def send_otp_message(self, phone_number: str, otp_code: str) -> bool:
        try:
            if not self.access_token or not self.phone_number_id:
                print("🔥 [WhatsApp ERROR] Missing credentials")
                return False
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # 🔥 PAYLOAD ACTUALIZADO PARA ESPAÑOL
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number.replace("+", ""),
                "type": "template",
                "template": {
                    "name": self.template_name,
                    "language": {"code": "es"}, 
                    "components": [
                        {
                            "type": "body",
                            "parameters": [{
                                "type": "text", 
                                "text": otp_code
                            }]
                        },
                        # 🔥 COPY CODE BUTTON COMPONENT
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

            print(f"🔥 [WhatsApp] Sending to: {phone_number.replace('+', '')}")
            print(f"🔥 [WhatsApp] Template: {self.template_name}")
            print(f"🔥 [WhatsApp] Language: es")
            print(f"🔥 [WhatsApp] Code: {otp_code}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                print(f"🔥 [WhatsApp] Status: {response.status_code}")
                print(f"🔥 [WhatsApp] Response: {response.text}")
                
                return response.status_code == 200
                
        except Exception as e:
            print(f"🔥 [WhatsApp] EXCEPTION: {str(e)}")
            return False

# 🔥 INSTANCIA GLOBAL - ESTA LÍNEA ES CRÍTICA
whatsapp_service = WhatsAppService()