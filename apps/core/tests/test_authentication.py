"""Testes de autenticação por API Key."""

from django.test import TestCase
from rest_framework.test import APIClient

_URL = "/api/v1/componentes-curriculares/"


class TestApiKeyAuthentication(TestCase):
    """Valida o comportamento da autenticação por API Key."""

    def test_sem_api_key_retorna_401_e_header_correto(self) -> None:
        """Sem header retorna 401 com WWW-Authenticate configurado."""
        client = APIClient()
        resposta = client.get(_URL)
        self.assertEqual(resposta.status_code, 401)
        self.assertEqual(
            resposta.get("WWW-Authenticate", "").lower(), "x-api-key"
        )

    def test_api_key_invalida_retorna_401(self) -> None:
        """Requisição com API Key incorreta retorna 401."""
        client = APIClient()
        client.credentials(HTTP_X_API_KEY="chave-errada")
        resposta = client.get(_URL)
        self.assertEqual(resposta.status_code, 401)

    def test_api_key_valida_permite_acesso(self) -> None:
        """Requisição com API Key válida permite o acesso."""
        client = APIClient()

        client.credentials(HTTP_X_API_KEY="dev-key-default")
        resposta = client.get(_URL)
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(str(resposta.wsgi_request.user), "api-user")
