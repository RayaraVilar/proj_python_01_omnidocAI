import os

os.environ["MOCK_AI"] = "true"
os.environ["API_ACCESS_KEY"] = "test-secret-key"
os.environ["OPENAI_MODEL"] = "gpt-5.4-nano"
os.environ["OPENAI_API_KEY"] = ""

from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Bem-vindo ao OmniDoc AI"
    assert "supported_formats" in data
    assert "TXT" in data["supported_formats"]


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"


def test_analyze_without_api_key_should_return_401():
    files = {
        "file": (
            "contrato.txt",
            b"Contrato de teste para analise automatizada.",
            "text/plain"
        )
    }

    response = client.post("/analyze", files=files)

    assert response.status_code == 401


def test_analyze_with_api_key_should_return_200():
    files = {
        "file": (
            "contrato.txt",
            b"Contrato de prestacao de servicos com prazo de 12 meses.",
            "text/plain"
        )
    }

    headers = {
        "X-API-Key": "test-secret-key"
    }

    response = client.post("/analyze", files=files, headers=headers)

    assert response.status_code == 200

    data = response.json()

    assert data["total_documents"] == 1
    assert data["documents"][0]["filename"] == "contrato.txt"
    assert data["documents"][0]["characters"] > 0
    assert "summary" in data["documents"][0]
    assert "key_points" in data["documents"][0]
    assert "risks" in data["documents"][0]
    assert "suggested_actions" in data["documents"][0]


def test_analyze_batch_with_api_key_should_return_200():
    files = {
        "file_1": (
            "contrato_1.txt",
            b"Primeiro contrato para teste automatizado.",
            "text/plain"
        ),
        "file_2": (
            "contrato_2.txt",
            b"Segundo contrato para teste automatizado.",
            "text/plain"
        )
    }

    headers = {
        "X-API-Key": "test-secret-key"
    }

    response = client.post("/analyze-batch", files=files, headers=headers)

    assert response.status_code == 200

    data = response.json()

    assert data["total_documents"] == 2
    assert len(data["documents"]) == 2


def test_unsupported_file_format_should_return_400():
    files = {
        "file": (
            "imagem.png",
            b"conteudo falso de imagem",
            "image/png"
        )
    }

    headers = {
        "X-API-Key": "test-secret-key"
    }

    response = client.post("/analyze", files=files, headers=headers)

    assert response.status_code == 400