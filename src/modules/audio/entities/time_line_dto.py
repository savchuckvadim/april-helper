from pydantic import BaseModel
from typing import Any

class TimeLineDTO(BaseModel):
    domain:str
    companyId:int
    links: Any=None
    message:str