import json
import os
from openai import AsyncOpenAI
from app.schemas import DocumentInsight


class AIAnalyzer:
    def __init__(self):
        self.mock_ai = os.getenv("MOCK_AI", "true").lower() == "true"
        self.model = os.getenv("OPENAI_MODEL", "")
        api_key = os.getenv("OPENAI_API_KEY")

        self.client = None

        if api_key and not self.mock_ai:
            self.client = AsyncOpenAI(api_key=api_key)

    async def analyze(self, filename: str, text: str) -> DocumentInsight:
        if self.mock_ai or self.client is None:
            return self._mock_analysis(filename, text)

        prompt = f"""
Analise o documento abaixo e retorne apenas um JSON válido.

O JSON deve seguir este formato:
{{
  "summary": "resumo curto do documento",
  "key_points": ["ponto 1", "ponto 2", "ponto 3"],
  "risks": ["risco 1", "risco 2"],
  "suggested_actions": ["ação 1", "ação 2"]
}}

Arquivo: {filename}

Texto do documento:
{text[:12000]}
"""

        response = await self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        raw_response = response.output_text

        try:
            data = json.loads(raw_response)
        except json.JSONDecodeError:
            data = {
                "summary": raw_response[:500],
                "key_points": [],
                "risks": [],
                "suggested_actions": []
            }

        return DocumentInsight(
            filename=filename,
            characters=len(text),
            summary=data.get("summary", ""),
            key_points=data.get("key_points", []),
            risks=data.get("risks", []),
            suggested_actions=data.get("suggested_actions", [])
        )

    def _mock_analysis(self, filename: str, text: str) -> DocumentInsight:
        preview = text[:250].replace("\n", " ")

        return DocumentInsight(
            filename=filename,
            characters=len(text),
            summary=f"Resumo simulado do documento. Início do conteúdo: {preview}...",
            key_points=[
                "Documento recebido e processado com sucesso.",
                "Texto extraído automaticamente.",
                "Análise simulada para ambiente de desenvolvimento."
            ],
            risks=[
                "A análise real com IA ainda está desativada.",
                "É necessário configurar a chave da OpenAI para resultados reais."
            ],
            suggested_actions=[
                "Ativar MOCK_AI=false no arquivo .env.",
                "Configurar OPENAI_API_KEY.",
                "Testar com documentos reais."
            ]
        )