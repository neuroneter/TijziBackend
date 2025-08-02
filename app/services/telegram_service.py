import os
import httpx
from typing import Optional, Dict

class TelegramService:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None
        
    async def send_otp_telegram(self, telegram_user: str, otp_code: str) -> bool:
        """
        Envía código OTP vía Telegram
        telegram_user puede ser username (@usuario) o chat_id
        """
        try:
            print(f"🔥 [Telegram] Checking credentials...")
            
            if not self.bot_token:
                print("🔥 [Telegram ERROR] Missing bot token")
                return False
            
            print(f"🔥 [Telegram] Bot token configured: {len(self.bot_token)} chars")
            print(f"🔥 [Telegram] Sending to: {telegram_user}")
            
            # Determinar si es username o chat_id
            chat_id = telegram_user
            if telegram_user.startswith("@"):
                # Es username, intentar obtener chat_id
                print(f"🔥 [Telegram] Username detected: {telegram_user}")
                resolved_chat_id = await self._resolve_username_to_chat_id(telegram_user)
                if resolved_chat_id:
                    chat_id = resolved_chat_id
                    print(f"🔥 [Telegram] Resolved to chat_id: {chat_id}")
                else:
                    print(f"🔥 [Telegram] Could not resolve username, trying direct send...")
                    chat_id = telegram_user  # Intentar envío directo
            
            # Mensaje con formato
            message = f"""🔐 *Código de Verificación Tijzi*

Tu código es: `{otp_code}`

⏰ Válido por 5 minutos
🔒 No compartas este código con nadie"""
            
            # Payload para Telegram API
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }
            
            url = f"{self.base_url}/sendMessage"
            
            print(f"🔥 [Telegram] Sending message...")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    timeout=30.0
                )
                
                print(f"🔥 [Telegram] Status: {response.status_code}")
                print(f"🔥 [Telegram] Response: {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("ok"):
                        print(f"🔥 [Telegram SUCCESS] Message sent to {telegram_user}")
                        return True
                    else:
                        error_description = result.get("description", "Unknown error")
                        print(f"🔥 [Telegram ERROR] API error: {error_description}")
                        return False
                else:
                    print(f"🔥 [Telegram ERROR] Failed with status {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"🔥 [Telegram EXCEPTION] {str(e)}")
            return False
    
    async def _resolve_username_to_chat_id(self, username: str) -> Optional[str]:
        """
        Intenta resolver username a chat_id usando getUpdates
        (Solo funciona si el usuario ha interactuado con el bot antes)
        """
        try:
            url = f"{self.base_url}/getUpdates"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("ok"):
                        # Buscar en updates recientes
                        for update in result.get("result", []):
                            message = update.get("message", {})
                            from_user = message.get("from", {})
                            username_clean = username.replace("@", "").lower()
                            
                            if from_user.get("username", "").lower() == username_clean:
                                chat_id = str(message.get("chat", {}).get("id"))
                                print(f"🔥 [Telegram] Found chat_id {chat_id} for {username}")
                                return chat_id
                                
            print(f"🔥 [Telegram] Could not resolve {username} to chat_id")
            return None
            
        except Exception as e:
            print(f"🔥 [Telegram] Error resolving username: {str(e)}")
            return None
    
    async def get_bot_info(self) -> Dict:
        """Obtiene información del bot para verificar configuración"""
        try:
            if not self.bot_token:
                return {"configured": False, "error": "Missing bot token"}
            
            url = f"{self.base_url}/getMe"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("ok"):
                        bot_info = result.get("result", {})
                        return {
                            "configured": True,
                            "bot_username": bot_info.get("username"),
                            "bot_name": bot_info.get("first_name"),
                            "bot_id": bot_info.get("id"),
                            "can_read_all_group_messages": bot_info.get("can_read_all_group_messages"),
                            "supports_inline_queries": bot_info.get("supports_inline_queries")
                        }
                
                return {"configured": False, "error": "Invalid bot token"}
                
        except Exception as e:
            return {"configured": False, "error": str(e)}
    
    def is_configured(self) -> bool:
        """Verifica si el servicio Telegram está configurado"""
        return bool(self.bot_token)
    
    def get_debug_info(self) -> dict:
        """Info de debug para verificar configuración"""
        return {
            "bot_token_configured": bool(self.bot_token),
            "bot_token_length": len(self.bot_token) if self.bot_token else 0,
            "base_url": self.base_url,
            "configured": self.is_configured()
        }