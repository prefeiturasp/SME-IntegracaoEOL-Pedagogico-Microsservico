"""Testes das views do domínio Turmas."""

from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

_SVC = "apps.turmas.api.views.TurmasService"
_BASE = "/api/v1/pedagogico/turmas"

_TURMA = {
    "codigo": 2112345,
    "nome_turma": "3A EF",
    "ano_letivo": 2024,
    "ano": "3",
    "tipo_turma": 1,
    "ue_codigo": "000532",
    "modalidade": "Ensino Fundamental",
    "codigo_modalidade": 5,
    "semestre": 0,
    "ensino_especial": False,
    "serie_ensino": "3º Ano",
    "codigo_serie_ensino": 3,
    "situacao": "A",
    "extinta": False,
    "tipo_turno": 1,
    "codigo_etapa_ensino": 5,
    "codigo_ciclo_ensino": 3,
}

_TURMA_DADOS = {
    **_TURMA,
    "duracao_turno": 2,
    "tipo_turno": 1,
    "data_inicio_turma": None,
    "data_fim": None,
    "codigo_tipo_programa": None,
    "codigo_modalidade_etapa": None,
    "data_atualizacao": None,
    "data_status_turma_escola": None,
}

_TURMA_SINC = {
    "ano": "3",
    "ano_letivo": 2024,
    "codigo": 2112345,
    "tipo_turma": 1,
    "modalidade": "Ensino Fundamental",
    "codigo_modalidade": 5,
    "nome_turma": "3A EF",
    "semestre": 0,
    "duracao_turno": 6,
    "tipo_turno": 1,
    "data_fim_turma": None,
    "ensino_especial": False,
    "etapa_eja": 0,
    "serie_ensino": "3º Ano",
    "codigo_serie_ensino": 3,
    "data_inicio_turma": None,
    "extinta": False,
    "situacao": "A",
    "ue_codigo": "000532",
    "data_atualizacao": None,
    "data_status_turma_escola": None,
    "etapa_ensino": 5,
    "ciclo_ensino": 3,
    "tipo_escola": 4,
    "descricao_grade_programa": "GRADE EMEI",
    "tipo_grade_programa": 1,
    "codigo_grade_programa": 10,
    "nome_filtro": "3A EF - 3º Ano",
    "componentes": [
        {
            "nome_componente_curricular": "ED.INF. EMEI 4 HS",
            "componente_curricular_codigo": 512,
            "registro_funcional": "1234567",
            "data_disponibizacao": None,
        }
    ],
}

_TURMA_HISTORICA = {
    "ano": "3",
    "ano_letivo": 2024,
    "codigo": 2112345,
    "modalidade": "Ensino Fundamental",
    "codigo_modalidade": 5,
    "nome_turma": "3A EF",
    "semestre": 0,
}

_TURMA_ATRIBUIDA = {
    "codigo_escola": "000001",
    "codigo_turma": 9000001,
    "ano_letivo": 2026,
    "modalidade": "Fundamental",
    "semestre": 0,
    "codigo_modalidade": 5,
    "codigo_dre": "100000",
    "dre": "DRE FICTICIA",
    "dre_abreviacao": "X",
    "ue": "EMEF FICTICIA DE TESTE",
    "ue_abreviacao": "EMEF FICTICIA DE TESTE",
    "nome_turma": "5A",
    "ano": "5",
    "tipo_ue": "DIRETA",
    "codigo_tipo_ue": 1,
    "codigo_tipo_escola": 1,
    "tipo_escola": "EMEF",
    "duracao_turno": 6,
    "tipo_turno": 1,
}

_TURMA_ELEGIVEL = {
    "cod_turma": 3011229,
    "nome_turma": "5A",
}


class TestTurmasViews(TestCase):
    """Valida views do domínio Turmas."""

    def setUp(self):
        self.client = APIClient()
        self.client.credentials(HTTP_X_API_KEY="dev-key-default")
        self.anon = APIClient()

    def get(self, path):
        return self.client.get(f"{_BASE}{path}")

    def post(self, path, payload):
        return self.client.post(f"{_BASE}{path}", payload, format="json")

    def assert_401(self, path, method="get", payload=None):
        kwargs = {"format": "json"} if payload else {}
        response = getattr(self.anon, method)(
            f"{_BASE}{path}", payload, **kwargs
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch(_SVC)
    def test_turmas_regulares_retorna_200(self, mock_svc):
        mock_svc.return_value.turmas_regulares.return_value = [_TURMA]
        res = self.post("/turmas-regulares/", [2112345])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_svc.return_value.turmas_regulares.assert_called_once_with(
            [2112345]
        )

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
    def test_turmas_regulares_shape_campos_obrigatorios(self, mock_svc):
        mock_svc.return_value.turmas_regulares.return_value = [_TURMA]
        res = self.post("/turmas-regulares/", [2112345])
        item = res.data[0]
        for campo in (
            "codigo",
            "nome_turma",
            "ano_letivo",
            "tipo_turma",
            "ue_codigo",
        ):
            self.assertIn(campo, item)

    @patch(_SVC)
    def test_turmas_programa_retorna_200(self, mock_svc):
        mock_svc.return_value.turmas_programa.return_value = [_TURMA]
        res = self.post("/turmas-programa/", [2112345])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_svc.return_value.turmas_programa.assert_called_once_with(
            [2112345]
        )

    @patch(_SVC)
    def test_turmas_programa_lista_vazia_retorna_200(self, mock_svc):
        mock_svc.return_value.turmas_programa.return_value = []
        res = self.post("/turmas-programa/", [])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, [])

    def test_turmas_programa_sem_api_key_retorna_401(self):
        self.assert_401("/turmas-programa/", method="post", payload=[1])

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
            "codigo",
            "nome_turma",
            "ano_letivo",
            "ano",
            "tipo_turma",
            "ue_codigo",
            "modalidade",
            "codigo_modalidade",
            "semestre",
            "ensino_especial",
            "serie_ensino",
            "codigo_serie_ensino",
            "situacao",
            "extinta",
            "tipo_turno",
            "codigo_etapa_ensino",
            "codigo_ciclo_ensino",
        )
        for campo in campos:
            self.assertIn(campo, item, f"campo ausente: {campo}")

    def test_listar_turmas_sem_api_key_retorna_401(self):
        self.assert_401("/listar-turmas/", method="post", payload=[1])

    @patch(_SVC)
    def test_turmas_atribuidas_dre_ue_retorna_200(self, mock_svc):
        mock_svc.return_value.turmas_atribuidas_dre_ue.return_value = [
            _TURMA_ATRIBUIDA
        ]

        res = self.post("/turmas-atribuidas-dre-ue/", ["000001"])

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]["codigo_turma"], 9000001)
        mock_svc.return_value.turmas_atribuidas_dre_ue.assert_called_once_with(
            ["000001"]
        )

    @patch(_SVC)
    def test_turmas_atribuidas_dre_ue_corpo_invalido_usa_lista_vazia(
        self,
        mock_svc,
    ):
        mock_svc.return_value.turmas_atribuidas_dre_ue.return_value = []

        res = self.post("/turmas-atribuidas-dre-ue/", {"codigo": "000001"})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, [])
        mock_svc.return_value.turmas_atribuidas_dre_ue.assert_called_once_with(
            []
        )

    def test_turmas_atribuidas_dre_ue_sem_api_key_retorna_401(self):
        self.assert_401(
            "/turmas-atribuidas-dre-ue/",
            method="post",
            payload=["000001"],
        )

    @patch(_SVC)
    def test_todas_turmas_atribuidas_dre_ue_sem_filtro_retorna_200(
        self, mock_svc
    ):
        mock_svc.return_value.todas_turmas_atribuidas_dre_ue.return_value = {
            "abrangencia": None,
            "dres": [{"codigo": "100000"}],
        }

        res = self.get("/turmas-atribuidas-dre-ue/todas/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["dres"][0]["codigo"], "100000")
        mock_svc.return_value.todas_turmas_atribuidas_dre_ue.assert_called_once_with()
        mock_svc.return_value.turmas_atribuidas_dre_ue_por_dre.assert_not_called()

    @patch(_SVC)
    def test_todas_turmas_atribuidas_dre_ue_com_codigo_dre_filtra(
        self, mock_svc
    ):
        mock_svc.return_value.turmas_atribuidas_dre_ue_por_dre.return_value = {
            "abrangencia": None,
            "dres": [{"codigo": "100000"}],
        }

        res = self.get("/turmas-atribuidas-dre-ue/todas/?codigo_dre=100000")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["dres"][0]["codigo"], "100000")
        mock_svc.return_value.turmas_atribuidas_dre_ue_por_dre.assert_called_once_with(
            "100000"
        )
        mock_svc.return_value.todas_turmas_atribuidas_dre_ue.assert_not_called()

    @patch(_SVC)
    def test_todas_turmas_atribuidas_dre_ue_codigo_dre_em_branco_ignora_filtro(
        self, mock_svc
    ):
        mock_svc.return_value.todas_turmas_atribuidas_dre_ue.return_value = {
            "abrangencia": None,
            "dres": [],
        }

        res = self.get("/turmas-atribuidas-dre-ue/todas/?codigo_dre=  ")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_svc.return_value.todas_turmas_atribuidas_dre_ue.assert_called_once_with()

    def test_todas_turmas_atribuidas_dre_ue_sem_api_key_retorna_401(self):
        self.assert_401("/turmas-atribuidas-dre-ue/todas/")

    @patch(_SVC)
    def test_turmas_atribuidas_dre_ue_por_turmas_retorna_200(self, mock_svc):
        mock_svc.return_value.turmas_atribuidas_dre_ue_por_turmas.return_value = {
            "abrangencia": None,
            "dres": [{"codigo": "100000"}],
        }

        res = self.post(
            "/turmas-atribuidas-dre-ue/por-turmas/", [9000001]
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["dres"][0]["codigo"], "100000")
        mock_svc.return_value.turmas_atribuidas_dre_ue_por_turmas.assert_called_once_with(
            [9000001]
        )

    @patch(_SVC)
    def test_turmas_atribuidas_dre_ue_por_turmas_ignora_codigos_invalidos(
        self, mock_svc
    ):
        mock_svc.return_value.turmas_atribuidas_dre_ue_por_turmas.return_value = {
            "abrangencia": None,
            "dres": [],
        }

        res = self.post(
            "/turmas-atribuidas-dre-ue/por-turmas/",
            [9000001, "abc", None, ""],
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_svc.return_value.turmas_atribuidas_dre_ue_por_turmas.assert_called_once_with(
            [9000001]
        )

    @patch(_SVC)
    def test_turmas_atribuidas_dre_ue_por_turmas_corpo_invalido_usa_lista_vazia(
        self, mock_svc
    ):
        mock_svc.return_value.turmas_atribuidas_dre_ue_por_turmas.return_value = {
            "abrangencia": None,
            "dres": [],
        }

        res = self.post(
            "/turmas-atribuidas-dre-ue/por-turmas/", {"codigo": 9000001}
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_svc.return_value.turmas_atribuidas_dre_ue_por_turmas.assert_called_once_with(
            []
        )

    def test_turmas_atribuidas_dre_ue_por_turmas_sem_api_key_retorna_401(
        self,
    ):
        self.assert_401(
            "/turmas-atribuidas-dre-ue/por-turmas/",
            method="post",
            payload=[9000001],
        )

    @patch(_SVC)
    def test_turmas_elegiveis_retorna_200(self, mock_svc):
        mock_svc.return_value.turmas_elegiveis.return_value = [_TURMA_ELEGIVEL]
        payload = {
            "codigo_rf": "1234567",
            "codigo_turma": 3011228,
            "componente_curricular": 138,
        }

        res = self.post("/turmas-elegiveis/", payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, [_TURMA_ELEGIVEL])
        mock_svc.return_value.turmas_elegiveis.assert_called_once_with(
            "1234567",
            3011228,
            138,
        )

    @patch(_SVC)
    def test_turmas_elegiveis_payload_invalido_retorna_400(self, mock_svc):
        res = self.post("/turmas-elegiveis/", {"codigo_rf": "1234567"})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        mock_svc.return_value.turmas_elegiveis.assert_not_called()

    def test_turmas_elegiveis_sem_api_key_retorna_401(self):
        self.assert_401(
            "/turmas-elegiveis/",
            method="post",
            payload={
                "codigo_rf": "1234567",
                "codigo_turma": 3011228,
                "componente_curricular": 138,
            },
        )

    @patch(_SVC)
    def test_recorte_fund_medio_eja_retorna_200(self, mock_svc):
        """Verifica retorno 200 e delegação ao service."""
        mock_svc.return_value.turmas_recorte_fund_medio_eja.return_value = [
            _TURMA
        ]
        res = self.post("/recorte-fund-medio-eja/", [2112345])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        (
            mock_svc.return_value.turmas_recorte_fund_medio_eja
        ).assert_called_once_with([2112345])

    @patch(_SVC)
    def test_recorte_fund_medio_eja_corpo_invalido_usa_lista_vazia(
        self, mock_svc
    ):
        """Verifica corpo inválido como lista vazia."""
        mock_svc.return_value.turmas_recorte_fund_medio_eja.return_value = []
        res = self.post("/recorte-fund-medio-eja/", {"codigo": 123})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        (
            mock_svc.return_value.turmas_recorte_fund_medio_eja
        ).assert_called_once_with([])

    @patch(_SVC)
    def test_recorte_por_tipo_repassa_codigos_e_filtros(self, mock_svc):
        """Lê códigos do corpo e tipo/UE/semestre da query string."""
        mock_svc.return_value.turmas_recorte_por_tipo.return_value = [2112345]
        res = self.client.post(
            f"{_BASE}/recorte-por-tipo/"
            "?tipos_turma=1&tipos_turma=5&ue_codigo=000532&semestre=1",
            [2112345, 9],
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, [2112345])
        (
            mock_svc.return_value.turmas_recorte_por_tipo
        ).assert_called_once_with([2112345, 9], [1, 5], "000532", 1)

    @patch(_SVC)
    def test_codigos_turmas_contagem_repassa_ues_e_filtros(self, mock_svc):
        """Lê UEs do corpo e ano/modalidade/ano_letivo da query string."""
        (
            mock_svc.return_value.codigos_turmas_por_ano_modalidade_dre
        ).return_value = [3011258]
        res = self.client.post(
            f"{_BASE}/codigos-turmas-contagem/"
            "?ano_turma=1&codigo_modalidade=5&ano_letivo=2026",
            ["019370", "108200"],
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, [3011258])
        (
            mock_svc.return_value.codigos_turmas_por_ano_modalidade_dre
        ).assert_called_once_with(["019370", "108200"], "1", 5, 2026)

    @patch(_SVC)
    def test_codigos_turmas_contagem_sem_filtros(self, mock_svc):
        """Sem query string, os filtros opcionais vão vazios/None."""
        (
            mock_svc.return_value.codigos_turmas_por_ano_modalidade_dre
        ).return_value = []
        res = self.post("/codigos-turmas-contagem/", ["019370"])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        (
            mock_svc.return_value.codigos_turmas_por_ano_modalidade_dre
        ).assert_called_once_with(["019370"], None, None, None)

    @patch(_SVC)
    def test_recorte_por_tipo_sem_filtros(self, mock_svc):
        """Sem query string, os filtros opcionais vão vazios/None."""
        mock_svc.return_value.turmas_recorte_por_tipo.return_value = []
        res = self.post("/recorte-por-tipo/", [2112345])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        (
            mock_svc.return_value.turmas_recorte_por_tipo
        ).assert_called_once_with([2112345], [], None, None)

    @patch(_SVC)
    def test_recorte_por_tipo_aceita_camelcase(self, mock_svc):
        """Aceita os filtros em camelCase (tiposTurma/ueCodigo)."""
        mock_svc.return_value.turmas_recorte_por_tipo.return_value = []
        res = self.client.post(
            f"{_BASE}/recorte-por-tipo/?tiposTurma=3&ueCodigo=000999",
            [2112345],
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        (
            mock_svc.return_value.turmas_recorte_por_tipo
        ).assert_called_once_with([2112345], [3], "000999", None)

    def test_recorte_por_tipo_sem_api_key_retorna_401(self):
        self.assert_401("/recorte-por-tipo/", method="post", payload=[1])

    def test_recorte_fund_medio_eja_sem_api_key_retorna_401(self):
        """Verifica se requisição sem autenticação é rejeitada."""
        self.assert_401("/recorte-fund-medio-eja/", method="post", payload=[1])

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
            "codigo",
            "ano_letivo",
            "nome_turma",
            "tipo_turma",
            "ue_codigo",
            "semestre",
            "ensino_especial",
            "extinta",
            "situacao",
            "codigo_tipo_programa",
            "codigo_modalidade_etapa",
            "data_atualizacao",
            "data_status_turma_escola",
        )
        for campo in campos:
            self.assertIn(campo, res.data, f"campo ausente: {campo}")

    @patch(_SVC)
    def test_sincronizacoes_retorna_200(self, mock_svc):
        mock_svc.return_value.sincronizacoes_institucionais.return_value = (
            _TURMA_SINC
        )
        res = self.get(
            "/ues/000532/turmas/2112345/sincronizacoes-institucionais/"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_svc.return_value.sincronizacoes_institucionais.assert_called_once_with(
            "000532", 2112345
        )

    @patch(_SVC)
    def test_sincronizacoes_ue_qualquer_valor_retorna_200(self, mock_svc):
        """UE com qualquer valor retorna 200 e delega o valor recebido."""
        mock_svc.return_value.sincronizacoes_institucionais.return_value = (
            _TURMA_SINC
        )
        res = self.get("/ues/0/turmas/2112345/sincronizacoes-institucionais/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_svc.return_value.sincronizacoes_institucionais.assert_called_once_with(
            "0", 2112345
        )

    @patch(_SVC)
    def test_sincronizacoes_nao_encontrada_retorna_400(self, mock_svc):
        """Sem turma para os parâmetros, retorna 400 com a mensagem."""
        mock_svc.return_value.sincronizacoes_institucionais.return_value = None
        res = self.get(
            "/ues/999999/turmas/9999999/sincronizacoes-institucionais/"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            res.data["detail"],
            "Houve um comportamento inesperado do sistema. "
            "Por favor, contate a SME.",
        )

    def test_sincronizacoes_sem_api_key_retorna_401(self):
        self.assert_401(
            "/ues/000532/turmas/2112345/sincronizacoes-institucionais/"
        )

    @patch(_SVC)
    def test_sincronizacoes_shape_campos_obrigatorios(self, mock_svc):
        mock_svc.return_value.sincronizacoes_institucionais.return_value = (
            _TURMA_SINC
        )
        res = self.get(
            "/ues/000532/turmas/2112345/sincronizacoes-institucionais/"
        )
        campos = (
            "ano",
            "ano_letivo",
            "codigo",
            "tipo_turma",
            "modalidade",
            "codigo_modalidade",
            "nome_turma",
            "semestre",
            "duracao_turno",
            "tipo_turno",
            "data_fim_turma",
            "ensino_especial",
            "etapa_eja",
            "serie_ensino",
            "codigo_serie_ensino",
            "data_inicio_turma",
            "extinta",
            "situacao",
            "ue_codigo",
            "data_atualizacao",
            "data_status_turma_escola",
            "etapa_ensino",
            "ciclo_ensino",
            "tipo_escola",
            "descricao_grade_programa",
            "tipo_grade_programa",
            "codigo_grade_programa",
            "nome_filtro",
            "componentes",
        )
        for campo in campos:
            self.assertIn(campo, res.data, f"campo ausente: {campo}")

    @patch(_SVC)
    def test_anos_letivos_com_filtro_delega_anos(self, mock_svc):
        """Com anos_letivos_vigente válidos, delega a lista de inteiros."""
        mock_svc.return_value.codigos_turmas_por_ue.return_value = [
            3036225,
            3082921,
        ]
        res = self.get(
            "/ue/019437/sincronizacoes-institucionais/anos-letivos/"
            "?anos_letivos_vigente=2025&anos_letivos_vigente=2026"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, [3036225, 3082921])
        mock_svc.return_value.codigos_turmas_por_ue.assert_called_once_with(
            "019437", [2025, 2026]
        )

    @patch(_SVC)
    def test_anos_letivos_sem_filtro_lista_todos(self, mock_svc):
        """Sem ano informado, delega com None e lista todos da UE."""
        mock_svc.return_value.codigos_turmas_por_ue.return_value = [
            3036225,
            3082921,
        ]
        res = self.get(
            "/ue/019437/sincronizacoes-institucionais/anos-letivos/"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, [3036225, 3082921])
        mock_svc.return_value.codigos_turmas_por_ue.assert_called_once_with(
            "019437", None
        )

    @patch(_SVC)
    def test_anos_letivos_sem_turmas_retorna_lista_vazia(self, mock_svc):
        mock_svc.return_value.codigos_turmas_por_ue.return_value = []
        res = self.get(
            "/ue/999999/sincronizacoes-institucionais/anos-letivos/"
            "?anos_letivos_vigente=2025"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, [])

    @patch(_SVC)
    def test_anos_letivos_vigente_invalido_retorna_400(self, mock_svc):
        """Valor não inteiro em anos_letivos_vigente retorna 400."""
        res = self.get(
            "/ue/019437/sincronizacoes-institucionais/anos-letivos/"
            "?anos_letivos_vigente=abc"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        mock_svc.return_value.codigos_turmas_por_ue.assert_not_called()

    @patch(_SVC)
    def test_anos_letivos_vigente_zero_retorna_vazio(self, mock_svc):
        """Ano 0 explícito retorna [] sem consultar o service."""
        res = self.get(
            "/ue/019437/sincronizacoes-institucionais/anos-letivos/"
            "?anos_letivos_vigente=0"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, [])
        mock_svc.return_value.codigos_turmas_por_ue.assert_not_called()

    @patch(_SVC)
    def test_anos_letivos_vigente_item_vazio_lista_todos(self, mock_svc):
        """Item vazio enviado pelo Swagger é descartado e lista todos."""
        mock_svc.return_value.codigos_turmas_por_ue.return_value = [3036225]
        res = self.get(
            "/ue/019437/sincronizacoes-institucionais/anos-letivos/"
            "?anos_letivos_vigente="
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_svc.return_value.codigos_turmas_por_ue.assert_called_once_with(
            "019437", None
        )

    @patch(_SVC)
    def test_anos_letivos_vigente_zero_e_ano_valido_filtra(self, mock_svc):
        """Ano 0 é descartado mas o ano válido permanece no filtro."""
        mock_svc.return_value.codigos_turmas_por_ue.return_value = [3036225]
        res = self.get(
            "/ue/019437/sincronizacoes-institucionais/anos-letivos/"
            "?anos_letivos_vigente=0&anos_letivos_vigente=2025"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_svc.return_value.codigos_turmas_por_ue.assert_called_once_with(
            "019437", [2025]
        )

    def test_anos_letivos_sem_api_key_retorna_401(self):
        self.assert_401(
            "/ue/000532/sincronizacoes-institucionais/anos-letivos/"
        )

    @patch(_SVC)
    def test_turmas_historicas_retorna_200(self, mock_svc):
        mock_svc.return_value.turmas_historicas_professor.return_value = [
            _TURMA_HISTORICA
        ]
        res = self.get(
            "/anos-letivos/2024/professor/7654321/turmas-historicas-geral/"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_svc.return_value.turmas_historicas_professor.assert_called_once_with(
            2024, "7654321"
        )

    @patch(_SVC)
    def test_turmas_historicas_sem_resultado_retorna_lista_vazia(
        self, mock_svc
    ):
        mock_svc.return_value.turmas_historicas_professor.return_value = []
        res = self.get(
            "/anos-letivos/2099/professor/0000000/turmas-historicas-geral/"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, [])

    def test_turmas_historicas_sem_api_key_retorna_401(self):
        self.assert_401(
            "/anos-letivos/2024/professor/7654321/turmas-historicas-geral/"
        )

    @patch(_SVC)
    def test_turmas_historicas_shape_turma_dto(self, mock_svc):
        mock_svc.return_value.turmas_historicas_professor.return_value = [
            _TURMA_HISTORICA
        ]
        res = self.get(
            "/anos-letivos/2024/professor/7654321/turmas-historicas-geral/"
        )
        item = res.data[0]
        campos = (
            "ano",
            "ano_letivo",
            "codigo",
            "modalidade",
            "codigo_modalidade",
            "nome_turma",
            "semestre",
        )
        self.assertEqual(set(item.keys()), set(campos))
        removidos = (
            "tipo_turma",
            "duracao_turno",
            "tipo_turno",
            "data_fim",
            "ehistorico",
            "ensino_especial",
            "etapa_eja",
            "serie_ensino",
            "data_inicio_turma",
            "extinta",
            "situacao",
            "ue_codigo",
        )
        for campo in removidos:
            self.assertNotIn(campo, item, f"campo legado removido: {campo}")

    @patch(_SVC)
    def test_itinerario_ensino_medio_retorna_200(self, mock_svc):
        mock_svc.return_value.itinerarios_ensino_medio.return_value = [
            {"id": 1, "nome": "Itinerário A", "serie": "1"},
            {"id": 2, "nome": "Itinerário B", "serie": "2"},
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
            {"id": 1, "nome": "Ciências da Natureza", "serie": "1"}
        ]
        res = self.get("/itinerario/ensino-medio/")
        item = res.data[0]
        self.assertIn("id", item)
        self.assertIn("nome", item)
        self.assertIn("serie", item)

    def test_todos_endpoints_sem_api_key_retornam_401(self):
        casos_get = [
            "/2112345/dados/",
            "/ues/000532/turmas/2112345/sincronizacoes-institucionais/",
            "/ue/000532/sincronizacoes-institucionais/anos-letivos/",
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

        casos_post = [
            "/turmas-regulares/",
            "/turmas-programa/",
            "/listar-turmas/",
        ]
        for path in casos_post:
            res = self.anon.post(f"{_BASE}{path}", [], format="json")
            self.assertEqual(
                res.status_code,
                status.HTTP_401_UNAUTHORIZED,
                f"esperado 401 em POST {path}",
            )

    @patch(_SVC)
    def test_modalidades_ensino_retorna_200(self, mock_svc):
        mock_svc.return_value.modalidades_ensino.return_value = [
            "Infantil",
            "Fundamental",
        ]
        res = self.get("/escolas/modalidades-ensino/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, ["Infantil", "Fundamental"])

    def test_modalidades_ensino_sem_api_key_retorna_401(self):
        self.assert_401("/escolas/modalidades-ensino/")

    @patch(_SVC)
    def test_turmas_por_tipo_sala_retorna_200(self, mock_svc):
        mock_svc.return_value.turmas_por_tipo_sala.return_value = [
            {"codigo_turma": 2112345}
        ]
        res = self.get("/escolas/000532/salas/1/anos-letivos/2024/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_svc.return_value.turmas_por_tipo_sala.assert_called_once_with(
            "000532", "1", "2024"
        )

    def test_turmas_por_tipo_sala_sem_api_key_retorna_401(self):
        self.assert_401("/escolas/000532/salas/1/anos-letivos/2024/")

    @patch(_SVC)
    def test_turmas_por_tipo_sala_ano_letivo_nao_numerico_retorna_200_vazio(
        self, mock_svc
    ):
        mock_svc.return_value.turmas_por_tipo_sala.return_value = []
        res = self.get("/escolas/dhhdf/salas/fdg/anos-letivos/as/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, [])
        mock_svc.return_value.turmas_por_tipo_sala.assert_called_once_with(
            "dhhdf", "fdg", "as"
        )

    @patch(_SVC)
    def test_turmas_por_escola_retorna_200(self, mock_svc):
        mock_svc.return_value.turmas_por_escola.return_value = [
            {"codigo_turma": 2112345}
        ]
        res = self.get("/escolas/000532/anos-letivos/2024/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_svc.return_value.turmas_por_escola.assert_called_once_with(
            "000532", "2024"
        )

    def test_turmas_por_escola_sem_api_key_retorna_401(self):
        self.assert_401("/escolas/000532/anos-letivos/2024/")

    @patch(_SVC)
    def test_turmas_por_escola_ano_letivo_nao_numerico_retorna_200_vazio(
        self, mock_svc
    ):
        mock_svc.return_value.turmas_por_escola.return_value = []
        res = self.get("/escolas/019487/anos-letivos/asdasd/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, [])
        mock_svc.return_value.turmas_por_escola.assert_called_once_with(
            "019487", "asdasd"
        )

    @patch(_SVC)
    def test_turmas_sondagem_retorna_200(self, mock_svc):
        mock_svc.return_value.turmas_sondagem.return_value = [
            {"codigo_turma": 2112345}
        ]
        res = self.get("/escolas/000532/turmas-sondagem/anos-letivos/2024/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_svc.return_value.turmas_sondagem.assert_called_once_with(
            "000532", "2024"
        )

    def test_turmas_sondagem_sem_api_key_retorna_401(self):
        self.assert_401(
            "/escolas/000532/turmas-sondagem/anos-letivos/2024/"
        )

    @patch(_SVC)
    def test_turmas_sondagem_ano_letivo_nao_numerico_retorna_200_vazio(
        self, mock_svc
    ):
        mock_svc.return_value.turmas_sondagem.return_value = []
        res = self.get(
            "/escolas/019487/turmas-sondagem/anos-letivos/wewe/"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, [])
        mock_svc.return_value.turmas_sondagem.assert_called_once_with(
            "019487", "wewe"
        )
