
import httpx
from app.config import settings

def send_whatsapp_message(phone_number: str, code: str) -> bool:
    url = f"https://graph.facebook.com/v19.0/{settings.PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "template",
        "template": {
            "name": settings.TEMPLATE_NAME,
            "language": {"code": "es"},
            "components": [{
                "type": "body",
                "parameters": [{"type": "text", "text": code}]
            }]
        }
    }
    try:
        response = httpx.post(url, json=payload, headers=headers)
        return response.status_code == 200
    except Exception:
        return False
