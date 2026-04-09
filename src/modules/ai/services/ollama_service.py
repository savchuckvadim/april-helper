import os

from dotenv import load_dotenv
from src.api.http.exceptions import AppException

from src.modules.ai.model.base_llm import LLMBase
from src.modules.ai.utils.langchain_helpers import extract_result
from src.modules.ai_admin.services.runtime_settings_service import RuntimeSettingsService

from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings


class OllamaService:
    def __init__(self, model_name: str):
        self.model_name = model_name
        load_dotenv()
        self.ollama_url = os.getenv("OLLAMA_BASE_URL")
        self.chat_model = os.getenv("OLLAMA_CHAT_MODEL", "mistral")
        print("OllamaService")
        self.llm = OllamaLLM(
            model=self.chat_model,
            base_url=self.ollama_url or "http://45.12.74.239:11434",
        )
        print(self.ollama_url)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
        self.runtime_settings = RuntimeSettingsService()

    async def resume(self, query: str, domain: str | None = None, use_portal_settings: bool = False):
        try:
            print("resume")

            # prompt = LLMBase.resume_prompt(with_history=True)
            # chain = prompt | self.llm  # Просто prompt + LLM, без retriever
            # chat_history =  []
            # result = chain.invoke({
            #     "input": query,
            #     "chat_history": chat_history
            # })
            runtime = self.runtime_settings.resolve(domain=domain, kind="resume", use_portal_settings=use_portal_settings)
            if runtime.source != "portal":
                print(f"ℹ️ resume settings source: {runtime.source}; issues={len(runtime.issues)}")
            retriever = LLMBase.get_retriver(
                self.embeddings,
                self.model_name,
                retrive_root=runtime.retrive_root,
                retrive_paths=runtime.retrive_paths,
                domain=domain if runtime.source == "portal" else None,
                kind="resume" if runtime.source == "portal" else None,
                content_hash=runtime.content_hash,
            )
            print("retriever")
            print("🔗 2. Собираем цепочку с учётом истории")

            chain = LLMBase.build_resume_chain(
                llm=self.llm, retriever=retriever, with_history=True, system_prompt_override=runtime.prompt
            )
            chat_history = []
            print("🚀 4. Запрос")

            # result = chain.invoke(
            #     {"input": query, "chat_history": chat_history, "context": ""}
            # )
            result = await chain.ainvoke(
                {"input": query, "chat_history": chat_history, "context": ""}
            )
            print(" Ответ получен")
            return extract_result(result)

        except Exception as e:
            print(f"❌ Ollama resume error: {e}")
            raise AppException(status_code=500, detail=str(e))

    async def recomendation(self, query: str, domain: str | None = None, use_portal_settings: bool = False):
        try:
            # 🧠 1. Получаем retriever
            runtime = self.runtime_settings.resolve(
                domain=domain, kind="recomendation", use_portal_settings=use_portal_settings
            )
            if runtime.source != "portal":
                print(f"ℹ️ recommendation settings source: {runtime.source}; issues={len(runtime.issues)}")
            retriever = LLMBase.get_retriver(
                self.embeddings,
                self.model_name,
                retrive_root=runtime.retrive_root,
                retrive_paths=runtime.retrive_paths,
                domain=domain if runtime.source == "portal" else None,
                kind="recomendation" if runtime.source == "portal" else None,
                content_hash=runtime.content_hash,
            )
            print("retriever")
            print("🔗 2. Собираем цепочку с учётом истории")

            chain = LLMBase.build_chain(
                llm=self.llm, retriever=retriever, with_history=True, system_prompt_override=runtime.prompt
            )

            # 💬 3. История чата (пока пустая, можно позже подключить хранение)
            chat_history = []

            print("🚀 4. Запрос")
            # result = chain.invoke(
            #     {"input": query, "chat_history": chat_history, "context": ""}
            # )
            result = await chain.ainvoke(
                {"input": query, "chat_history": chat_history, "context": ""}
            )
            print(" Ответ получен")
            # ✅ 5. Возвращаем результат
            return extract_result(result)

        except Exception as e:
            print(f"❌ Ollama recommendation error: {e}")
            raise AppException(status_code=500, detail=str(e))
