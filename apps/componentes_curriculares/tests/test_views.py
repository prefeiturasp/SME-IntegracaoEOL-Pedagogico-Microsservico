"""Testes de views do domínio Componentes Curriculares (EP-1 a EP-15)."""
from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

_SVC = "apps.componentes_curriculares.api.views.ComponentesService"
_BASE = "/api/v1/pedagogico/componentes-curriculares"


class TestComponentesViews(TestCase):
    """Testes dos endpoints EP-1 a EP-15 de Componentes Curriculares."""

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.credentials(HTTP_X_API_KEY="dev-key-default")

    # ---- EP-1 ----

    def test_ep1_sem_turma_retorna_200(self) -> None:
        """EP-1 sem codigoTurma retorna 200."""
        with patch(_SVC) as mock:
            mock.return_value.listar_componentes_por_funcionario.return_value = []
            res = self.client.get(f"{_BASE}/funcionarios/f1/?idPerfil=p1")
        self.assertEqual(res.status_code, 200)

    def test_ep1_com_turma_retorna_200(self) -> None:
        """EP-1 com codigoTurma retorna 200."""
        with patch(_SVC) as mock:
            mock.return_value.listar_componentes_por_funcionario.return_value = []
            res = self.client.get(
                f"{_BASE}/funcionarios/f1/?idPerfil=p1&codigoTurma=T1"
            )
        self.assertEqual(res.status_code, 200)

    def test_ep1_com_planejamento_true(self) -> None:
        """EP-1 com planejamento=true retorna 200."""
        with patch(_SVC) as mock:
            mock.return_value.listar_componentes_por_funcionario.return_value = []
            res = self.client.get(
                f"{_BASE}/funcionarios/f1/"
                "?idPerfil=p1&codigoTurma=T1&planejamento=true"
            )
        self.assertEqual(res.status_code, 200)

    def test_ep1_sem_api_key_retorna_401(self) -> None:
        """EP-1 sem API Key retorna 401."""
        res = APIClient().get(f"{_BASE}/funcionarios/f1/?idPerfil=p1")
        self.assertEqual(res.status_code, 401)

    # ---- EP-2 ----

    def test_ep2_regencia_retorna_200(self) -> None:
        """EP-2 retorna 200 com componentes de regência."""
        with patch(_SVC) as mock:
            mock.return_value.listar_regencia_por_ano_turma.return_value = []
            res = self.client.get(f"{_BASE}/anos/2024/regencia/")
        self.assertEqual(res.status_code, 200)

    def test_ep2_sem_api_key_retorna_401(self) -> None:
        """EP-2 sem API Key retorna 401."""
        res = APIClient().get(f"{_BASE}/anos/2024/regencia/")
        self.assertEqual(res.status_code, 401)

    # ---- EP-3 ----

    def test_ep3_pap_retorna_200(self) -> None:
        """EP-3 retorna 200 com booleano de validação PAP."""
        with patch(_SVC) as mock:
            mock.return_value.turma_possui_componente_pap.return_value = True
            res = self.client.get(
                f"{_BASE}/turmas/T1/pap/?login=f1&idPerfil=p1"
            )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data)

    def test_ep3_sem_api_key_retorna_401(self) -> None:
        """EP-3 sem API Key retorna 401."""
        res = APIClient().get(f"{_BASE}/turmas/T1/pap/?login=f1&idPerfil=p1")
        self.assertEqual(res.status_code, 401)

    # ---- EP-4 ----

    def test_ep4_ue_anos_escolares_retorna_200(self) -> None:
        """EP-4 retorna 200 com componentes por UE, modalidade e séries."""
        with patch(_SVC) as mock:
            mock.return_value.listar_por_ue_modalidade_ano_e_anos_escolares.return_value = []  # noqa: E501
            res = self.client.get(
                f"{_BASE}/ues/U1/modalidades/1/anos/2024/?anosEscolares=1"
            )
        self.assertEqual(res.status_code, 200)

    def test_ep4_sem_api_key_retorna_401(self) -> None:
        """EP-4 sem API Key retorna 401."""
        res = APIClient().get(
            f"{_BASE}/ues/U1/modalidades/1/anos/2024/?anosEscolares=1"
        )
        self.assertEqual(res.status_code, 401)

    # ---- EP-5 ----

    def test_ep5_turma_programa_retorna_200(self) -> None:
        """EP-5 retorna 200 com componentes de turmas programa."""
        with patch(_SVC) as mock:
            mock.return_value.listar_turma_programa_por_ue_modalidade_ano.return_value = []  # noqa: E501
            res = self.client.get(
                f"{_BASE}/ues/U1/modalidades/1/anos/2024/turmas-programa/"
            )
        self.assertEqual(res.status_code, 200)

    def test_ep5_sem_api_key_retorna_401(self) -> None:
        """EP-5 sem API Key retorna 401."""
        res = APIClient().get(
            f"{_BASE}/ues/U1/modalidades/1/anos/2024/turmas-programa/"
        )
        self.assertEqual(res.status_code, 401)

    # ---- EP-6 ----

    def test_ep6_ue_turmas_retorna_200(self) -> None:
        """EP-6 retorna 200 com componentes simplificados por UE e turmas."""
        with patch(_SVC) as mock:
            mock.return_value.listar_por_ue_e_turmas.return_value = []
            res = self.client.get(f"{_BASE}/ues/U1/turmas/?turmas=T1")
        self.assertEqual(res.status_code, 200)

    def test_ep6_sem_api_key_retorna_401(self) -> None:
        """EP-6 sem API Key retorna 401."""
        res = APIClient().get(f"{_BASE}/ues/U1/turmas/?turmas=T1")
        self.assertEqual(res.status_code, 401)

    # ---- EP-7 ----

    def test_ep7_lista_turmas_retorna_200(self) -> None:
        """EP-7 retorna 200 com componentes de múltiplas turmas."""
        with patch(_SVC) as mock:
            mock.return_value.listar_por_lista_turmas.return_value = []
            res = self.client.get(f"{_BASE}/turmas/?codigoTurmas=T1")
        self.assertEqual(res.status_code, 200)

    def test_ep7_sem_api_key_retorna_401(self) -> None:
        """EP-7 sem API Key retorna 401."""
        res = APIClient().get(f"{_BASE}/turmas/")
        self.assertEqual(res.status_code, 401)

    # ---- EP-8 ----

    def test_ep8_brutos_retorna_200(self) -> None:
        """EP-8 retorna 200 com componentes de turmas sem processamento."""
        with patch(_SVC) as mock:
            mock.return_value.listar_turmas_brutos.return_value = []
            res = self.client.get(
                f"{_BASE}/turmas/brutos/?codigoTurmas=T1"
            )
        self.assertEqual(res.status_code, 200)

    def test_ep8_sem_api_key_retorna_401(self) -> None:
        """EP-8 sem API Key retorna 401."""
        res = APIClient().get(f"{_BASE}/turmas/brutos/")
        self.assertEqual(res.status_code, 401)

    # ---- EP-9 ----

    def test_ep9_catalogo_sucesso(self) -> None:
        """EP-9 retorna 200 com catálogo completo."""
        with patch(_SVC) as mock:
            mock.return_value.listar_catalogo.return_value = [
                {"codigo": 138, "descricao": "LINGUA PORTUGUESA"}
            ]
            res = self.client.get(f"{_BASE}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

    def test_ep9_lista_vazia(self) -> None:
        """EP-9 retorna 200 com lista vazia."""
        with patch(_SVC) as mock:
            mock.return_value.listar_catalogo.return_value = []
            res = self.client.get(f"{_BASE}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, [])

    def test_ep9_sem_api_key_retorna_401(self) -> None:
        """EP-9 sem API Key retorna 401."""
        res = APIClient().get(f"{_BASE}/")
        self.assertEqual(res.status_code, 401)

    # ---- EP-10 ----

    def test_ep10_vigencia_com_semestre(self) -> None:
        """EP-10 retorna 200 com semestre informado."""
        with patch(_SVC) as mock:
            mock.return_value.listar_vigencia_componentes.return_value = []
            res = self.client.get(
                f"{_BASE}/turmas/vigencia/"
                "?ueCodigo=1&anoLetivo=2024"
                "&componentesCurriculares=1&semestre=1"
            )
        self.assertEqual(res.status_code, 200)

    def test_ep10_vigencia_sem_semestre(self) -> None:
        """EP-10 retorna 200 sem semestre."""
        with patch(_SVC) as mock:
            mock.return_value.listar_vigencia_componentes.return_value = []
            res = self.client.get(
                f"{_BASE}/turmas/vigencia/"
                "?ueCodigo=1&anoLetivo=2024&componentesCurriculares=1"
            )
        self.assertEqual(res.status_code, 200)

    def test_ep10_sem_api_key_retorna_401(self) -> None:
        """EP-10 sem API Key retorna 401."""
        res = APIClient().get(f"{_BASE}/turmas/vigencia/")
        self.assertEqual(res.status_code, 401)

    # ---- EP-11 ----

    def test_ep11_grade_curricular_retorna_200(self) -> None:
        """EP-11 retorna 200 com grade curricular."""
        with patch(_SVC) as mock:
            mock.return_value.listar_grade_curricular.return_value = []
            res = self.client.get(f"{_BASE}/grade-curricular/2024/")
        self.assertEqual(res.status_code, 200)

    def test_ep11_sem_api_key_retorna_401(self) -> None:
        """EP-11 sem API Key retorna 401."""
        res = APIClient().get(f"{_BASE}/grade-curricular/2024/")
        self.assertEqual(res.status_code, 401)

    # ---- EP-12 ----

    def test_ep12_sem_atribuicao_retorna_200(self) -> None:
        """EP-12 retorna 200 com componentes sem professor."""
        with patch(_SVC) as mock:
            mock.return_value.listar_componentes_sem_atribuicao.return_value = []  # noqa: E501
            res = self.client.get(
                f"{_BASE}/turmas/T1/sem-atribuicao/?dataBase=2024-03-01"
            )
        self.assertEqual(res.status_code, 200)

    def test_ep12_sem_data_base_retorna_200(self) -> None:
        """EP-12 funciona sem dataBase."""
        with patch(_SVC) as mock:
            mock.return_value.listar_componentes_sem_atribuicao.return_value = []  # noqa: E501
            res = self.client.get(
                f"{_BASE}/turmas/T1/sem-atribuicao/"
            )
        self.assertEqual(res.status_code, 200)

    def test_ep12_sem_api_key_retorna_401(self) -> None:
        """EP-12 sem API Key retorna 401."""
        res = APIClient().get(f"{_BASE}/turmas/T1/sem-atribuicao/")
        self.assertEqual(res.status_code, 401)

    # ---- EP-13 ----

    def test_ep13_correlacionados_sem_data_base(self) -> None:
        """EP-13 retorna 200 sem dataBase."""
        with patch(_SVC) as mock:
            mock.return_value.listar_agrupamentos_correlacionados.return_value = []  # noqa: E501
            res = self.client.get(
                f"{_BASE}/1/territorio-saber/agrupamentos-correlacionados/"
            )
        self.assertEqual(res.status_code, 200)

    def test_ep13_correlacionados_com_data_base(self) -> None:
        """EP-13 retorna 200 com dataBase ISO 8601."""
        with patch(_SVC) as mock:
            mock.return_value.listar_agrupamentos_correlacionados.return_value = []  # noqa: E501
            res = self.client.get(
                f"{_BASE}/1/territorio-saber/agrupamentos-correlacionados/"
                "?dataBase=2024-01-01"
            )
        self.assertEqual(res.status_code, 200)

    def test_ep13_sem_api_key_retorna_401(self) -> None:
        """EP-13 sem API Key retorna 401."""
        res = APIClient().get(
            f"{_BASE}/1/territorio-saber/agrupamentos-correlacionados/"
        )
        self.assertEqual(res.status_code, 401)

    # ---- EP-14 ----

    def test_ep14_lote_retorna_200(self) -> None:
        """EP-14 retorna 200 com lista de IDs."""
        with patch(_SVC) as mock:
            mock.return_value.listar_agrupamentos_correlacionados_lote.return_value = []  # noqa: E501
            res = self.client.post(
                f"{_BASE}/territorio-saber/agrupamentos-correlacionados/",
                [1],
                format="json",
            )
        self.assertEqual(res.status_code, 200)

    def test_ep14_lote_com_data_base(self) -> None:
        """EP-14 retorna 200 com dataBase ISO 8601."""
        with patch(_SVC) as mock:
            mock.return_value.listar_agrupamentos_correlacionados_lote.return_value = []  # noqa: E501
            res = self.client.post(
                f"{_BASE}/territorio-saber/agrupamentos-correlacionados/"
                "?dataBase=2024-01-01",
                [1],
                format="json",
            )
        self.assertEqual(res.status_code, 200)

    def test_ep14_corpo_invalido_retorna_400(self) -> None:
        """EP-14 retorna 400 quando corpo não é lista."""
        with patch(_SVC):
            res = self.client.post(
                f"{_BASE}/territorio-saber/agrupamentos-correlacionados/",
                {"not": "list"},
                format="json",
            )
        self.assertEqual(res.status_code, 400)

    def test_ep14_sem_api_key_retorna_401(self) -> None:
        """EP-14 sem API Key retorna 401."""
        res = APIClient().post(
            f"{_BASE}/territorio-saber/agrupamentos-correlacionados/",
            [1],
            format="json",
        )
        self.assertEqual(res.status_code, 401)

    # ---- EP-15 ----

    def test_ep15_territorio_retorna_200(self) -> None:
        """EP-15 retorna 200 com lista de IDs."""
        with patch(_SVC) as mock:
            mock.return_value.listar_agrupamentos_territorio.return_value = []
            res = self.client.post(
                f"{_BASE}/territorio-saber/agrupamentos/",
                [1],
                format="json",
            )
        self.assertEqual(res.status_code, 200)

    def test_ep15_corpo_invalido_retorna_400(self) -> None:
        """EP-15 retorna 400 quando corpo não é lista."""
        with patch(_SVC):
            res = self.client.post(
                f"{_BASE}/territorio-saber/agrupamentos/",
                {"not": "list"},
                format="json",
            )
        self.assertEqual(res.status_code, 400)

    def test_ep15_sem_api_key_retorna_401(self) -> None:
        """EP-15 sem API Key retorna 401."""
        res = APIClient().post(
            f"{_BASE}/territorio-saber/agrupamentos/",
            [1],
            format="json",
        )
        self.assertEqual(res.status_code, 401)
