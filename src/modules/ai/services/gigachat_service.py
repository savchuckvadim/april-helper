import os
from src.api.http.exceptions import AppException
from dotenv import load_dotenv
from langchain_gigachat import GigaChatEmbeddings
from langchain_gigachat import GigaChat
from src.modules.ai.model.base_llm import LLMBase
from src.modules.ai.utils.langchain_helpers import extract_result


class GigaChatService:
    def __init__(self, model_name:str):
        load_dotenv()
        self.model_name = model_name
        self.api_key = os.getenv("GIGACHAT_API_KEY")
        if not self.api_key:
            raise ValueError("❌ Missing GIGACHAT_API_KEY")
        self.llm = GigaChat(credentials=self.api_key, verify_ssl_certs=False)

        self.embeddings = GigaChatEmbeddings(
            credentials=self.api_key, verify_ssl_certs=False
        )

    async def resume(self, query: str):
        try:
            # prompt = LLMBase.resume_prompt(with_history=False)
            # chain = prompt | self.llm  # Просто prompt + LLM, без retriever
            # result = chain.invoke({
            #     "input": query,
           
            # })
            # return extract_result(result)  # уже строка
            retriever = LLMBase.get_retriver(self.embeddings, self.model_name)
            chain = LLMBase.build_resume_chain(
                llm=self.llm,
                retriever=retriever,
                with_history=False
            )

            # chat_history = []
            result = chain.invoke({
                "input": query,
                "context": ""
                # "chat_history": chat_history
            })

   
            return extract_result(result)
        except Exception as e:
            print(f"❌ GigaChatService recommendation error: {e}")
            raise AppException(status_code=500, detail=str(e))

    

    async def recomendation(self, query: str):
        try:
            # 🧠 1. Получаем retriever
            retriever = LLMBase.get_retriver(self.embeddings, self.model_name)
            chain = LLMBase.build_chain(
                llm=self.llm,
                retriever=retriever,
                with_history=False
            )

            # chat_history = []
            result = chain.invoke({
                "input": query,
                "context": ""
                # "chat_history": chat_history
            })

   
            return extract_result(result)

        except Exception as e:
            print(f"❌ GigaChatService recommendation error: {e}")
            raise AppException(status_code=500, detail=str(e))
