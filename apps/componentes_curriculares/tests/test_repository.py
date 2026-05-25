"""Testes de repository do domínio Componentes Curriculares."""

from datetime import UTC, date, datetime
from unittest.mock import patch

from django.test import TestCase

from apps.componentes_curriculares.models import (
    AgrupamentoAtribuicaoTerritorioSaber,
    ComponenteCurricular,
    ComponenteCurricularPlanejamentoRegencia,
    GradeComponenteCurricular,
)
from apps.componentes_curriculares.repository import (
    ComponentesRepository,
    _agrupamento_para_dict,
    _grade_para_componente,
    _parse_csv,
)


def _make_agrupamento(**kwargs):
    """Cria agrupamento com valores padrão."""
    defaults = {
        "cod_agrupamento": 9000,
        "cod_territorio_saber": 1,
        "dt_inicio_atribuicao": datetime(2024, 1, 1, tzinfo=UTC),
        "ano_atribuicao": 2024,
        "ano_letivo": 2024,
        "cod_turma": "T1",
        "cod_componentes_curriculares": "100,200",
        "desc_territorio_saber": "TS",
        "desc_experiencia_pedagogica": "EP",
    }
    defaults.update(kwargs)
    return AgrupamentoAtribuicaoTerritorioSaber.objects.create(**defaults)


class TestHelpersRepository(TestCase):
    """Valida funções auxiliares do repository."""

    def test_parse_csv_vazio(self) -> None:
        """Retorna lista vazia para CSV ausente."""
        self.assertEqual(_parse_csv(None), [])
        self.assertEqual(_parse_csv(""), [])

    def test_parse_csv_valido(self) -> None:
        """Valida conversão de CSV de inteiros."""
        self.assertEqual(_parse_csv("1,2,3"), [1, 2, 3])
        self.assertEqual(_parse_csv("100, 200 "), [100, 200])

    def test_parse_csv_ignora_nao_numericos(self) -> None:
        """Ignora tokens não numéricos no CSV."""
        self.assertEqual(_parse_csv("1,abc,3"), [1, 3])

    def test_grade_para_componente(self) -> None:
        """Valida conversão de grade em componente."""
        resultado = _grade_para_componente(
            {
                "codigo_componente_curricular": 138,
                "descricao_componente_curricular": "LP",
                "regencia": True,
            }
        )

        self.assertEqual(resultado["codigo"], 138)
        self.assertEqual(resultado["descricao"], "LP")
        self.assertTrue(resultado["regencia"])
        self.assertFalse(resultado["exibir_componente_eol"])
        self.assertEqual(resultado["codigos_territorios_agrupamento"], [])

    def test_grade_para_componente_aplica_regencia_classe_infantil(
        self,
    ) -> None:
        """Valida normalização da regência de classe infantil."""
        resultado = _grade_para_componente(
            {
                "codigo_componente_curricular": 512,
                "codigo_componente_curricular_pai": 512,
                "descricao_componente_curricular": "ED.INF. EMEI 4 HS",
                "regencia": False,
            }
        )

        self.assertEqual(resultado["codigo"], 512)
        self.assertEqual(resultado["codigo_componente_curricular_pai"], 512)
        self.assertEqual(resultado["descricao"], "Regência de classe infantil")
        self.assertTrue(resultado["regencia"])

    def test_agrupamento_para_dict_com_experiencia(self) -> None:
        """Valida descrição de agrupamento com experiência pedagógica."""
        agrupamento = _make_agrupamento(
            cod_agrupamento=9999,
            desc_territorio_saber="TS X",
            desc_experiencia_pedagogica="EP Y",
            cod_componentes_curriculares="10,20",
        )

        resultado = _agrupamento_para_dict(agrupamento)

        self.assertEqual(resultado["codigo"], 9999)
        self.assertEqual(resultado["descricao"], "TS X - EP Y")
        self.assertEqual(resultado["codigo_componente_territorio_saber"], 10)
        self.assertEqual(
            resultado["codigos_territorios_agrupamento"], [10, 20]
        )
        self.assertTrue(resultado["territorio_saber"])

    def test_agrupamento_para_dict_sem_experiencia(self) -> None:
        """Valida descrição de agrupamento sem experiência pedagógica."""
        agrupamento = _make_agrupamento(
            desc_territorio_saber="TS Z",
            desc_experiencia_pedagogica=None,
        )

        resultado = _agrupamento_para_dict(agrupamento)

        self.assertEqual(resultado["descricao"], "TS Z")

    def test_agrupamento_para_dict_csv_vazio(self) -> None:
        """Valida agrupamento sem componentes curriculares."""
        agrupamento = _make_agrupamento(
            cod_componentes_curriculares=None,
        )

        resultado = _agrupamento_para_dict(agrupamento)

        self.assertEqual(resultado["codigo_componente_territorio_saber"], 0)
        self.assertEqual(resultado["codigos_territorios_agrupamento"], [])


class TestComponentesRepository(TestCase):
    """Valida consultas de componentes curriculares."""

    def setUp(self) -> None:
        """Inicializa o repository."""
        self.repo = ComponentesRepository()

    @patch("apps.componentes_curriculares.repository._raw")
    def test_listar_por_turma_funcionario(self, mock_raw) -> None:
        """Lista componentes por turma e funcionário."""
        mock_raw.return_value = [
            {
                "codigo": 1,
                "descricao": "Matemática",
                "codigo_componente_territorio_saber": None,
                "codigo_componente_curricular_pai": None,
            }
        ]

        resultado = self.repo.listar_por_turma_funcionario("T1", "RF1")

        self.assertEqual(resultado[0]["codigo"], 1)
        self.assertFalse(resultado[0]["exibir_componente_eol"])
        mock_raw.assert_called_once()

    @patch("apps.componentes_curriculares.repository._raw")
    def test_listar_por_funcionario_deduplica_por_componente(
        self, mock_raw
    ) -> None:
        """Deduplica por componente no endpoint sem turma."""
        mock_raw.return_value = [
            {
                "codigo": 1,
                "codigo_componente_curricular_pai": None,
                "turma_codigo": "T1",
                "professor": "RF1",
            },
            {
                "codigo": 1,
                "codigo_componente_curricular_pai": None,
                "turma_codigo": "T2",
                "professor": "RF1",
            },
        ]

        resultado = self.repo.listar_por_funcionario("RF1")

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["turma_codigo"], "T1")
        self.assertIsNone(resultado[0]["professor"])

    @patch("apps.componentes_curriculares.repository._raw")
    def test_listar_por_funcionario_filtra_por_ano_letivo_atual(
        self, mock_raw
    ) -> None:
        """Filtra atribuições pelo ano letivo corrente."""
        from datetime import date

        mock_raw.return_value = []

        self.repo.listar_por_funcionario("RF1")

        args, _ = mock_raw.call_args
        self.assertIn("ac.ano_letivo", args[0])
        self.assertNotIn("ORDER BY ct.componente_codigo, ct.turma_codigo", args[0])
        self.assertEqual(args[1], ["RF1", date.today().year])

    @patch("apps.componentes_curriculares.repository._raw")
    def test_listar_por_funcionario_normaliza_regencia_infantil_pai(
        self,
        mock_raw,
    ) -> None:
        """Agrupa filho de regência infantil pelo componente pai."""
        ComponenteCurricular.objects.create(
            codigo=512,
            descricao="ED.INF. EMEI 4 HS",
        )
        mock_raw.return_value = [
            {
                "codigo": 513,
                "descricao": "ED.INF. EMEI 2 HS",
                "codigo_componente_curricular_pai": 512,
            }
        ]

        resultado = self.repo.listar_por_funcionario("RF1")

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["codigo"], 512)
        self.assertEqual(
            resultado[0]["descricao"],
            "Regência de classe infantil",
        )
        self.assertTrue(resultado[0]["regencia"])

    @patch("apps.componentes_curriculares.repository._raw")
    def test_listar_planejamento_expande_regencia(self, mock_raw) -> None:
        """Substitui regência por componentes filhos no planejamento."""
        ComponenteCurricular.objects.create(codigo=10, descricao="Filho")
        ComponenteCurricularPlanejamentoRegencia.objects.create(
            id_componente_curricular=10,
            turno=None,
            ano=None,
        )
        mock_raw.return_value = [
            {
                "codigo": 1,
                "descricao": "Regência",
                "regencia": True,
                "turma_codigo": "T1",
                "ano_letivo": 2024,
                "turno_turma": None,
                "ano_turma": None,
                "professor": "RF1",
            }
        ]

        resultado = self.repo.listar_planejamento_por_turma_funcionario(
            "T1",
            "RF1",
        )

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["codigo"], 10)
        self.assertTrue(resultado[0]["planejamento_regencia"])

    def test_listar_regencia_por_ano_turma(self) -> None:
        """Lista componentes de planejamento de regência por ano de turma."""
        ComponenteCurricular.objects.create(
            codigo=4,
            descricao="C4",
        )
        ComponenteCurricular.objects.create(
            codigo=9,
            descricao="C9",
        )
        ComponenteCurricular.objects.create(
            codigo=12,
            descricao="C12",
        )
        ComponenteCurricularPlanejamentoRegencia.objects.create(
            id_componente_curricular=12,
            ano=2024,
        )
        ComponenteCurricularPlanejamentoRegencia.objects.create(
            id_componente_curricular=9,
            ano=2025,
        )
        ComponenteCurricularPlanejamentoRegencia.objects.create(
            id_componente_curricular=4,
            ano=2024,
        )

        resultado = self.repo.listar_regencia_por_ano_turma(2024)

        self.assertEqual([item["codigo"] for item in resultado], [4, 12])
        self.assertEqual(resultado[0]["descricao"], "C4")
        self.assertEqual(resultado[1]["descricao"], "C12")

    def test_listar_regencia_ano_nulo(self) -> None:
        """Usa configuração padrão quando ano da turma é nulo."""
        ComponenteCurricular.objects.create(
            codigo=5,
            descricao="C5",
        )
        ComponenteCurricularPlanejamentoRegencia.objects.create(
            id_componente_curricular=5,
            ano=None,
        )

        resultado = self.repo.listar_regencia_por_ano_turma(0)

        self.assertEqual(resultado[0]["codigo"], 5)

    @patch("apps.componentes_curriculares.repository._raw")
    def test_turma_possui_componente_pap(self, mock_raw) -> None:
        """Verifica componente PAP associado à atribuição."""
        mock_raw.return_value = [{"possui": True}]

        self.assertTrue(self.repo.turma_possui_componente_pap("T1", "RF1"))

    @patch("apps.componentes_curriculares.repository._raw")
    def test_turma_nao_possui_componente_pap(self, mock_raw) -> None:
        """Verifica ausência de componente PAP na turma."""
        mock_raw.return_value = [{"possui": False}]

        self.assertFalse(self.repo.turma_possui_componente_pap("T1", "RF1"))

    @patch("apps.componentes_curriculares.repository._raw")
    def test_listar_por_ue_modalidade_ano_e_anos_escolares(
        self,
        mock_raw,
    ) -> None:
        """Monta filtro por UE, modalidade, ano e anos escolares."""
        mock_raw.return_value = [
            {
                "codigo_componente_curricular": 6,
                "codigo_componente_curricular_pai": 1,
                "descricao_componente_curricular": "Pai C1",
                "regencia": True,
            }
        ]

        resultado = self.repo.listar_por_ue_modalidade_ano_e_anos_escolares(
            "U1",
            5,
            2024,
            ["1"],
        )

        self.assertEqual(resultado[0]["codigo"], 6)
        self.assertEqual(resultado[0]["codigo_componente_curricular_pai"], 1)
        self.assertEqual(resultado[0]["descricao"], "Pai C1")
        self.assertTrue(resultado[0]["regencia"])
        self.assertFalse(resultado[0]["exibir_componente_eol"])
        self.assertIn("COALESCE(", mock_raw.call_args[0][0])
        self.assertIn("ccp.descricao", mock_raw.call_args[0][0])
        self.assertIn("ccp.regencia", mock_raw.call_args[0][0])
        self.assertIn(
            "cch.idcomponentecurricularpai", mock_raw.call_args[0][0]
        )
        self.assertIn(
            "t.codigo_modalidade_etapa = %s", mock_raw.call_args[0][0]
        )
        self.assertNotIn("t.tipo_turma != 4", mock_raw.call_args[0][0])
        self.assertIn("t.ano IN", mock_raw.call_args[0][0])
        self.assertEqual(mock_raw.call_args[0][1], ["U1", 5, 2024, "1"])

    @patch("apps.componentes_curriculares.repository._raw")
    def test_listar_turma_programa_modalidade_invalida(self, mock_raw) -> None:
        """Retorna lista vazia para modalidade inválida."""
        resultado = self.repo.listar_turma_programa_por_ue_modalidade_ano(
            "U1",
            99,
            2024,
        )

        self.assertEqual(resultado, [])
        mock_raw.assert_not_called()

    @patch("apps.componentes_curriculares.repository._raw")
    def test_listar_turma_programa_educacao_infantil(self, mock_raw) -> None:
        """Aplica filtro de série para educação infantil."""
        mock_raw.return_value = [
            {
                "codigo_componente_curricular": 1056,
                "codigo_componente_curricular_pai": None,
                "descricao_componente_curricular": "TIC",
                "regencia": False,
            },
            {
                "codigo_componente_curricular": 1030,
                "codigo_componente_curricular_pai": 1,
                "descricao_componente_curricular": "Pai C1",
                "regencia": True,
            }
        ]

        resultado = self.repo.listar_turma_programa_por_ue_modalidade_ano(
            "U1",
            1,
            2024,
        )

        self.assertEqual([item["codigo"] for item in resultado], [1030, 1056])
        self.assertEqual(resultado[0]["codigo_componente_curricular_pai"], 1)
        self.assertEqual(resultado[0]["descricao"], "Pai C1")
        self.assertTrue(resultado[0]["regencia"])
        self.assertIn("ccp.descricao", mock_raw.call_args[0][0])
        self.assertIn(
            "cch.idcomponentecurricularpai", mock_raw.call_args[0][0]
        )
        self.assertIn("t.tipo_turma != 4", mock_raw.call_args[0][0])
        self.assertIn("t.codigo_serie_ensino IN", mock_raw.call_args[0][0])

    @patch("apps.componentes_curriculares.repository._raw")
    def test_listar_por_ue_e_turmas(self, mock_raw) -> None:
        """Lista componentes simplificados por turmas."""
        mock_raw.return_value = [{"codigo": 8, "descricao": "Matemática"}]

        resultado = self.repo.listar_por_ue_e_turmas("U1", ["T8"])

        self.assertEqual(resultado, [{"codigo": 8, "descricao": "Matemática"}])
        self.assertIn("t.ue_codigo = %s", mock_raw.call_args[0][0])
        self.assertIn("ct.turma_codigo IN", mock_raw.call_args[0][0])
        self.assertEqual(mock_raw.call_args[0][1], ["U1", "T8"])

    @patch("apps.componentes_curriculares.repository._raw")
    def test_listar_por_ue_e_turmas_wildcard_ue(self, mock_raw) -> None:
        """Preserva wildcard de UE na listagem por turmas."""
        mock_raw.return_value = []

        resultado = self.repo.listar_por_ue_e_turmas("-99", [])

        self.assertEqual(resultado, [])
        self.assertNotIn("t.ue_codigo = %s", mock_raw.call_args[0][0])
        self.assertEqual(mock_raw.call_args[0][1], [])

    def test_listar_por_lista_turmas_vazio(self) -> None:
        """Retorna lista vazia quando não há turmas."""
        self.assertEqual(self.repo.listar_por_lista_turmas([]), [])

    @patch("apps.componentes_curriculares.repository._raw")
    def test_listar_por_lista_turmas_sem_planejamento(self, mock_raw) -> None:
        """Deduplica componentes por turma e código."""
        mock_raw.return_value = [
            {"turma_codigo": "T1", "codigo": 9},
            {"turma_codigo": "T1", "codigo": 9},
        ]

        resultado = self.repo.listar_por_lista_turmas(
            ["T1"],
            adicionar_componentes_planejamento=False,
        )

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["codigo"], 9)

    def test_listar_turmas_brutos_vazio(self) -> None:
        """Retorna lista vazia quando não há turmas."""
        self.assertEqual(self.repo.listar_turmas_brutos([]), [])

    @patch("apps.componentes_curriculares.repository._raw")
    def test_listar_turmas_brutos(self, mock_raw) -> None:
        """Retorna componentes sem professor."""
        mock_raw.return_value = [
            {
                "codigo": 10,
                "descricao": "C10",
                "codigo_componente_territorio_saber": None,
            }
        ]

        resultado = self.repo.listar_turmas_brutos(["T10"])

        self.assertIsNone(resultado[0]["professor"])
        self.assertEqual(resultado[0]["codigo"], 10)

    def test_listar_catalogo(self) -> None:
        """Lista catálogo ordenado por código."""
        ComponenteCurricular.objects.create(codigo=2, descricao="B")
        ComponenteCurricular.objects.create(codigo=1, descricao="A")

        resultado = self.repo.listar_catalogo()

        self.assertEqual(
            resultado,
            [
                {"codigo": 1, "descricao": "A"},
                {"codigo": 2, "descricao": "B"},
            ],
        )

    @patch("apps.componentes_curriculares.repository._raw")
    def test_listar_vigencia_componentes_vazio(self, mock_raw) -> None:
        """Retorna lista vazia sem componentes curriculares."""
        resultado = self.repo.listar_vigencia_componentes("U1", 2024, [], None)

        self.assertEqual(resultado, [])
        mock_raw.assert_not_called()

    @patch("apps.componentes_curriculares.repository._raw")
    def test_listar_vigencia_componentes_com_semestre(self, mock_raw) -> None:
        """Adiciona filtro de semestre quando informado."""
        mock_raw.return_value = []

        resultado = self.repo.listar_vigencia_componentes(
            "U1",
            2024,
            ["1"],
            2,
        )

        self.assertEqual(resultado, [])
        self.assertIn("AND t.semestre = %s", mock_raw.call_args[0][0])
        self.assertEqual(mock_raw.call_args[0][1], ["U1", 2024, 1, 2])

    def test_listar_grade_curricular(self) -> None:
        """Lista grade curricular por ano letivo."""
        GradeComponenteCurricular.objects.create(
            codigo_componente_curricular=1,
            descricao_componente_curricular="C1",
            codigo_ano_turma="1",
            descricao_serie_ensino="1º ano",
            codigo_serie_ensino=1,
            modalidade=5,
            ano_letivo=2024,
        )

        resultado = self.repo.listar_grade_curricular(2024)

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["codigo_componente_curricular"], 1)

    def test_listar_grade_curricular_preserva_ano_turma_do_etl(self) -> None:
        """Preserva o código de ano turma materializado pelo ETL."""
        GradeComponenteCurricular.objects.create(
            codigo_componente_curricular=1308,
            descricao_componente_curricular="REG CLASSE ESC PARTIC PRE",
            codigo_ano_turma="5",
            descricao_serie_ensino="5ºESC PARTIC PRE I",
            codigo_serie_ensino=313,
            modalidade=1,
            ano_letivo=2024,
        )
        GradeComponenteCurricular.objects.create(
            codigo_componente_curricular=1309,
            descricao_componente_curricular="REG CLASSE ESC PARTIC CRECHE",
            codigo_ano_turma="6",
            descricao_serie_ensino="6ºESC PARTIC PREII",
            codigo_serie_ensino=314,
            modalidade=1,
            ano_letivo=2024,
        )

        resultado = self.repo.listar_grade_curricular(2024)

        codigos_ano = {
            item["codigo_componente_curricular"]: item["codigo_ano_turma"]
            for item in resultado
        }
        self.assertEqual(codigos_ano[1308], "5")
        self.assertEqual(codigos_ano[1309], "6")

    @patch("apps.componentes_curriculares.repository._raw")
    def test_listar_componentes_sem_atribuicao(self, mock_raw) -> None:
        """Retorna descrições de componentes sem atribuição."""
        mock_raw.return_value = [{"descricao": "C17"}]

        resultado = self.repo.listar_componentes_sem_atribuicao("T17")

        self.assertEqual(resultado, ["C17"])
        mock_raw.assert_called_once()

    def test_listar_agrupamentos_correlacionados_sem_origem(self) -> None:
        """Retorna vazio quando agrupamento de origem não existe."""
        resultado = self.repo.listar_agrupamentos_correlacionados(999, None)

        self.assertEqual(resultado, [])

    def test_listar_agrupamentos_correlacionados_com_origem(self) -> None:
        """Retorna agrupamentos correlacionados da origem."""
        _make_agrupamento(
            cod_agrupamento=1001,
            cod_turma="T1",
            cod_territorio_saber=10,
            cod_componentes_curriculares="100,200,300",
        )
        _make_agrupamento(
            cod_agrupamento=1002,
            cod_turma="T1",
            cod_territorio_saber=10,
            cod_componentes_curriculares="100,200",
        )

        resultado = self.repo.listar_agrupamentos_correlacionados(1001, None)

        self.assertEqual([item["codigo"] for item in resultado], [1001, 1002])

    def test_listar_agrupamentos_correlacionados_com_data_base(self) -> None:
        """Aplica filtro de data base."""
        _make_agrupamento(
            cod_agrupamento=2001,
            dt_inicio_atribuicao=datetime(2024, 6, 1, tzinfo=UTC),
            cod_componentes_curriculares="50",
        )

        resultado = self.repo.listar_agrupamentos_correlacionados(
            2001,
            date(2024, 7, 1),
        )

        self.assertEqual(len(resultado), 1)

    def test_listar_agrupamentos_correlacionados_data_exclui(self) -> None:
        """Exclui agrupamento iniciado após a data base."""
        _make_agrupamento(
            cod_agrupamento=2002,
            dt_inicio_atribuicao=datetime(2024, 8, 1, tzinfo=UTC),
            cod_componentes_curriculares="50",
        )

        resultado = self.repo.listar_agrupamentos_correlacionados(
            2002,
            date(2024, 7, 1),
        )

        self.assertEqual(resultado, [])

    def test_listar_agrupamentos_correlacionados_lote(self) -> None:
        """Retorna agrupamentos correlacionados sem duplicar."""
        _make_agrupamento(
            cod_agrupamento=3001,
            cod_componentes_curriculares="70",
        )

        resultado = self.repo.listar_agrupamentos_correlacionados_lote(
            [3001, 3001],
            None,
        )

        self.assertEqual(len(resultado), 1)

    def test_listar_agrupamentos_correlacionados_lote_vazio(self) -> None:
        """Retorna vazio quando lista de códigos está vazia."""
        resultado = self.repo.listar_agrupamentos_correlacionados_lote(
            [], None
        )

        self.assertEqual(resultado, [])

    def test_listar_agrupamentos_territorio(self) -> None:
        """Retorna agrupamentos por IDs."""
        _make_agrupamento(
            cod_agrupamento=4001,
            cod_componentes_curriculares="80,90",
        )

        resultado = self.repo.listar_agrupamentos_territorio([4001])

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["codigo"], 4001)
        self.assertEqual(
            resultado[0]["codigos_territorios_agrupamento"], [80, 90]
        )

    def test_listar_agrupamentos_territorio_vazio(self) -> None:
        """Retorna vazio quando lista de IDs está vazia."""
        resultado = self.repo.listar_agrupamentos_territorio([])

        self.assertEqual(resultado, [])
