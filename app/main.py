import asyncio
import time
from typing import Annotated

from fastapi import FastAPI, File, UploadFile, HTTPException, Security
from dotenv import load_dotenv

from app.schemas import BatchAnalysisResponse
from app.services.document_reader import DocumentReader
from app.services.ai_analyzer import AIAnalyzer
from app.security import get_api_key


load_dotenv()

app = FastAPI(
    title="OmniDoc AI",
    description="API assíncrona para análise de documentos com Inteligência Artificial.",
    version="0.2.0"
)

document_reader = DocumentReader()
ai_analyzer = AIAnalyzer()


@app.get(
    "/",
    summary="Página inicial da API",
    tags=["Sistema"]
)
async def home():
    return {
        "message": "Bem-vindo ao OmniDoc AI",
        "description": "API para análise automatizada de documentos com Inteligência Artificial.",
        "docs": "Acesse /docs para testar os endpoints.",
        "supported_formats": ["TXT", "PDF", "DOCX"]
    }


@app.get(
    "/health",
    summary="Verificar status da API",
    tags=["Sistema"]
)
async def health_check():
    return {
        "status": "ok",
        "message": "OmniDoc AI está rodando."
    }


async def process_document(file: UploadFile):
    filename, text = await document_reader.extract_text(file)
    analysis = await ai_analyzer.analyze(filename, text)
    return analysis


@app.post(
    "/analyze",
    response_model=BatchAnalysisResponse,
    summary="Analisar um documento",
    description="Recebe um documento TXT, PDF ou DOCX e retorna uma análise automatizada.",
    tags=["Documentos"]
)
async def analyze_document(
    file: Annotated[UploadFile, File(description="Arquivo TXT, PDF ou DOCX")],
    api_key: str = Security(get_api_key)
):
    start_time = time.perf_counter()

    analysis = await process_document(file)

    processing_time = round(time.perf_counter() - start_time, 2)

    return BatchAnalysisResponse(
        total_documents=1,
        processing_time_seconds=processing_time,
        documents=[analysis]
    )


@app.post(
    "/analyze-batch",
    response_model=BatchAnalysisResponse,
    summary="Analisar múltiplos documentos",
    description="Recebe até 5 documentos TXT, PDF ou DOCX e processa todos de forma assíncrona.",
    tags=["Documentos"]
)
async def analyze_multiple_documents(
    file_1: UploadFile = File(..., description="Primeiro documento"),
    file_2: UploadFile | None = File(None, description="Segundo documento"),
    file_3: UploadFile | None = File(None, description="Terceiro documento"),
    file_4: UploadFile | None = File(None, description="Quarto documento"),
    file_5: UploadFile | None = File(None, description="Quinto documento"),
    api_key: str = Security(get_api_key)
):
    files = [file for file in [file_1, file_2, file_3, file_4, file_5] if file is not None]

    start_time = time.perf_counter()

    results = await asyncio.gather(
        *(process_document(file) for file in files)
    )

    processing_time = round(time.perf_counter() - start_time, 2)

    return BatchAnalysisResponse(
        total_documents=len(results),
        processing_time_seconds=processing_time,
        documents=results
    )