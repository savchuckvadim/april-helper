# ollama
import os
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings


router = APIRouter(prefix="/ai", tags=["AI"])

@router.get("/gpt/")
async def retrieve(query: str):
    try:
        # Настройка LLM (Ollama) и эмбеддингов
        llm = OllamaLLM(
            model="mistral",
            base_url=os.getenv("OLLAMA_BASE_URL", "http://45.12.74.239:11434")
        )
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

        # Загрузка и разделение документа
        file_path = os.path.abspath("data.txt")
        loader = TextLoader(file_path, encoding="utf-8")
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)

        # Создание векторного хранилища
        vectorstore = Chroma.from_documents(
            documents=splits, 
            embedding=embeddings
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

        # Промпт для переформулировки вопроса
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", "Если в истории чата есть релевантный контекст, используйте его для переформулировки текущего вопроса."),
            MessagesPlaceholder("chat_history"),
            ("user", "{input}")
        ])

        # Создание retriever с учетом истории
        history_aware_retriever = create_history_aware_retriever(
            llm, 
            retriever, 
            contextualize_q_prompt
        )

        # Промпт для объединения документов
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", "Используйте следующие документы для ответа на вопрос:\n\n{context}"),
            MessagesPlaceholder("chat_history"),
            ("user", "{input}")
        ])

        # Создание цепочки для объединения документов
        document_chain = create_stuff_documents_chain(llm, qa_prompt)

        # Финальная retrieval chain
        retrieval_chain = create_retrieval_chain(
            history_aware_retriever, 
            document_chain
        )

        # История чата (можно хранить в БД)
        chat_history = []

        # Выполнение запроса
        result = retrieval_chain.invoke({
            "input": query,
            "chat_history": chat_history
        })

        return JSONResponse({
            "result": result["answer"],
            "sources": [doc.page_content for doc in result.get("context", [])]
        })

    except Exception as e:
        print(f"❌ Ошибка: {e}") 
        return JSONResponse({"error": str(e)}, status_code=500)
