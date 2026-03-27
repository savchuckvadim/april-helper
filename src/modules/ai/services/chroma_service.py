import os
# from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.modules.ai.utils.file_loader import FileLoader
from langchain.schema import Document


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


        documents = []  
        # text = extract_text_from_pdf(file_path)
        for filename in os.listdir(folder):
            path = os.path.join(folder, filename)
            try:
                content = FileLoader.extract_text(path)
                all_text += content + "\n"
                print(f"✅ Загрузили: {filename}")
                documents.append(Document(page_content=content, metadata={"source": filename}))

            except Exception as e:
                print(f"⚠️ Пропущен {filename}: {e}")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=250, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)

    
        vectorstore = Chroma.from_documents(splits, embedding=embeddings, persist_directory=db_path)
        # vectorstore.persist()  # Сохранение базы
    
        return vectorstore
