"""Testes das views do domínio Turmas."""

from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

_SVC = "apps.turmas.api.views.TurmasService"
_BASE = "/api/v1/pedagogico/turmas"

_TURMA = {
    "codigo": 2112345,
    "nomeTurma": "3A EF",
    "anoLetivo": 2024,
    "ano": "3",
    "tipoTurma": 1,
    "ueCodigo": "000532",
    "modalidade": "Ensino Fundamental",
    "codigoModalidade": 5,
    "semestre": 0,
    "ensinoEspecial": False,
    "serieEnsino": "3º Ano",
    "codigoSerieEnsino": 3,
    "situacao": "A",
    "extinta": False,
}

_TURMA_DADOS = {
    **_TURMA,
    "duracaoTurno": 2,
    "tipoTurno": 1,
    "dataInicioTurma": None,
    "dataFim": None,
    "codigoTipoPrograma": None,
    "codigoModalidadeEtapa": None,
    "dataAtualizacao": None,
    "dataStatusTurmaEscola": None,
}

_TURMA_SINC = {
    "codigo": 2112345,
    "ueCodigo": "000532",
    "anoLetivo": 2024,
    "dataInicioTurma": None,
    "dataFim": None,
    "dataAtualizacao": None,
    "dataStatusTurmaEscola": None,
    "situacao": "A",
    "extinta": False,
    "codigoModalidade": 5,
    "modalidade": "Ensino Fundamental",
    "semestre": 0,
    "ensinoEspecial": False,
    "codigoSerieEnsino": 3,
    "serieEnsino": "3º Ano",
}

_TURMA_HISTORICA = {
    "ano": "3",
    "anoLetivo": 2024,
    "codigo": 2112345,
    "tipoTurma": 1,
    "modalidade": "Ensino Fundamental",
    "codigoModalidade": 5,
    "nomeTurma": "3A EF",
    "semestre": 0,
    "duracaoTurno": 2,
    "tipoTurno": 1,
    "dataFim": None,
    "ehistorico": False,
    "ensinoEspecial": False,
    "etapaEJA": 0,
    "serieEnsino": "3º Ano",
    "dataInicioTurma": None,
    "extinta": False,
    "situacao": "A",
    "ueCodigo": "000532",
}


class TestTurmasViews(TestCase):
    """Testes dos endpoints do domínio Turmas."""

    def setUp(self):
        self.client = APIClient()
        self.client.credentials(HTTP_X_API_KEY="dev-key-default")
        self.anon = APIClient()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def get(self, path):
        return self.client.get(f"{_BASE}{path}")

    def post(self, path, payload):
        return self.client.post(f"{_BASE}{path}", payload, format="json")

    def assert_401(self, path, method="get", payload=None):
        kwargs = {"format": "json"} if payload else {}
        response = getattr(self.anon, method)(f"{_BASE}{path}", payload, **kwargs)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ------------------------------------------------------------------
    # POST turmas-regulares
    # ------------------------------------------------------------------

    @patch(_SVC)
    def test_turmas_regulares_retorna_200(self, mock_svc):
        mock_svc.return_value.turmas_regulares.return_value = [_TURMA]
        res = self.post("/turmas-regulares/", [2112345])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_svc.return_value.turmas_regulares.assert_called_once_with([2112345])

    @patch(_SVC)
    def test_turmas_regulares_lista_vazia_retorna_200(self, mock_svc):
        mock_svc.return_value.turmas_regulares.return_value = []
        res = self.post("/turmas-regulares/", [])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, [])

    @patch(_SVC)
    def test_turmas_regulares_corpo_invalido_usa_lista_vazia(self, mock_svc):
        mock_svc.return_value.turmas_regulares.return_value = []
        res = self.post("/turmas-regulares/", {"codigo": 123})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_svc.return_value.turmas_regulares.assert_called_once_with([])

    def test_turmas_regulares_sem_api_key_retorna_401(self):
        self.assert_401("/turmas-regulares/", method="post", payload=[1])

    @patch(_SVC)
    def test_turmas_regulares_shape_camel_case(self, mock_svc):
        mock_svc.return_value.turmas_regulares.return_value = [_TURMA]
        res = self.post("/turmas-regulares/", [2112345])
        item = res.data[0]
        for campo in ("codigo", "nomeTurma", "anoLetivo", "tipoTurma", "ueCodigo"):
            self.assertIn(campo, item)

    # ------------------------------------------------------------------
    # POST turmas-programa
    # ------------------------------------------------------------------

    @patch(_SVC)
    def test_turmas_programa_retorna_200(self, mock_svc):
        mock_svc.return_value.turmas_programa.return_value = [_TURMA]
        res = self.post("/turmas-programa/", [2112345])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_svc.return_value.turmas_programa.assert_called_once_with([2112345])

    @patch(_SVC)
    def test_turmas_programa_lista_vazia_retorna_200(self, mock_svc):
        mock_svc.return_value.turmas_programa.return_value = []
        res = self.post("/turmas-programa/", [])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, [])

    def test_turmas_programa_sem_api_key_retorna_401(self):
        self.assert_401("/turmas-programa/", method="post", payload=[1])

    # ------------------------------------------------------------------
    # POST listar-turmas
    # ------------------------------------------------------------------

    @patch(_SVC)
    def test_listar_turmas_retorna_200(self, mock_svc):
        mock_svc.return_value.listar_turmas.return_value = [_TURMA]
        res = self.post("/listar-turmas/", [2112345])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_svc.return_value.listar_turmas.assert_called_once_with([2112345])

    @patch(_SVC)
    def test_listar_turmas_shape_campos_obrigatorios(self, mock_svc):
        mock_svc.return_value.listar_turmas.return_value = [_TURMA]
        res = self.post("/listar-turmas/", [2112345])
        item = res.data[0]
        campos = (
            "codigo", "nomeTurma", "anoLetivo", "ano", "tipoTurma",
            "ueCodigo", "modalidade", "codigoModalidade", "semestre",
            "ensinoEspecial", "serieEnsino", "codigoSerieEnsino",
            "situacao", "extinta",
        )
        for campo in campos:
            self.assertIn(campo, item, f"campo ausente: {campo}")

    def test_listar_turmas_sem_api_key_retorna_401(self):
        self.assert_401("/listar-turmas/", method="post", payload=[1])

    # ------------------------------------------------------------------
    # GET {codigoTurma}/dados
    # ------------------------------------------------------------------

    @patch(_SVC)
    def test_turma_dados_retorna_200(self, mock_svc):
        mock_svc.return_value.dados_turma.return_value = _TURMA_DADOS
        res = self.get("/2112345/dados/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_svc.return_value.dados_turma.assert_called_once_with(2112345)

    @patch(_SVC)
    def test_turma_dados_nao_encontrada_retorna_404(self, mock_svc):
        mock_svc.return_value.dados_turma.return_value = None
        res = self.get("/9999999/dados/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_turma_dados_sem_api_key_retorna_401(self):
        self.assert_401("/2112345/dados/")

    @patch(_SVC)
    def test_turma_dados_shape_campos_obrigatorios(self, mock_svc):
        mock_svc.return_value.dados_turma.return_value = _TURMA_DADOS
        res = self.get("/2112345/dados/")
        campos = (
            "codigo", "anoLetivo", "nomeTurma", "tipoTurma", "ueCodigo",
            "semestre", "ensinoEspecial", "extinta", "situacao",
            "codigoTipoPrograma", "codigoModalidadeEtapa",
            "dataAtualizacao", "dataStatusTurmaEscola",
        )
        for campo in campos:
            self.assertIn(campo, res.data, f"campo ausente: {campo}")

    # ------------------------------------------------------------------
    # GET sincronizacoes-institucionais
    # ------------------------------------------------------------------

    @patch(_SVC)
    def test_sincronizacoes_retorna_200(self, mock_svc):
        mock_svc.return_value.sincronizacoes_institucionais.return_value = _TURMA_SINC
        res = self.get("/ues/000532/turmas/2112345/sincronizacoes-institucionais/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_svc.return_value.sincronizacoes_institucionais.assert_called_once_with(
            "000532", 2112345
        )

    @patch(_SVC)
    def test_sincronizacoes_nao_encontrada_retorna_404(self, mock_svc):
        mock_svc.return_value.sincronizacoes_institucionais.return_value = None
        res = self.get("/ues/999999/turmas/9999999/sincronizacoes-institucionais/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_sincronizacoes_sem_api_key_retorna_401(self):
        self.assert_401("/ues/000532/turmas/2112345/sincronizacoes-institucionais/")

    @patch(_SVC)
    def test_sincronizacoes_shape_campos_obrigatorios(self, mock_svc):
        mock_svc.return_value.sincronizacoes_institucionais.return_value = _TURMA_SINC
        res = self.get("/ues/000532/turmas/2112345/sincronizacoes-institucionais/")
        campos = (
            "codigo", "ueCodigo", "anoLetivo", "dataInicioTurma", "dataFim",
            "dataAtualizacao", "dataStatusTurmaEscola", "situacao", "extinta",
            "codigoModalidade", "modalidade", "semestre", "ensinoEspecial",
            "codigoSerieEnsino", "serieEnsino",
        )
        for campo in campos:
            self.assertIn(campo, res.data, f"campo ausente: {campo}")

    # ------------------------------------------------------------------
    # GET anos-letivos por UE
    # ------------------------------------------------------------------

    @patch(_SVC)
    def test_anos_letivos_retorna_200(self, mock_svc):
        mock_svc.return_value.anos_letivos_por_ue.return_value = [2023, 2024]
        res = self.get("/ue/000532/sincronizacoes-institucionais/anosLetivos/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, [2023, 2024])
        mock_svc.return_value.anos_letivos_por_ue.assert_called_once_with("000532")

    @patch(_SVC)
    def test_anos_letivos_sem_turmas_retorna_lista_vazia(self, mock_svc):
        mock_svc.return_value.anos_letivos_por_ue.return_value = []
        res = self.get("/ue/999999/sincronizacoes-institucionais/anosLetivos/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, [])

    def test_anos_letivos_sem_api_key_retorna_401(self):
        self.assert_401("/ue/000532/sincronizacoes-institucionais/anosLetivos/")

    # ------------------------------------------------------------------
    # GET turmas-historicas-geral
    # ------------------------------------------------------------------

    @patch(_SVC)
    def test_turmas_historicas_retorna_200(self, mock_svc):
        mock_svc.return_value.turmas_historicas_professor.return_value = [_TURMA_HISTORICA]
        res = self.get("/anos-letivos/2024/professor/7654321/turmas-historicas-geral/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_svc.return_value.turmas_historicas_professor.assert_called_once_with(
            2024, "7654321"
        )

    @patch(_SVC)
    def test_turmas_historicas_sem_resultado_retorna_404(self, mock_svc):
        mock_svc.return_value.turmas_historicas_professor.return_value = []
        res = self.get("/anos-letivos/2099/professor/0000000/turmas-historicas-geral/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_turmas_historicas_sem_api_key_retorna_401(self):
        self.assert_401(
            "/anos-letivos/2024/professor/7654321/turmas-historicas-geral/"
        )

    @patch(_SVC)
    def test_turmas_historicas_shape_turma_dto(self, mock_svc):
        mock_svc.return_value.turmas_historicas_professor.return_value = [
            _TURMA_HISTORICA
        ]
        res = self.get("/anos-letivos/2024/professor/7654321/turmas-historicas-geral/")
        item = res.data[0]
        campos = (
            "ano", "anoLetivo", "codigo", "tipoTurma", "modalidade",
            "codigoModalidade", "nomeTurma", "semestre", "duracaoTurno",
            "tipoTurno", "dataFim", "ehistorico", "ensinoEspecial",
            "etapaEJA", "serieEnsino", "dataInicioTurma", "extinta",
            "situacao", "ueCodigo",
        )
        for campo in campos:
            self.assertIn(campo, item, f"campo ausente no TurmaDTO: {campo}")

    # ------------------------------------------------------------------
    # GET itinerario/ensino-medio
    # ------------------------------------------------------------------

    @patch(_SVC)
    def test_itinerario_ensino_medio_retorna_200(self, mock_svc):
        mock_svc.return_value.itinerarios_ensino_medio.return_value = [
            {"nome": "Itinerário A", "serie": "1"},
            {"nome": "Itinerário B", "serie": "2"},
        ]
        res = self.get("/itinerario/ensino-medio/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data[0]["nome"], "Itinerário A")

    @patch(_SVC)
    def test_itinerario_ensino_medio_lista_vazia_retorna_200(self, mock_svc):
        mock_svc.return_value.itinerarios_ensino_medio.return_value = []
        res = self.get("/itinerario/ensino-medio/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, [])

    def test_itinerario_ensino_medio_sem_api_key_retorna_401(self):
        self.assert_401("/itinerario/ensino-medio/")

    @patch(_SVC)
    def test_itinerario_ensino_medio_shape(self, mock_svc):
        mock_svc.return_value.itinerarios_ensino_medio.return_value = [
            {"nome": "Ciências da Natureza", "serie": "1"}
        ]
        res = self.get("/itinerario/ensino-medio/")
        item = res.data[0]
        self.assertIn("nome", item)
        self.assertIn("serie", item)

    # ------------------------------------------------------------------
    # Todos os endpoints protegidos
    # ------------------------------------------------------------------

    def test_todos_endpoints_sem_api_key_retornam_401(self):
        """Verifica proteção de todos os endpoints do domínio Turmas."""
        casos_get = [
            "/2112345/dados/",
            "/ues/000532/turmas/2112345/sincronizacoes-institucionais/",
            "/ue/000532/sincronizacoes-institucionais/anosLetivos/",
            "/anos-letivos/2024/professor/7654321/turmas-historicas-geral/",
            "/itinerario/ensino-medio/",
        ]
        for path in casos_get:
            res = self.anon.get(f"{_BASE}{path}")
            self.assertEqual(
                res.status_code,
                status.HTTP_401_UNAUTHORIZED,
                f"esperado 401 em GET {path}",
            )

        casos_post = ["/turmas-regulares/", "/turmas-programa/", "/listar-turmas/"]
        for path in casos_post:
            res = self.anon.post(f"{_BASE}{path}", [], format="json")
            self.assertEqual(
                res.status_code,
                status.HTTP_401_UNAUTHORIZED,
                f"esperado 401 em POST {path}",
            )
