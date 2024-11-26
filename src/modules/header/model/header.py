from typing import Annotated, Optional
from pydantic import BaseModel, Field


class Header(BaseModel):

    name_organization: Annotated[
        Optional[str],
        Field(default="____________________", description="Наименование организации"),
    ]
    position_director: Annotated[
        Optional[str],
        Field(default="____________________", description="Должность руководителя"),
    ]
    fio_director: Annotated[
        Optional[str],
        Field(default="____________________", description="ФИО руководителя"),
    ]
    grounds: Annotated[
        Optional[str],
        Field(default="____________________", description="Действующий на основании"),
    ]


class HeaderClient(Header):
    type: int = 1
