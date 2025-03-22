import os

from dotenv import load_dotenv
from src.api.http.exceptions import AppException

from src.modules.ai.model.base_llm import LLMBase
from src.modules.ai.utils.langchain_helpers import extract_result

from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings

class OllamaService:
    def __init__(self):
        load_dotenv()
        self.ollama_url = os.getenv("OLLAMA_BASE_URL")
        if not self.api_key:
            raise ValueError("❌ Missing GIGACHAT_API_KEY")
        self.llm = OllamaLLM(
            model="mistral",
            base_url=os.getenv(self.ollama_url, "http://45.12.74.239:11434")
        )

        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")


    async def resume(self, query: str):
        try:
            retriever = LLMBase.get_retriver(self.embeddings)
            chain = LLMBase.build_resume_chain(llm=self.llm, retriever=retriever, with_history=True)
          
            chat_history = []

            # 🚀 4. Выполнение запроса
            result = chain.invoke({
                "input": query,
                "chat_history": chat_history
            })

            # ✅ 5. Возвращаем чистый результат
            return extract_result(result)
        
        except Exception as e:
            print(f"❌ Ollama recommendation error: {e}")
            raise AppException(status_code=500, detail=str(e))
        

    async def recomendation(self, query: str):
        try:
            # 🧠 1. Получаем retriever
            retriever = LLMBase.get_retriver(self.embeddings)

            # 🔗 2. Собираем цепочку с учётом истории
            chain = LLMBase.build_chain(
                llm=self.llm,
                retriever=retriever,
                with_history=True
            )

            # 💬 3. История чата (пока пустая, можно позже подключить хранение)
            chat_history = []

            # 🚀 4. Запрос
            result = chain.invoke({
                "input": query,
                "chat_history": chat_history
            })

            # ✅ 5. Возвращаем результат
            return extract_result(result)

        except Exception as e:
            print(f"❌ Ollama recommendation error: {e}")
            raise AppException(status_code=500, detail=str(e))