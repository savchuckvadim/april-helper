import httpx
from src.core.config.settings import settings
from src.api.entities.api_dto import APIRequest
from src.api.clients.bx_action.bx_action_dto import BxActionServiceDTO
from src.api.entities.api_dto import APIMethod
from pydantic import BaseModel


class BxActionAPI:
    def __init__(self):
        
        self.base_url = settings.bx_action_base_url
        self.api_key = settings.bx_action_api_key
        
        

    async def service(self, service: BxActionServiceDTO) -> APIRequest:
      
        url = f"{self.base_url}/{service.endpoint}"
        async with httpx.AsyncClient() as client:
            

        
            method_to_call = getattr(client, service.method)
            headers={'X-HELPER-API-KEY' : self.api_key}
            
            
    
    
            if service.method == APIMethod.GET.value:
                response = await method_to_call(url, params=service.data, headers=headers)
            else:
                if isinstance(service.data, BaseModel):
                    payload = service.data.model_dump()
                else:
                    payload = service.data
                response = await method_to_call(url, json=payload, headers=headers)
      
            if response.status_code == 200:          
              response_data = response.json()

            # Специфическая обработка респонса
            if "error" in response_data:
                raise ValueError("Error fetching portal data")

            return response_data




