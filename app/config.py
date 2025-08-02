# app/config.py
import os
from typing import Optional

class Settings:
    """
    Configuración centralizada para el backend de Tijzi
    """
    
    # 🔥 WHATSAPP CREDENTIALS
    ACCESS_TOKEN: str = os.getenv(
        "ACCESS_TOKEN", 
        "EAARCZANcIBdYBOZCKwQcvHOEw9PPqC08shdcoGvf10t6TjrvxhKmHijsnpMesLFftnTYrGiXQZB9HsyZCOhs0ht20BD1Uceb4k1CoDbXHTZAKwnZBOlhuzGDnS1EUu0NiRVDZB0msdHcfvYprpMQFS9OQsNkeIRn5qK89kJXGIb1bXF7JkmYjTaZCOdDZB82efY8G0yemPMNezY61JdlChOBjZAeEeUUr3Wuy5TsnQzyW2FS3cDbQZD"
    )
    PHONE_NUMBER_ID: str = os.getenv("PHONE_NUMBER_ID", "465399596649912")
    TEMPLATE_NAME: str = os.getenv("TEMPLATE_NAME", "otp_login")
    
    # 🔥 API CONFIGURATION
    WHATSAPP_API_VERSION: str = os.getenv("WHATSAPP_API_VERSION", "v19.0")
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    
    # 🔥 OTP CONFIGURATION
    OTP_LENGTH: int = int(os.getenv("OTP_LENGTH", "6"))
    OTP_EXPIRY_MINUTES: int = int(os.getenv("OTP_EXPIRY_MINUTES", "5"))
    
    # 🔥 DEBUGGING
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate_whatsapp_config(cls) -> bool:
        """
        Valida que las credenciales de WhatsApp estén configuradas
        """
        return (
            cls.ACCESS_TOKEN and 
            cls.PHONE_NUMBER_ID and 
            cls.TEMPLATE_NAME and
            len(cls.ACCESS_TOKEN) > 50 and
            cls.PHONE_NUMBER_ID.isdigit()
        )
    
    @classmethod
    def get_whatsapp_base_url(cls) -> str:
        """
        Construye la URL base para la API de WhatsApp
        """
        return f"https://graph.facebook.com/{cls.WHATSAPP_API_VERSION}/{cls.PHONE_NUMBER_ID}/messages"
    
    @classmethod
    def print_config_status(cls) -> None:
        """
        Imprime el estado de la configuración (para debugging)
        """
        print("🔥 [CONFIG] Tijzi Backend Configuration:")
        print(f"   - Template: {cls.TEMPLATE_NAME}")
        print(f"   - Phone ID: {cls.PHONE_NUMBER_ID}")
        print(f"   - API Version: {cls.WHATSAPP_API_VERSION}")
        print(f"   - OTP Length: {cls.OTP_LENGTH}")
        print(f"   - OTP Expiry: {cls.OTP_EXPIRY_MINUTES} minutes")
        print(f"   - Debug Mode: {cls.DEBUG_MODE}")
        print(f"   - Access Token: {'✅ Configured' if cls.ACCESS_TOKEN and len(cls.ACCESS_TOKEN) > 50 else '❌ Missing'}")
        print(f"   - WhatsApp Config Valid: {'✅ Yes' if cls.validate_whatsapp_config() else '❌ No'}")

# Instancia global de configuración
settings = Settings()

# Imprimir configuración al importar (solo en debug mode)
if settings.DEBUG_MODE:
    settings.print_config_status()