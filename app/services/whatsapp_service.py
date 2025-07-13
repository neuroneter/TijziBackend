import httpx
import os
from typing import Optional

class WhatsAppService:
    def __init__(self):
        # Variables de entorno (configuraremos en Render)
        self.access_token = os.getenv("ACCESS_TOKEN", "EAARCZANcIBdYBOZCKwQcvHOEw9PPqC08shdcoGvf10t6TjrvxhKmHijsnpMesLFftnTYrGiXQZB9HsyZCOhs0ht20BD1Uceb4k1CoDbXHTZAKwnZBOlhuzGDnS1EUu0NiRVDZB0msdHcfvYprpMQFS9OQsNkeIRn5qK89kJXGIb1bXF7JkmYjTaZCOdDZB82efY8G0yemPMNezY61JdlChOBjZAeEeUUr3Wuy5TsnQzyW2FS3cDbQZD")
        self.phone_number_id = os.getenv("PHONE_NUMBER_ID", "465399596649912")
        self.template_name = os.getenv("TEMPLATE_NAME", "otp_login")
        
        # URL base de WhatsApp API v19.0
        self.base_url = f"https://graph.facebook.com/v19.0/{self.phone_number_id}/messages"
        
        print(f"🔥 [WhatsApp] Initialized with Phone ID: {self.phone_number_id[:10]}...")

    async def send_otp_message(self, phone_number: str, otp_code: str) -> bool:
        """
        Envía código OTP via WhatsApp usando template
        
        Args:
            phone_number: Número completo con código de país (ej: +573001234567)
            otp_code: Código OTP de 6 dígitos
            
        Returns:
            bool: True si el mensaje se envió exitosamente
        """
        try:
            # Validar credenciales
            if not self.access_token or not self.phone_number_id:
                print("🔥 [WhatsApp ERROR] Missing credentials")
                return False
            
            # Headers para la API de WhatsApp
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Payload para template de OTP
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "template",
                "template": {
                    "name": self.template_name,
                    "language": {"code": "es"},  # Español
                    "components": [{
                        "type": "body",
                        "parameters": [{
                            "type": "text",
                            "text": otp_code
                        }]
                    }]
                }
            }
            
            print(f"🔥 [WhatsApp] Sending to: {phone_number}")
            print(f"🔥 [WhatsApp] Template: {self.template_name}")
            print(f"🔥 [WhatsApp] Code: {otp_code}")
            
            # Enviar request a WhatsApp API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                print(f"🔥 [WhatsApp] Status: {response.status_code}")
                
                if response.status_code == 200:
                    response_data = response.json()
                    print(f"🔥 [WhatsApp] SUCCESS: {response_data}")
                    return True
                else:
                    error_text = response.text
                    print(f"🔥 [WhatsApp] ERROR: {response.status_code} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"🔥 [WhatsApp] EXCEPTION: {str(e)}")
            return False

    def send_otp_message_sync(self, phone_number: str, otp_code: str) -> bool:
        """
        Versión síncrona para compatibilidad
        """
        import asyncio
        try:
            return asyncio.run(self.send_otp_message(phone_number, otp_code))
        except Exception as e:
            print(f"🔥 [WhatsApp SYNC] ERROR: {str(e)}")
            return False

# Instancia global del servicio
whatsapp_service = WhatsAppService()