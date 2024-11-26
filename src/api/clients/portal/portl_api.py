import httpx
from core.config import settings
from entities.april import PortalDTO

class PortalAPI:
    BASE_URL = settings.portal_base_url

    async def fetch_portal_data(self, domain: str) -> PortalDTO:
        url = f"{self.BASE_URL}/getPortal"
        params = {"domain": domain}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response_data = response.json()

            # Специфическая обработка респонса
            if "error" in response_data:
                raise ValueError("Error fetching portal data")

            return PortalDTO(**response_data)

    async def get_hook(self) -> str:
        # Метод для получения хука
        return f"{self.BASE_URL}/hook?access_key={settings.portal_access_key}"

    # Другие специфические методы для Portal API
