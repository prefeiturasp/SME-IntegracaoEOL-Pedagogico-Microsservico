"""Testes de autenticação por API Key."""
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def url() -> str:
    """URL do endpoint de catálogo para uso nos testes de autenticação."""
    return "/api/v1/componentes-curriculares/"


def test_sem_api_key_retorna_401(url: str) -> None:
    """Requisição sem header retorna 401 — authenticate_header() faz DRF emitir WWW-Authenticate."""
    client = APIClient()
    resposta = client.get(url)
    assert resposta.status_code == 401


def test_api_key_invalida_retorna_401(url: str) -> None:
    """Requisição com API Key incorreta deve retornar 401."""
    client = APIClient()
    client.credentials(HTTP_X_API_KEY="chave-errada")
    resposta = client.get(url)
    assert resposta.status_code == 401


@pytest.mark.django_db(databases=["default", "pedagogico"])
def test_api_key_valida_permite_acesso(api_client: APIClient, url: str) -> None:
    """Requisição com API Key válida deve retornar 200."""
    resposta = api_client.get(url)
    assert resposta.status_code == 200
