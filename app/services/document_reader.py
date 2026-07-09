import io
from fastapi import UploadFile, HTTPException
from pypdf import PdfReader
from docx import Document


class DocumentReader:
    async def extract_text(self, file: UploadFile) -> tuple[str, str]:
        content = await file.read()

        if not content:
            raise HTTPException(status_code=400, detail=f"O arquivo {file.filename} está vazio.")

        filename = file.filename or "documento_sem_nome"
        extension = filename.lower().split(".")[-1]

        if extension == "txt":
            text = content.decode("utf-8", errors="ignore")

        elif extension == "pdf":
            text = self._extract_pdf_text(content)

        elif extension == "docx":
            text = self._extract_docx_text(content)

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Formato não suportado: {extension}. Use TXT, PDF ou DOCX."
            )

        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail=f"Não foi possível extrair texto do arquivo {filename}."
            )

        return filename, text

    def _extract_pdf_text(self, content: bytes) -> str:
        reader = PdfReader(io.BytesIO(content))
        pages = []

        for page in reader.pages:
            pages.append(page.extract_text() or "")

        return "\n".join(pages)

    def _extract_docx_text(self, content: bytes) -> str:
        document = Document(io.BytesIO(content))
        paragraphs = [paragraph.text for paragraph in document.paragraphs]
        return "\n".join(paragraphs)