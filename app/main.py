import time
from typing import Annotated

from fastapi import FastAPI, File, UploadFile
from dotenv import load_dotenv

from app.schemas import BatchAnalysisResponse
from app.services.document_reader import DocumentReader
from app.services.ai_analyzer import AIAnalyzer


load_dotenv()

app = FastAPI(
    title="OmniDoc AI",
    description="API assíncrona para análise de documentos com Inteligência Artificial.",
    version="0.1.0"
)

document_reader = DocumentReader()
ai_analyzer = AIAnalyzer()


@app.get(
    "/health",
    summary="Verificar status da API",
    tags=["Sistema"]
)
async def health_check():
    return {"status": "ok", "message": "OmniDoc AI está rodando."}


@app.post(
    "/analyze",
    response_model=BatchAnalysisResponse,
    summary="Analisar documento",
    description="Recebe um documento TXT, PDF ou DOCX e retorna uma análise automatizada.",
    tags=["Documentos"]
)
async def analyze_document(
    file: Annotated[UploadFile, File(description="Arquivo TXT, PDF ou DOCX")]
):
    start_time = time.perf_counter()

    filename, text = await document_reader.extract_text(file)
    analysis = await ai_analyzer.analyze(filename, text)

    processing_time = round(time.perf_counter() - start_time, 2)

    return BatchAnalysisResponse(
        total_documents=1,
        processing_time_seconds=processing_time,
        documents=[analysis]
    )