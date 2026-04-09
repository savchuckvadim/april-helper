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
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    queue_task_ttl_seconds = int(os.getenv("QUEUE_TASK_TTL_SECONDS", "3600"))

    #     # Указываем явно путь к .env
    #     env_file = ".env"
    #     env_file_encoding = "utf-8"


settings = Settings()
