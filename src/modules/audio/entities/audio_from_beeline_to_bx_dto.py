from pydantic import BaseModel

class AudioFromBeelineToBxDTO(BaseModel):
    domain:str
    companyId:int
    date_from: str
    date_to: str
    userId: int
    phone_client: str
    duration_call_minute: int 