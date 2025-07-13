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
                "language": {"code": "es"},  # 🔥 CAMBIO: ESPAÑOL
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