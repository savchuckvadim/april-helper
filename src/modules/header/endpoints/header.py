from fastapi import APIRouter
from fastapi.responses import JSONResponse
from src.modules.header.model.header import HeaderClient
from src.modules.header.model.header import Header
from src.modules.header.services.header_service import header

router = APIRouter(prefix="/header", tags=['Шапка документа'])

@router.post("/create")
async def document_header(
    executor: Header = None,
    client: HeaderClient = None,
) -> JSONResponse:
    """
    Возвращает строку шапки документа\n
    executor:
    - name_organization: название организации
    - position_director: должность руководителя
    - fio_director: ФИО руководителя
    - grounds: действующий на основании

    client:
    - type: 1 - юр.лицо.
    2 - физ. лицо
    - name_organization: название организации
    - position_director: должность руководителя
    - fio_director: ФИО руководителя
    - grounds: действующий на основании

    """
    text = await header(executor=executor, client=client)
    return JSONResponse({"result": text}, status_code=200)