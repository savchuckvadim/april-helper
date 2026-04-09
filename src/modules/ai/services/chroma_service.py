import os
# from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.modules.ai.utils.file_loader import FileLoader
from langchain.schema import Document
from pathlib import Path


class ChromaService:
    @staticmethod
    def _sanitize_key_part(value: str) -> str:
        return "".join(ch if ch.isalnum() or ch in ("-", "_", ".") else "_" for ch in value)

    @staticmethod
    def _build_db_path(embedding_id: str, domain: str | None, kind: str | None, content_hash: str | None) -> str:
        key = ChromaService._sanitize_key_part(embedding_id)
        if domain:
            key += f"__{ChromaService._sanitize_key_part(domain)}"
        if kind:
            key += f"__{ChromaService._sanitize_key_part(kind)}"
        if content_hash:
            key += f"__{ChromaService._sanitize_key_part(content_hash[:16])}"
        return f"chroma_db/{key}"

    @staticmethod
    def get_vectorstore(
        embeddings,
        embedding_id: str,
        retrive_root: str | Path | None = None,
        retrive_paths: list[str] | None = None,
        domain: str | None = None,
        kind: str | None = None,
        content_hash: str | None = None,
    ):
        # Генерируем путь для хранения конкретной модели/домена/вида промпта
        db_path = ChromaService._build_db_path(embedding_id, domain=domain, kind=kind, content_hash=content_hash)

        # Если база уже есть — просто загружаем
        if os.path.exists(db_path):
            return Chroma(persist_directory=db_path, embedding_function=embeddings)
        
        # Иначе загружаем документы, создаём базу и сохраняем
    

        print("📄 Чтение файлов для построения индекса...")
        folder = os.path.abspath(str(retrive_root or "retrive_data"))


        documents = []  
        # text = extract_text_from_pdf(file_path)
        allowed_paths = [p.strip().strip("/").replace("\\", "/") for p in (retrive_paths or []) if p.strip()]
        allowed_paths_set = set(allowed_paths)

        for root, _, files in os.walk(folder):
            for filename in files:
                path = os.path.join(root, filename)
                try:
                    content = FileLoader.extract_text(path)
                    rel_source = os.path.relpath(path, folder).replace("\\", "/")
                    if allowed_paths_set and not any(
                        rel_source == allowed or rel_source.startswith(f"{allowed}/")
                        for allowed in allowed_paths_set
                    ):
                        continue
                    print(f"✅ Загрузили: {rel_source}")
                    documents.append(Document(page_content=content, metadata={"source": rel_source}))
                except Exception as e:
                    print(f"⚠️ Пропущен {filename}: {e}")

        if not documents:
            raise ValueError(f"No retrive documents found in {folder}")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=250, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)

    
        vectorstore = Chroma.from_documents(splits, embedding=embeddings, persist_directory=db_path)
        # vectorstore.persist()  # Сохранение базы
    
        return vectorstore
