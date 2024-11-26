import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    portal_base_url = os.getenv("URL_API_APRIL")
    portal_api_key = os.getenv("API_TOKEN_APRIL")
    bx_action_base_url = os.getenv("URL_BX_ACTION")
    bx_action_api_key = os.getenv("API_TOKEN_BX_ACTION")
    beeline_base_url = os.getenv("URL_BEELINE_API")
    beeline_api_key = os.getenv("API_TOKEN_BEELINE")


settings = Settings()
