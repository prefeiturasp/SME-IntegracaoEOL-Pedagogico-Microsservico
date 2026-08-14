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
    def test_lista_disciplinas_por_turma(self, mock_service) -> None:
        """Repassa a turma e os códigos das disciplinas ao serviço."""
        metodo = mock_service.return_value.listar_disciplinas_por_turma
        metodo.return_value = [
            {
                "turma_codigo": "3022108",
                "desc_territorio_saber": "Território",
                "desc_experiencia_pedagogica": "Experiência",
                "componente_codigo": 1214,
                "codigo_componente_territorio_saber": 1519,
            }
        ]

        response = self.get(
            "/turmas/3022108/componentes-turma/"
            "?codigos_componentes=1214&codigos_componentes=1215"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, metodo.return_value)
        metodo.assert_called_once_with("3022108", [1214, 1215])

    def test_lista_disciplinas_por_turma_exige_codigos(self) -> None:
        """Rejeita a consulta sem códigos de disciplinas."""
        response = self.get("/turmas/3022108/componentes-turma/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lista_disciplinas_por_turma_rejeita_codigo_invalido(self) -> None:
        """Rejeita um código de disciplina não numérico."""
        response = self.get(
            "/turmas/3022108/componentes-turma/"
            "?codigos_componentes=invalido"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lista_disciplinas_por_turma_exige_api_key(self) -> None:
        """Rejeita a consulta sem API Key."""
        self.assert_unauthorized(
            "/turmas/3022108/componentes-turma/?codigos_componentes=1214"
        )

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
    def test_lista_atribuicoes_territorio_por_professor_ano(
        self,
        mock_service,
    ) -> None:
        """Retorna atribuições e repassa RF e ano ao serviço."""
        metodo = (
            mock_service.return_value.listar_atribuicoes_territorio_por_professor_ano
        )
        metodo.return_value = [{"codigo_rf": "RF1", "ano_letivo": 2024}]

        response = self.get(
            "/professores/RF1/anos-letivos/2024/"
            "atribuicoes-territorio-saber/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [{"codigo_rf": "RF1", "ano_letivo": 2024}],
        )
        metodo.assert_called_once_with("RF1", 2024)

    def test_atribuicoes_territorio_exige_api_key(self) -> None:
        """Rejeita a listagem de atribuições sem API Key."""
        self.assert_unauthorized(
            "/professores/RF1/anos-letivos/2024/"
            "atribuicoes-territorio-saber/"
        )

    @patch(_SVC)
    def test_lista_atribuicoes_territorio_sem_filtro_de_ano(
        self,
        mock_service,
    ) -> None:
        """Lista atribuições repassando somente o RF ao serviço."""
        metodo = (
            mock_service.return_value.listar_atribuicoes_territorio_por_professor
        )
        metodo.return_value = [
            {"codigo_rf": "RF1", "ano_letivo": 2023},
            {"codigo_rf": "RF1", "ano_letivo": 2024},
        ]

        response = self.get("/professores/RF1/atribuicoes-territorio-saber/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        metodo.assert_called_once_with("RF1")

    def test_atribuicoes_territorio_sem_ano_exige_api_key(self) -> None:
        """Rejeita a listagem sem ano quando não há API Key."""
        self.assert_unauthorized(
            "/professores/RF1/atribuicoes-territorio-saber/"
        )

    @patch(_SVC)
    def test_lista_atribuicoes_territorio_por_turma(
        self,
        mock_service,
    ) -> None:
        """Lista atribuições repassando somente o código da turma."""
        metodo = (
            mock_service.return_value.listar_atribuicoes_territorio_por_turma
        )
        metodo.return_value = [
            {
                "cod_agrupamento": 9001,
                "codigo_turma": "T1",
                "ano_letivo": 2024,
            }
        ]

        response = self.get("/turmas/T1/atribuicoes-territorio-saber/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [
                {
                    "cod_agrupamento": 9001,
                    "codigo_turma": "T1",
                    "ano_letivo": 2024,
                }
            ],
        )
        metodo.assert_called_once_with("T1")

    def test_atribuicoes_territorio_por_turma_exige_api_key(self) -> None:
        """Rejeita a listagem por turma quando não há API Key."""
        self.assert_unauthorized("/turmas/T1/atribuicoes-territorio-saber/")

    @patch(_SVC)
    def test_lista_atribuicoes_territorio_por_turmas(
        self,
        mock_service,
    ) -> None:
        """Lista atribuições repassando os códigos das turmas."""
        metodo = (
            mock_service.return_value.listar_atribuicoes_territorio_por_turmas
        )
        metodo.return_value = [
            {"codigo_turma": "T1", "ano_letivo": 2024},
            {"codigo_turma": "T2", "ano_letivo": 2024},
        ]

        response = self.get(
            "/turmas/atribuicoes-territorio-saber/"
            "?codigo_turma=T1&codigo_turma=T2"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        metodo.assert_called_once_with(["T1", "T2"])

    @patch(_SVC)
    def test_atribuicoes_territorio_por_turmas_exige_codigo(
        self,
        mock_service,
    ) -> None:
        """Rejeita consulta sem código de turma."""
        response = self.get("/turmas/atribuicoes-territorio-saber/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_service.assert_not_called()

    def test_atribuicoes_territorio_por_turmas_exige_api_key(self) -> None:
        """Rejeita a listagem em lote quando não há API Key."""
        self.assert_unauthorized(
            "/turmas/atribuicoes-territorio-saber/",
        )

    @patch(_SVC)
    def test_lista_componentes_api_eol(self, mock_service):
        """Lista componentes curriculares da API EOL."""
        dados = [
            {
                "id_relacao_origem": None,
                "id_componente_curricular": 1,
                "eh_regencia": True,
                "eh_territorio": False,
                "descricao": "Regência",
                "id_componente_curricular_pai": None,
                "vigencia": None,
            }
        ]
        service = mock_service.return_value
        service.listar_componentes_api_eol.return_value = dados

        response = self.get("/api-eol/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, dados)
        service.listar_componentes_api_eol.assert_called_once_with()

    def test_componentes_api_eol_sem_api_key(self):
        """Rejeita consulta da API EOL sem autenticação."""
        self.assert_unauthorized("/api-eol/")

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

    @patch(_SVC)
    def test_valida_atribuicao_territorio_saber(
        self,
        mock_service,
    ) -> None:
        """Retorna a validação e repassa os parâmetros ao serviço."""
        metodo = (
            mock_service.return_value.validar_atribuicao_territorio_saber_professor
        )
        metodo.return_value = True

        response = self.get(
            "/1214/turmas/T1/professor/RF1/data/2024-06-01"
            "/atribuicao/validar/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIs(response.data, True)
        metodo.assert_called_once_with(
            1214,
            "T1",
            "RF1",
            "2024-06-01",
        )

    @patch(_SVC)
    def test_valida_atribuicao_rejeita_data_inexistente(
        self,
        mock_service,
    ) -> None:
        """Rejeita data inexistente sem consultar o serviço."""
        response = self.get(
            "/1214/turmas/T1/professor/RF1/data/2024-02-30"
            "/atribuicao/validar/"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, "Deve ser informada uma data valida.")
        metodo = (
            mock_service.return_value.validar_atribuicao_territorio_saber_professor
        )
        metodo.assert_not_called()

    @patch(_SVC)
    def test_valida_atribuicao_rejeita_formato_de_data(
        self,
        mock_service,
    ) -> None:
        """Rejeita data fora do formato ISO sem consultar o serviço."""
        response = self.get(
            "/1214/turmas/T1/professor/RF1/data/01-06-2024"
            "/atribuicao/validar/"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        metodo = (
            mock_service.return_value.validar_atribuicao_territorio_saber_professor
        )
        metodo.assert_not_called()

    def test_valida_atribuicao_exige_api_key(self) -> None:
        """Rejeita validação sem API Key."""
        self.assert_unauthorized(
            "/1214/turmas/T1/professor/RF1/data/2024-06-01"
            "/atribuicao/validar/"
        )


class TestListagemTurmasComponentesView(TestCase):
    """Valida a view de listagem turma×componente."""

    def setUp(self):
        """Configura clientes de teste."""
        self.client = APIClient()
        self.client.credentials(HTTP_X_API_KEY="dev-key-default")
        self.anon = APIClient()
        self.path = "/ues/9000/modalidades/5/anos/2024/componentes/"

    @patch(_SVC)
    def test_lista_com_paginacao(self, mock_service):
        """Retorna o envelope paginado do service."""
        service = mock_service.return_value
        envelope = {"items": [], "total_registros": 0, "total_paginas": 0}
        metodo = service.listar_turmas_componentes_por_ue_modalidade_ano
        metodo.return_value = envelope

        response = self.client.get(f"{_BASE}{self.path}?qtdeRegistros=10")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), envelope)

    @patch(_SVC)
    def test_traduz_parametros_professor(self, mock_service):
        """Repassa eh_professor/codigo_rf e demais filtros ao service."""
        service = mock_service.return_value
        metodo = service.listar_turmas_componentes_por_ue_modalidade_ano
        metodo.return_value = {
            "items": [],
            "total_registros": 0,
            "total_paginas": 0,
        }

        self.client.get(
            f"{_BASE}{self.path}"
            "?ehProfessor=true&codigoRf=RF1&codigoTurma=77"
            "&qtdeRegistros=10&consideraHistorico=false"
        )

        _, kwargs = metodo.call_args
        self.assertTrue(kwargs["eh_professor"])
        self.assertEqual(kwargs["codigo_rf"], "RF1")
        self.assertEqual(kwargs["codigo_turma"], 77)
        self.assertEqual(kwargs["qtde_registros"], 10)

    @patch(_SVC)
    def test_gestor_nao_repassa_rf(self, mock_service):
        """Sem eh_professor, o RF não é repassado ao service."""
        service = mock_service.return_value
        metodo = service.listar_turmas_componentes_por_ue_modalidade_ano
        metodo.return_value = {
            "items": [],
            "total_registros": 0,
            "total_paginas": 0,
        }

        self.client.get(f"{_BASE}{self.path}?codigoRf=RF1")

        _, kwargs = metodo.call_args
        self.assertFalse(kwargs["eh_professor"])
        self.assertIsNone(kwargs["codigo_rf"])

    def test_exige_api_key(self):
        """Rejeita requisição sem API Key."""
        response = self.anon.get(f"{_BASE}{self.path}")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
