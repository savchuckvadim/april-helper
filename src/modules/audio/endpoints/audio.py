from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from src.modules.audio.entities.audio_from_beeline_to_bx_dto import AudioFromBeelineToBxDTO
from src.modules.audio.usecases.audio_from_beeline_to_bx_case import AudioFromBeelineToBxCase



router = APIRouter(prefix="/audio", tags=['Получить аудио-файл из билайн в битрикс веб-хук'])

# class Payload(BaseModel):
    # date_from: str  # Формат даты: 'YYYY-MM-DD'
    # date_to: str
    # userId: int
    # phone_client: str
    # duration_call_minut: int

@router.post("/audio/")
async def audio(
    request: Request,
    date_from: str,  # Формат даты: 'YYYY-MM-DD'
    date_to: str,
    userId: int,
    phone_client: str,
    duration_call_minut: int 
    ):
    print(request.query_params)

    return JSONResponse({"result": request}, status_code=200)



@router.post("/test/")
async def test(  
    request: Request,
    # domain: str, 
    # companyId: int, 
    # date_from: str,
    # date_to: str,
    # userId: int,
    # phone_client: str,
    # duration_call_minute: int 
    ):
    
    domain='april-garant.bitrix24.ru'
    companyId=36582
    date_from='01.11.2024'
    date_to='22.11.2024'
    userId=705
    phone_client='+796200299999'
    duration_call_minute=1
    
    data = AudioFromBeelineToBxDTO(
        domain=domain,
        companyId=companyId,
        date_from=date_from,
        date_to=date_to,
        userId=userId,
        phone_client=phone_client,
        duration_call_minute=duration_call_minute
    )
    
    
    service = AudioFromBeelineToBxCase(dto=data)
    result = await service.get_and_push_links()
    
    return JSONResponse({'result':result})