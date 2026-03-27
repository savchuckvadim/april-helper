import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from dotenv import load_dotenv
from src.api.http.exceptions import AppException
from src.modules.ai.model.base_llm import LLMBase
from src.modules.ai.utils.langchain_helpers import extract_result


class OpenAIService:
    def __init__(self, model_name:str):
        load_dotenv()
        self.model_name = model_name
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("❌ Missing GIGACHAT_API_KEY")
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=self.api_key)

        self.embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
    async def resume(self, query: str):
        try:
            retriever = LLMBase.build_resume_chain(self.embeddings, self.model_name)
            chain = LLMBase.build_chain(
                llm=self.llm,
                retriever=retriever,
                with_history=False,
            )
            result = chain.invoke({
                "input": query,
                "context": ""
            })

   
            return extract_result(result)
        except Exception as e:
            print(f"❌ Open AI recommendation error: {e}")
            raise AppException(status_code=500, detail=str(e))
    async def recomendation(self, query: str):
        try:
            # 🧠 1. Получаем retriever
            retriever = LLMBase.get_retriver(self.embeddings, self.model_name)
            chain = LLMBase.build_chain(
                llm=self.llm,
                retriever=retriever,
                with_history=False,
            )
            result = chain.invoke({
                "input": query,
                "context": ""
            })

   
            return extract_result(result)

        except Exception as e:
            print(f"❌ Open AI recommendation error: {e}")
            raise AppException(status_code=500, detail=str(e))


    # async def resume(query: str):
    #     load_dotenv()
    #     OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    #     if not OPENAI_API_KEY:
    #         return JSONResponse({"error": "Missing OPENAI_API_KEY"}, status_code=500)

    #     try:
    #         # Настройка модели LLM
    #         llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)

    #         # Промпт для генерации резюме
    #         prompt = ChatPromptTemplate.from_messages(
    #             [
    #                 (
    #                     "system",
    #                     "Ты — помощник по анализу транскрибации звонков. "
    #                     "Всегда пиши от первого лица. От лица Менеджера. (предложил,предложила, провел презентацию, попробовала договориться и так далее)"
    #                     "Твоя задача — создать краткое резюме разговора. "
    #                     "Наша компания называется Гарант"
    #                     "Если в тексте пишется как-то по-другому или созвучно исправь на  ГАРАНТ"
    #                     "Резюмируя текст пиши от своего лица, как будто ты Менедер по продажам типа Попытался предложить.. Провел презентацию.. и так далее"
    #                     "Напиши возражения с которыми столкнулся менеджер, как он их попытался преодолеть и почему не получилось, если такой момент был"
    #                     "Также напиши какие теперь планы работы с клиентом, что нужно будет сделать в следующий раз при общении чтобы успешно провести презентацию и продать продукт"
    #                     "Пиши развернуто описывая нюансы разговора"
    #                     "Пиши какие успешные и неуспешные моменты в работе с клиентом, что он сделал в конце текста."
    #                     "Особое внимание удели тому общался ли менеджер с лицом принимающим решение или нет"
    #                     "Основной продукт компании — Гарант. В тексте могут быть ошибки распознавания речи. Исправь их если такие есть"
    #                     "Определи ключевые моменты разговора. Если были договоренности по времени — упомяни их. "
    #                     "Также отметь, проводилась ли презентация продукта: напиши 'Презентация: проведена' или 'Презентация: не проведена'."
    #                     "Всегда пиши был ли звонок результативный в конце текста таким образом Звонок: Результативный или Звонок: Нерезультативный",
    #                 ),
    #                 ("human", "{input}"),
    #             ]
    #         )

    #         # Формирование запроса к модели
    #         formatted_prompt = prompt.format(input=query)
    #         result = llm.predict(formatted_prompt)

    #         return result

    #     except Exception as e:
    #         print(f"❌ Ошибка: {e}")
    #         return JSONResponse({"error": str(e)}, status_code=500)

    # async def recomendation(query: str):
    #     load_dotenv()
    #     OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    #     if not OPENAI_API_KEY:
    #         return JSONResponse({"error": "Missing OPENAI_API_KEY"}, status_code=500)

    #     try:
    #         # 🔹 Настройка LLM
    #         embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    #         llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)

    #         # 🔹 Загружаем PDF
    #         file_path = os.path.abspath("retrive_data/data.pdf")
    #         print(f"✅ Файл найден: {file_path}")

    #         # 📥 Читаем PDF
    #         def extract_text_from_pdf(pdf_path):
    #             text = ""
    #             with fitz.open(pdf_path) as doc:
    #                 for page in doc:
    #                     text += page.get_text("text") + "\n"
    #             return text

    #         pdf_text = extract_text_from_pdf(file_path)

    #         # 🔹 Разделяем текст на части
    #         text_splitter = RecursiveCharacterTextSplitter(
    #             chunk_size=250, chunk_overlap=200
    #         )
    #         splits = text_splitter.create_documents([pdf_text])

    #         # 🔹 Создаём векторное хранилище
    #         vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    #         retriever = vectorstore.as_retriever(
    #             search_kwargs={"k": 2}
    #         )  # Получаем 2 ближайших документа

    #         # 🔹 Промпт для рекомендаций
    #         recommendation_prompt = ChatPromptTemplate.from_messages(
    #             [
    #                 (
    #                     "system",
    #                     "Ты эксперт по анализу звонков и продажам ИПО ГАРАНТ. Используй следующие документы, чтобы дать рекомендации.\n\n{context}\n\n"
    #                     "Анализируй, какие ошибки допустил менеджер и как можно было бы провести разговор лучше.",
    #                 ),
    #                 MessagesPlaceholder("chat_history"),
    #                 ("human", "{input}"),
    #             ]
    #         )

    #         # 🔹 Создаём цепочку с рекомендациями
    #         document_chain = create_stuff_documents_chain(llm, recommendation_prompt)
    #         retrieval_chain = create_retrieval_chain(retriever, document_chain)

    #         # 🔹 История чата (можно подключить из базы, но пока пустая)
    #         chat_history = []

    #         # 🔹 Выполняем запрос
    #         result = retrieval_chain.invoke(
    #             {"input": query, "chat_history": chat_history}
    #         )

    #         return result["answer"]

    #     except Exception as e:
    #         print(f"❌ Ошибка: {e}")
    #         return ""
