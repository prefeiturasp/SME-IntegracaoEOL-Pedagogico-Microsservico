"""Testes das views de abrangência."""

from datetime import datetime

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.abrangencia.models import CicloEnsino


class CiclosEnsinoViewTest(TestCase):
    """Valida o contrato de listagem dos ciclos de ensino."""

    _URL = "/api/v1/pedagogico/abrangencia/ciclo-ensino/"

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.credentials(HTTP_X_API_KEY="dev-key-default")

    def test_retorna_contrato_legado(self) -> None:
        """Retorna todos os campos com a nomenclatura legada."""
        CicloEnsino.objects.create(
            codigo_modalidade_ensino=5,
            codigo_etapa_ensino=4,
            codigo=3,
            descricao="Alfabetização",
            data_atualizacao=timezone.make_aware(
                datetime(2026, 8, 20, 10, 30, 15, 123000)
            ),
        )

        response = self.client.get(self._URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [
                {
                    "codigoModalidadeEnsino": 5,
                    "codigoEtapaEnsino": 4,
                    "codigo": 3,
                    "descricao": "Alfabetização",
                    "dtAtualizacao": "2026-08-20T10:30:15.123",
                }
            ],
        )

    def test_sem_ciclos_retorna_lista_vazia(self) -> None:
        """Mantém a resposta vazia observada no legado."""
        response = self.client.get(self._URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_sem_api_key_retorna_401(self) -> None:
        """Exige a API key configurada pelo microsserviço."""
        response = APIClient().get(self._URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_schema_expoe_tag_abrangencia(self) -> None:
        """Publica o endpoint na tag Abrangencia do Swagger."""
        response = self.client.get(
            "/pedagogico/api/v1/schema/",
            HTTP_ACCEPT="application/json",
        )

        operacao = response.data["paths"][self._URL]["get"]
        self.assertEqual(operacao["tags"], ["Abrangencia"])
