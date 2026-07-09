from pydantic import BaseModel
from typing import List


class DocumentInsight(BaseModel):
    filename: str
    characters: int
    summary: str
    key_points: List[str]
    risks: List[str]
    suggested_actions: List[str]


class BatchAnalysisResponse(BaseModel):
    total_documents: int
    processing_time_seconds: float
    documents: List[DocumentInsight]