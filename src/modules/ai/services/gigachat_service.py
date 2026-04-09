import os
from src.api.http.exceptions import AppException
from dotenv import load_dotenv
from langchain_gigachat import GigaChatEmbeddings
from langchain_gigachat import GigaChat
from src.modules.ai.model.base_llm import LLMBase
from src.modules.ai.pipelines.long_dialogue_pipeline import LongDialoguePipeline
from src.modules.ai.utils.langchain_helpers import extract_result
from src.modules.ai_admin.services.runtime_settings_service import RuntimeSettingsService


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
        self.runtime_settings = RuntimeSettingsService()

    async def resume(self, query: str, domain: str | None = None, use_portal_settings: bool = False):
        try:
            # prompt = LLMBase.resume_prompt(with_history=False)
            # chain = prompt | self.llm  # Просто prompt + LLM, без retriever
            # result = chain.invoke({
            #     "input": query,
           
            # })
            # return extract_result(result)  # уже строка
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
            if LongDialoguePipeline.needs_chunked_processing(query):
                pipeline = LongDialoguePipeline(llm=self.llm, retriever=retriever)
                return pipeline.run_resume(query)

            chain = LLMBase.build_resume_chain(
                llm=self.llm,
                retriever=retriever,
                with_history=False,
                system_prompt_override=runtime.prompt,
            )

            result = chain.invoke({
                "input": query,
                "context": ""
            })

            return extract_result(result)
        except Exception as e:
            print(f"❌ GigaChatService recommendation error: {e}")
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
            if LongDialoguePipeline.needs_chunked_processing(query):
                pipeline = LongDialoguePipeline(llm=self.llm, retriever=retriever)
                return pipeline.run_recommendation(query)

            chain = LLMBase.build_chain(
                llm=self.llm,
                retriever=retriever,
                with_history=False,
                system_prompt_override=runtime.prompt,
            )

            result = chain.invoke({
                "input": query,
                "context": ""
            })

            return extract_result(result)

        except Exception as e:
            print(f"❌ GigaChatService recommendation error: {e}")
            raise AppException(status_code=500, detail=str(e))
