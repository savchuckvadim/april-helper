from src.modules.header.model import header as Header
from src.modules.header.lib.fio.fio import genitive, to_fio_genitive, to_position_genitive


async def header(executor: Header.Header | None, client: Header.HeaderClient | None):
    if executor is None:
        executor = Header.Header()
    if client is None:
        client = Header.HeaderClient()

    executor.fio_director = to_fio_genitive(executor.fio_director)
    if " " in executor.position_director:
        executor.position_director = to_position_genitive(executor.position_director)
    else:
        executor.position_director = genitive(executor.position_director)

    client.fio_director = to_fio_genitive(client.fio_director)
    if " " in client.position_director:
        client.position_director = to_position_genitive(client.position_director)
    else:
        client.position_director = genitive(client.position_director)
    if client.type == 1:  # юр лицо
        text = (
            f'{executor.name_organization}, именуемое в дальнейшем "ИСПОЛНИТЕЛЬ", '
            f"в лице {executor.position_director} {executor.fio_director}, "
            f"действующего на основании {executor.grounds} с одной стороны и {client.name_organization}, "
            f'именуемое(-ый) в дальнейшем "ЗАКАЗЧИК", '
            f"в лице {client.position_director} {client.fio_director}, "
            f"действующего(-ей) на основании {client.grounds}"
            f"с другой стороны, совместно и по отдельности, именуемые соответственно «стороны» и «сторона», "
            f"заключили настоящий   «ДОГОВОР» о нижеследующем"
        )
    elif client.type == 2:  # физ. лицо
        text = (
            f'{executor.name_organization}, именуемое в дальнейшем "ИСПОЛНИТЕЛЬ", '
            f"в лице {executor.position_director} {executor.fio_director}, "
            f"действующего на основании {executor.grounds} с одной стороны и {client.name_organization}, "
            f'именуемое(-ый) в дальнейшем "ЗАКАЗЧИК", '
            f"в лице {client.fio_director}, "
            f"действующего(-ей) на основании {client.grounds}"
            f"с другой стороны, совместно и по отдельности, именуемые соответственно «стороны» и «сторона», "
            f"заключили настоящий   «ДОГОВОР» о нижеследующем"
        )
    else:
        text = (
            "Укажите тип клиента: type:1 > Юридическое лицо, type:2 > физическое лицо"
        )
    return text
