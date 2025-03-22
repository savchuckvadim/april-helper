# from fastapi import APIRouter
# from fastapi.responses import JSONResponse
# import os
# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# from langchain_community.document_loaders import TextLoader
# from langchain_community.vectorstores import Chroma
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.chains import create_history_aware_retriever
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain.chains import create_retrieval_chain
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from dotenv import load_dotenv
# from langchain_community.llms import LlamaCpp
# from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
# from langchain_core.prompts import PromptTemplate


# router = APIRouter(prefix="/ai", tags=["AI"])

# @router.get("/gpt/")
# async def retrive(query: str):
#     load_dotenv()
#     OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

#     if not OPENAI_API_KEY:
#         return JSONResponse({"error": "Missing OPENAI_API_KEY"}, status_code=500)

#     try:
#         # Настройка эмбеддингов и LLM
#         # embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
#         # Callbacks support token-wise streaming
#         callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
#         llm = LlamaCpp(
#             model_path="/Users/rlm/Desktop/Code/llama.cpp/models/openorca-platypus2-13b.gguf.q4_0.bin",
#             temperature=0.75,
#             max_tokens=2000,
#             top_p=1,
#             callback_manager=callback_manager,
#             verbose=True,  # Verbose is required to pass to the callback manager
#             )

#         # Загрузка и разделение документа
#         file_path = os.path.abspath("data.txt")
#         print(f"✅ Файл найден: {file_path}")

#         # Загрузка документа
#         loader = TextLoader(file_path, encoding="utf-8")
#         documents = loader.load()

#         # Разделение текста на части
#         text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=1000, 
#             chunk_overlap=200
#         )
#         splits = text_splitter.split_documents(documents)

#         # Создание векторного хранилища
#         vectorstore = Chroma.from_documents(
#             documents=splits, 
#             embedding=embeddings
#         )
#         retriever = vectorstore.as_retriever(search_kwargs={"k": 1})

#         # Промпт для переформулировки вопроса
#         contextualize_q_prompt = ChatPromptTemplate.from_messages([
#             ("system", "Если в истории чата есть релевантный контекст, используйте его для переформулировки текущего вопроса."),
#             MessagesPlaceholder("chat_history"),
#             ("human", "{input}")
#         ])

#         # Создание retriever с учетом истории
#         history_aware_retriever = create_history_aware_retriever(
#             llm, 
#             retriever, 
#             contextualize_q_prompt
#         )

#         # Промпт для объединения документов
#         qa_prompt = ChatPromptTemplate.from_messages([
#             ("system", "Используйте следующие документы для ответа на вопрос:\n\n{context}"),
#             MessagesPlaceholder("chat_history"),
#             ("human", "{input}")
#         ])

#         # Создание цепочки для объединения документов
#         document_chain = create_stuff_documents_chain(llm, qa_prompt)

#         # Финальная retrieval chain
#         retrieval_chain = create_retrieval_chain(
#             history_aware_retriever, 
#             document_chain
#         )

#         # Инициализация истории чата
#         chat_history = []

#         # Выполнение запроса
#         result = retrieval_chain.invoke({
#             "input": query,
#             "chat_history": chat_history
#         })

#         return JSONResponse({
#             "result": result["answer"],
#             "sources": [doc.page_content for doc in result.get("context", [])]
#         })



#     except Exception as e:
#         print(f"❌ Ошибка: {e}") 
#         return JSONResponse({"error": str(e)}, status_code=500)
