import os
from src.api.http.exceptions import AppException
from dotenv import load_dotenv
from langchain_gigachat import GigaChatEmbeddings
from langchain_gigachat import GigaChat
from src.modules.ai.model.base_llm import LLMBase
from src.modules.ai.utils.langchain_helpers import extract_result


class GigaChatService:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GIGACHAT_API_KEY")
        if not self.api_key:
            raise ValueError("❌ Missing GIGACHAT_API_KEY")
        self.llm = GigaChat(credentials=self.api_key, verify_ssl_certs=False)

        self.embeddings = GigaChatEmbeddings(
            credentials=self.api_key, verify_ssl_certs=False
        )

    async def resume(self, query: str):
        try:
            retriever = LLMBase.get_retriver(self.embeddings)
            chain = LLMBase.build_resume_chain(llm=self.llm, retriever=retriever)

            result = chain.invoke(
                {"input": query, "chat_history": []}  # пустая история по умолчанию
            )
            return extract_result(result)  # уже строка
        except Exception as e:
            print(f"❌ Ollama recommendation error: {e}")
            raise AppException(status_code=500, detail=str(e))

    # async def recomendation(self, query: str):
    #     try:

    #         retriever = LLMBase.get_retriver(self.embeddings)
    #         # Создание цепочек
    #         prompt = LLMBase.recomendation_prompt()
    #         document_chain = create_stuff_documents_chain(self.llm, prompt)
    #         retrieval_chain = create_retrieval_chain(retriever, document_chain)

    #         # Запуск
    #         chat_history = []
    #         result = retrieval_chain.invoke(
    #             {"input": query, "chat_history": chat_history}
    #         )

    #         return extract_result(result)
    #     except Exception as e:
    #         print(f"❌ GigaChat recommendation error: {e}")
    #         return JSONResponse({"error": str(e)}, status_code=500)

    async def recomendation(self, query: str):
        try:
            # 🧠 1. Получаем retriever
            retriever = LLMBase.get_retriver(self.embeddings)
            chain = LLMBase.build_chain(
                llm=self.llm,
                retriever=retriever,
                with_history=False
            )

            # chat_history = []
            result = chain.invoke({
                "input": query,
                # "chat_history": chat_history
            })

   
            return extract_result(result)

        except Exception as e:
            print(f"❌ Ollama recommendation error: {e}")
            raise AppException(status_code=500, detail=str(e))
