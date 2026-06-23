"""Testes das views do domínio Componentes Curriculares."""

from datetime import date
from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

_SVC = "apps.componentes_curriculares.api.views.ComponentesService"
_BASE = "/api/v1/pedagogico/componentes-curriculares"


class TestComponentesViews(TestCase):
    """Valida views de componentes curriculares."""

    def setUp(self):
        """Configura clientes de teste."""
        self.client = APIClient()
        self.client.credentials(HTTP_X_API_KEY="dev-key-default")
        self.anon = APIClient()

    def get(self, path):
        """Executa consulta autenticada."""
        return self.client.get(f"{_BASE}{path}")

    def post(self, path, payload):
        """Envia payload autenticado."""
        return self.client.post(f"{_BASE}{path}", payload, format="json")

    def assert_unauthorized(self, path, method="get", payload=None):
        """Valida rejeição de requisição sem API Key."""
        response = getattr(self.anon, method)(
            f"{_BASE}{path}",
            payload,
            format="json" if payload else None,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch(_SVC)
    def test_ep1_lista_componentes(self, mock_service):
        """Lista componentes do funcionário."""
        service = mock_service.return_value
        service.listar_componentes_por_funcionario.return_value = []

        response = self.get("/funcionarios/f1/?idPerfil=p1&codigoTurma=T1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        service.listar_componentes_por_funcionario.assert_called_once_with(
            "f1",
            codigo_turma="T1",
            planejamento=False,
            agrupamento=False,
        )

    def test_ep1_sem_api_key(self):
        """Valida rejeição de requisição sem API Key."""
        self.assert_unauthorized("/funcionarios/f1/?idPerfil=p1")

    @patch(_SVC)
    def test_ep14_corpo_invalido(self, _mock_service):
        """Valida corpo inválido para agrupamentos correlacionados."""
        response = self.post(
            "/territorio-saber/agrupamentos-correlacionados/",
            {"not": "list"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            response.data,
            {"detail": "O corpo deve ser uma lista de inteiros."},
        )

    def test_endpoints_sem_api_key(self):
        """Valida proteção das views autenticadas."""
        casos = [
            "/",
            "/turmas/",
            "/turmas/brutos/",
            "/grade-curricular/2024/",
        ]

        for path in casos:
            response = self.anon.get(f"{_BASE}{path}")

            self.assertEqual(
                response.status_code,
                status.HTTP_401_UNAUTHORIZED,
            )

    @patch(_SVC)
    def test_endpoints_get_sucesso(self, mock_service):
        """Valida respostas de sucesso das consultas."""
        casos = [
            (
                "/anos/2024/regencia/",
                "listar_regencia_por_ano_turma",
            ),
            (
                "/grade-curricular/2024/",
                "listar_grade_curricular",
            ),
        ]

        for path, metodo in casos:
            getattr(
                mock_service.return_value,
                metodo,
            ).return_value = []

            response = self.get(path)

            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
            )

    @patch(_SVC)
    def test_componentes_sem_atribuicao_repassa_data_base(
        self,
        mock_service,
    ):
        """Converte a data-base ISO antes de chamar o serviço."""
        service = mock_service.return_value
        service.listar_componentes_sem_atribuicao.return_value = [
            "512",
            "513",
        ]

        response = self.get("/turmas/T1/sem-atribuicao/?data_base=2024-06-01")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, ["512", "513"])
        service.listar_componentes_sem_atribuicao.assert_called_once_with(
            "T1",
            date(2024, 6, 1),
        )

    @patch(_SVC)
    def test_grade_curricular_retorna_resposta_snake_case(
        self,
        mock_service,
    ):
        """Valida chaves da resposta de grade curricular."""
        mock_service.return_value.listar_grade_curricular.return_value = [
            {
                "codigo_componente_curricular": 1,
                "descricao_componente_curricular": "C1",
                "codigo_ano_turma": "1",
                "descricao_serie_ensino": "1 ano",
                "codigo_serie_ensino": 1,
                "modalidade": 5,
            }
        ]

        response = self.get("/grade-curricular/2024/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [
                {
                    "codigo_componente_curricular": 1,
                    "descricao_componente_curricular": "C1",
                    "codigo_ano_turma": "1",
                    "descricao_serie_ensino": "1 ano",
                    "codigo_serie_ensino": 1,
                    "modalidade": 5,
                }
            ],
        )

    @patch(_SVC)
    def test_ue_turmas_repassa_ue_id_para_service(self, mock_service):
        """Valida repasse da UE para o service."""
        mock_service.return_value.listar_por_ue_e_turmas.return_value = []

        response = self.get("/ues/100013/turmas/?turmas=T1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_service.return_value.listar_por_ue_e_turmas.assert_called_once_with(
            "100013",
            ["T1"],
        )
