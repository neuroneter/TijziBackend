
import random
import time

class OTPService:
    def __init__(self):
        self._storage = {}

    def generate_and_store_code(self, phone_number):
        code = str(random.randint(100000, 999999))
        self._storage[phone_number] = {"code": code, "timestamp": time.time()}
        return code

    def verify_code(self, phone_number, code):
        entry = self._storage.get(phone_number)
        if entry and entry["code"] == code and time.time() - entry["timestamp"] < 300:
            return True
        return False

    def generate_token(self, phone_number):
        return f"mock-token-for-{phone_number}"
