# bx_api:
import requests
from fastapi import HTTPException
from src.core.config import settings
from src.modules.audio.entities.audio_from_beeline_to_bx_dto import SendToTimelineCallsLinksDTO
from src.core.config.settings import settings


class BxAPI:
    def __init__(self):
        self.headers = {
             "Content-Type": "application/json",
             "X-HELPER-API-KEY": settings.bx_action_api_key
         }
        self.bitrix_url = settings.bx_action_base_url

    def send_to_bitrix(self, data: SendToTimelineCallsLinksDTO):
        # Подготовка данных для отправки
        payload = {
            "domain": data.domain,
            "links": data.links,
            "companyId": data.companyId,
            "message": data.message
        }
        try:
            # Отправка POST-запроса
            response = requests.post(self.bitrix_url, json=payload, headers=self.headers)
            response.raise_for_status()

            # Проверка статуса ответа
            if response.status_code == 200:
                print(f"Успешно отправлено в Bitrix24: {response.json()}")
            else:
                print(f"Ошибка при отправке в Bitrix24. Код ответа: {response.status_code}")
                print(f"Ответ от сервера: {response.text}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Ошибка при отправке данных в Bitrix24. Код ответа: {response.status_code}, Ответ: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе в Bitrix24: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка при запросе в Bitrix24: {str(e)}"
            )


bx_api = BxAPI()
