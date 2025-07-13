import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    ACCESS_TOKEN: str = "your_whatsapp_access_token"
    PHONE_NUMBER_ID: str = "your_phone_number_id"
    TEMPLATE_NAME: str = "otp_login"

    class Config:
        env_file = ".env"

settings = Settings()