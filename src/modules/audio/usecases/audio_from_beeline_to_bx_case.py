from src.modules.audio.entities.time_line_dto import TimeLineDTO
from src.modules.audio.services.bx_service import BxService


from ..entities.audio_from_beeline_to_bx_dto import AudioFromBeelineToBxDTO

class AudioFromBeelineToBxCase:
    def __init__(self, dto: AudioFromBeelineToBxDTO):
        self.domain = dto.domain
        self.companyId = dto.companyId
        self.userId = dto.userId    
        self.date_from = dto.date_from
        self.date_to = dto.date_to
        self.phone_client = dto.phone_client
        self.duration_call_minute = dto.duration_call_minute
        

    async def __get_beeline_links_data(self):
        return 'objects from beeline'
  
    def __get_clean_beeline_links_data(self):
        return 'objects from beeline'
    
    async def get_and_push_links(self):
        
        
        
        beeline_result = await self.__get_beeline_links_data() # функция которая берет данные из билайн
        
        beeline_data = self.__get_clean_beeline_links_data() # функция которая подготавливает данные из билайн для отправки в таймлайн должна вернуть тп test_data
    
        message='Аудиозаписи не найдены' # или найдены
        
        test_data = TimeLineDTO(
            companyId=self.companyId,
            domain=self.domain,
            links=[],
            message=message
            ) 
        bx_service = BxService()
        bx_result = await bx_service.set_links_in_timeline(test_data)
      
        result = {'bx_result': bx_result, 'beeline_result':beeline_result}
        print(result)
        return result