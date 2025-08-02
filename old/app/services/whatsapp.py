import httpx
import os
from typing import Optional

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

    async def send_otp_message(self, phone_number: str, otp_code: str) -> bool:
        """
        Envía un mensaje OTP vía WhatsApp usando el template configurado
        """
        try:
            if not self.access_token or not self.phone_number_id:
                print("🔥 [WhatsApp ERROR] Missing credentials")
                return False
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # 🔥 LIMPIAR NÚMERO DE TELÉFONO (remover +)
            clean_phone = phone_number.replace("+", "")
            
            # 🔥 PAYLOAD ACTUALIZADO PARA ESPAÑOL CON COPY CODE BUTTON
            payload = {
                "messaging_product": "whatsapp",
                "to": clean_phone,
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

            print(f"🔥 [WhatsApp] Sending to: {clean_phone}")
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
                
                if response.status_code == 200:
                    print(f"🔥 [WhatsApp SUCCESS] Message sent to {phone_number}")
                    return True
                else:
                    print(f"🔥 [WhatsApp ERROR] Failed with status {response.status_code}")
                    print(f"🔥 [WhatsApp ERROR] Response: {response.text}")
                    return False
                
        except Exception as e:
            print(f"🔥 [WhatsApp EXCEPTION] {str(e)}")
            return False

    def validate_credentials(self) -> bool:
        """
        Valida que las credenciales estén configuradas correctamente
        """
        return (
            self.access_token and 
            self.phone_number_id and 
            self.template_name and
            len(self.access_token) > 50 and  # Los tokens son largos
            self.phone_number_id.isdigit()   # Phone Number ID son números
        )

    async def test_connection(self) -> dict:
        """
        Función de prueba para verificar que la conexión funciona
        """
        if not self.validate_credentials():
            return {
                "status": "error",
                "message": "Invalid credentials"
            }
        
        try:
            # Test de conectividad básica
            async with httpx.AsyncClient() as client:
                # Endpoint para verificar el número de teléfono
                test_url = f"https://graph.facebook.com/v19.0/{self.phone_number_id}"
                headers = {"Authorization": f"Bearer {self.access_token}"}
                
                response = await client.get(test_url, headers=headers, timeout=10.0)
                
                if response.status_code == 200:
                    return {
                        "status": "success",
                        "message": "WhatsApp API connection successful",
                        "phone_number_id": self.phone_number_id
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"API returned status {response.status_code}",
                        "response": response.text
                    }
                    
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection failed: {str(e)}"
            }

# 🔥 INSTANCIA GLOBAL para ser importada desde auth.py
whatsapp_service = WhatsAppService()