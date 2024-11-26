from enum import Enum
from pydantic import BaseModel
from src.api.entities.api_dto import APIMethod
# from src.modules.audio.repositories.TimeLineDTO import TimeLineDTO


class BXActionEndpoint(str, Enum):
    TIMELINE='timeline/set'
    
    
class BxActionServiceDTO(BaseModel):
    endpoint: str | BXActionEndpoint
    method: APIMethod
    data: dict


