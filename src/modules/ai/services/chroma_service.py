import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

DB_PATH = "chroma_db"

# Загружаем модель эмбеддингов
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

class ChromaService:
    def get_vectorstore():
        # Если база уже есть — просто загружаем
        if os.path.exists(DB_PATH):
            return Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
        
        # Иначе загружаем документы, создаём базу и сохраняем
        file_path = os.path.abspath("data.txt")
        loader = TextLoader(file_path, encoding="utf-8")
        documents = loader.load()
    
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)
    
        vectorstore = Chroma.from_documents(splits, embedding=embeddings, persist_directory=DB_PATH)
        vectorstore.persist()  # Сохранение базы
    
        return vectorstore
