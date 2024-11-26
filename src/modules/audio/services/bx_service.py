from src.api.clients.bx_action.bx_action_dto import BxActionServiceDTO, BXActionEndpoint
from src.api.clients.bx_action.bx_action_api import BxActionAPI
from src.api.entities.api_dto import APIMethod
from src.modules.audio.entities.time_line_dto import TimeLineDTO


class BxService:
        
    async def set_links_in_timeline(self, data=TimeLineDTO):
        
        timeline_data=data.model_dump()
        bx_api = BxActionAPI()
        set_timeline_data = BxActionServiceDTO(
            method=APIMethod.POST.value,
            endpoint=BXActionEndpoint.TIMELINE.value,
            data=timeline_data
        )
        result = await bx_api.service(service=set_timeline_data)
        print(result)
        
        return result
    

        
        
    
        beeline_result = await self.__set_links_in_timeline() # функция которая берет данные из билайн
        
        beeline_data = self.__get_clean_beeline_links_data # функция которая подготавливает данные из билайн для отправки в таймлайн должна вернуть тп test_data
    
        test_data = TimeLineDTO(
            companyId=36582,
            domain='april-garant.bitrix24.ru',
            links=[],
            message='new code'
            ) 
        
        bx_result = await self.__set_links_in_timeline(test_data)
      
        result = {bx_result: bx_result, beeline_result:beeline_result}
        print(result)
        return result