import os
import fitz
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.modules.ai.utils import FileLoader

class ChromaService:
    @staticmethod
    def get_vectorstore(embeddings, embedding_id: str):
        # Генерируем путь для хранения конкретной модели
        db_path = f"chroma_db/{embedding_id}"

        # Если база уже есть — просто загружаем
        if os.path.exists(db_path):
            return Chroma(persist_directory=db_path, embedding_function=embeddings)
        
        # Иначе загружаем документы, создаём базу и сохраняем
    

        print("📄 Чтение файлов для построения индекса...")
        all_text = ""
        folder = os.path.abspath("retrive_data")

        # text = extract_text_from_pdf(file_path)
        for filename in os.listdir(folder):
            path = os.path.join(folder, filename)
            try:
                content = FileLoader.extract_text(path)
                all_text += content + "\n"
                print(f"✅ Загрузили: {filename}")
            except Exception as e:
                print(f"⚠️ Пропущен {filename}: {e}")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents([all_text])
    
        vectorstore = Chroma.from_documents(splits, embedding=embeddings, persist_directory=DB_PATH)
        vectorstore.persist()  # Сохранение базы
    
        return vectorstore
