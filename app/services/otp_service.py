import random
import time
from typing import Dict, Optional

class OTPService:
    def __init__(self):
        self._storage: Dict[str, Dict] = {}

    def generate_and_store_code(self, phone_number: str) -> str:
        """Genera y almacena un código OTP de 6 dígitos"""
        code = str(random.randint(100000, 999999))
        self._storage[phone_number] = {
            "code": code, 
            "timestamp": time.time()
        }
        return code

    def verify_code(self, phone_number: str, code: str) -> bool:
        """Verifica si el código OTP es válido (5 minutos de expiración)"""
        entry = self._storage.get(phone_number)
        if entry and entry["code"] == code:
            # Verificar que no haya expirado (5 minutos = 300 segundos)
            if time.time() - entry["timestamp"] < 300:
                return True
        return False

    def generate_token(self, phone_number: str) -> str:
        """Genera un token simple para el usuario"""
        return f"tijzi-token-{phone_number}-{int(time.time())}"

    def get_stored_codes(self) -> Dict:
        """Debug: Ver códigos almacenados"""
        return self._storage