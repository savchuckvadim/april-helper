from enum import Enum
from pydantic import BaseModel


# Определение перечисления
class APIMethod(str, Enum):
    GET = 'get'
    POST = 'post'


class APIResultCode(int, Enum):
    SUCCESS = 0
    ERROR = 1


class APIRequest(BaseModel):
    resultCode: APIResultCode
    message: str
    data: int