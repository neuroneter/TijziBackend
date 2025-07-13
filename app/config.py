import os

class Settings:
    ACCESS_TOKEN: str = os.getenv("ACCESS_TOKEN", "EAARCZANcIBdYBOZCKwQcvHOEw9PPqC08shdcoGvf10t6TjrvxhKmHijsnpMesLFftnTYrGiXQZB9HsyZCOhs0ht20BD1Uceb4k1CoDbXHTZAKwnZBOlhuzGDnS1EUu0NiRVDZB0msdHcfvYprpMQFS9OQsNkeIRn5qK89kJXGIb1bXF7JkmYjTaZCOdDZB82efY8G0yemPMNezY61JdlChOBjZAeEeUUr3Wuy5TsnQzyW2FS3cDbQZD")
    PHONE_NUMBER_ID: str = os.getenv("PHONE_NUMBER_ID", "465399596649912") 
    TEMPLATE_NAME: str = os.getenv("TEMPLATE_NAME", "otp_login")

settings = Settings()