import httpx
import os
from typing import Optional

class WhatsAppService:
    def __init__(self):
        self.access_token = os.getenv("ACCESS_TOKEN", "")
        self.phone_number_id = os.getenv("PHONE_NUMBER_ID", "")
        self.template_name = os.getenv("TEMPLATE_NAME", "")
        
        # 🔥 USAR v19.0 COMO EN EL CÓDIGO ORIGINAL
        self.base_url = f"https://graph.facebook.com/v19.0/{self.phone_number_id}/messages"
        
        print(f"🔥 [WhatsApp] Initialized with Phone ID: {self.phone_number_id[:10]}...")

    async def send_otp_message(self, phone_number: str, otp_code: str) -> bool:
        """
        Usar EXACTAMENTE la estructura del código original que funcionaba
        """
        try:
            if not self.access_token or not self.phone_number_id:
                print("🔥 [WhatsApp ERROR] Missing credentials")
                return False
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # 🔥 FORMATO EXACTO DEL CÓDIGO ORIGINAL
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number.replace("+", ""),  # 🔥 QUITAR EL + como en el ejemplo
                "type": "template",
                "template": {
                    "name": self.template_name,
                    "language": {"code": "es"},  # 🔥 ESPAÑOL como en el original
                    "components": [{
                        "type": "body",
                        "parameters": [{"type": "text", "text": otp_code}]
                    }]
                }
            }
            
            print(f"🔥 [WhatsApp] Sending to: {phone_number.replace('+', '')}")
            print(f"🔥 [WhatsApp] Template: {self.template_name}")
            print(f"🔥 [WhatsApp] Code: {otp_code}")
            print(f"🔥 [WhatsApp] URL: {self.base_url}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                print(f"🔥 [WhatsApp] Status: {response.status_code}")
                print(f"🔥 [WhatsApp] Response: {response.text}")
                
                if response.status_code == 200:
                    print(f"🔥 [WhatsApp] SUCCESS!")
                    return True
                else:
                    print(f"🔥 [WhatsApp] ERROR: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            print(f"🔥 [WhatsApp] EXCEPTION: {str(e)}")
            return False

    def send_otp_message_sync(self, phone_number: str, otp_code: str) -> bool:
        import asyncio
        try:
            return asyncio.run(self.send_otp_message(phone_number, otp_code))
        except Exception as e:
            print(f"🔥 [WhatsApp SYNC] ERROR: {str(e)}")
            return False

whatsapp_service = WhatsAppService()