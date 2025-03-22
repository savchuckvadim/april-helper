from langchain_core.messages.ai import AIMessage


def extract_result(result) -> str:
    """
    Возвращает текст из результата chain.invoke().
    Поддерживает типы AIMessage, dict (с ключом 'answer'), или просто строку.
    """
    if isinstance(result, AIMessage):
        return result.content
    elif isinstance(result, dict) and "answer" in result:
        return result["answer"]
    elif isinstance(result, str):
        return result
    else:
        return str(result)
