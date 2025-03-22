from docx import Document
import fitz

class FileLoader:
    @staticmethod
    def extract_text(path: str) -> str:
        if path.endswith(".pdf"):
            return FileLoader._extract_pdf(path)
        elif path.endswith(".txt"):
            return FileLoader._extract_txt(path)
        elif path.endswith(".docx"):
            return FileLoader._extract_docx(path)
        else:
            raise ValueError(f"❌ Неподдерживаемый тип файла: {path}")

    @staticmethod
    def _extract_pdf(path: str) -> str:
        text = ""
        with fitz.open(path) as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
        return text

    @staticmethod
    def _extract_txt(path: str) -> str:
        with open(path, encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def _extract_docx(path: str) -> str:
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
