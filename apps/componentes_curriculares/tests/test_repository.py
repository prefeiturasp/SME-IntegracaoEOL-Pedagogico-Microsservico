"""Testes de repository do domínio Componentes Curriculares."""
from datetime import UTC, date, datetime
from uuid import uuid4
from unittest.mock import patch

from django.test import TestCase

from apps.componentes_curriculares.models import (
    AgrupamentoAtribuicaoTerritorioSaber,
    AtribuicaoComponente,
    ComponenteCurricular,
    ComponenteCurricularPAP,
    ComponenteTurma,
    RegenciaComponenteCurricular,
    GradeComponenteCurricular
)
from apps.componentes_curriculares.repository import (
    ComponentesRepository,
    _agrupamento_para_dict,
    _grade_para_componente,
    _parse_csv,
)


def _make_ct(**kwargs) -> ComponenteTurma:
    """Cria ComponenteTurma com defaults."""
    defaults = {
        "componente_codigo": 1,
        "descricao": "Comp",
        "regencia": False,
        "planejamento_regencia": False,
        "territorio_saber": False,
        "turma_codigo": "T0",
        "ano_letivo": 2024,
    }
    defaults.update(kwargs)
    return ComponenteTurma.objects.create(**defaults)


def _make_ac(**kwargs) -> AtribuicaoComponente:
    """Cria AtribuicaoComponente com defaults."""
    defaults = {
        "turma_codigo": "T0",
        "componente_codigo": 1,
        "professor": None,
        "atribuicao_externa": False,
        "ano_letivo": 2024,
    }
    defaults.update(kwargs)
    return AtribuicaoComponente.objects.create(**defaults)


def _make_agrupamento(**kwargs) -> AgrupamentoAtribuicaoTerritorioSaber:
    """Cria AgrupamentoAtribuicaoTerritorioSaber com defaults."""
    defaults = {
        "cod_agrupamento": 9000,
        "cod_territorio_saber": 1,
        "dt_inicio_atribuicao": datetime(2024, 1, 1, tzinfo=UTC),
        "ano_atribuicao": 2024,
        "ano_letivo": 2024,
        "cod_componentes_curriculares": "100,200",
        "desc_territorio_saber": "TS",
        "desc_experiencia_pedagogica": "EP",
    }
    defaults.update(kwargs)
    return AgrupamentoAtribuicaoTerritorioSaber.objects.create(**defaults)


class TestHelpersRepository(TestCase):
    """Testes das funções auxiliares do repository."""

    def test_parse_csv_vazio(self) -> None:
        """_parse_csv retorna lista vazia para None e string vazia."""
        self.assertEqual(_parse_csv(None), [])
        self.assertEqual(_parse_csv(""), [])

    def test_parse_csv_valido(self) -> None:
        """_parse_csv converte CSV de inteiros corretamente."""
        self.assertEqual(_parse_csv("1,2,3"), [1, 2, 3])
        self.assertEqual(_parse_csv("100, 200 "), [100, 200])

    def test_parse_csv_ignora_nao_numericos(self) -> None:
        """_parse_csv ignora tokens não numéricos."""
        self.assertEqual(_parse_csv("1,abc,3"), [1, 3])

    def test_grade_para_componente_defaults(self) -> None:
        """_grade_para_componente preenche campos com defaults corretos."""
        row = {
            "codigo_componente_curricular": 138,
            "descricao_componente_curricular": "LP",
        }
        resultado = _grade_para_componente(row)
        self.assertEqual(resultado["codigo"], 138)
        self.assertFalse(resultado["regencia"])
        self.assertEqual(resultado["codigosTerritoriosAgrupamento"], [])
        self.assertTrue(resultado["exibir_componente_eol"])

    def test_agrupamento_para_dict_com_experiencia(self) -> None:
        """_agrupamento_para_dict formata descricao com experiencia."""
        ag = _make_agrupamento(
            cod_agrupamento=9999,
            desc_territorio_saber="TS X",
            desc_experiencia_pedagogica="EP Y",
            cod_componentes_curriculares="10,20",
        )
        d = _agrupamento_para_dict(ag)
        self.assertEqual(d["codigo"], 9999)
        self.assertEqual(d["descricao"], "TS X - EP Y")
        self.assertEqual(d["codigosTerritoriosAgrupamento"], [10, 20])
        self.assertTrue(d["territorio_saber"])

    def test_agrupamento_para_dict_sem_experiencia(self) -> None:
        """_agrupamento_para_dict usa apenas desc_territorio quando sem EP."""
        ag = _make_agrupamento(
            cod_agrupamento=9998,
            desc_territorio_saber="TS Z",
            desc_experiencia_pedagogica=None,
        )
        d = _agrupamento_para_dict(ag)
        self.assertEqual(d["descricao"], "TS Z")

    def test_agrupamento_para_dict_csv_vazio(self) -> None:
        """_agrupamento_para_dict retorna codigosTerritoriosAgrupamento vazio."""
        ag = _make_agrupamento(
            cod_agrupamento=9997,
            cod_componentes_curriculares=None,
        )
        d = _agrupamento_para_dict(ag)
        self.assertEqual(d["codigosTerritoriosAgrupamento"], [])
        self.assertEqual(d["codigo_componente_territorio_saber"], 0)


class TestComponentesRepository(TestCase):
    """Testes de integração do ComponentesRepository com SQLite in-memory."""

    def setUp(self) -> None:
        self.repo = ComponentesRepository()

    def test_listar_por_turma_funcionario(self) -> None:
        """EP-1: filtra por turma e login via JOIN componente_turma + atribuicao_componente."""
        _make_ct(componente_codigo=1, turma_codigo="T1")
        _make_ac(turma_codigo="T1", componente_codigo=1, professor="u1")
        res = self.repo.listar_por_turma_funcionario("T1", "u1")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["turma_codigo"], "T1")
        self.assertIn("codigosTerritoriosAgrupamento", res[0])

    def test_listar_por_funcionario(self) -> None:
        """EP-1: filtra componentes por login sem turma."""
        _make_ct(componente_codigo=2, turma_codigo="T2")
        _make_ac(turma_codigo="T2", componente_codigo=2, professor="f2")
        res = self.repo.listar_por_funcionario("f2")
        self.assertEqual(len(res), 1)

    def test_listar_planejamento_por_turma_funcionario(self) -> None:
        """EP-1: filtra planejamento_regencia=True."""
        _make_ct(
            componente_codigo=3,
            turma_codigo="T3",
            planejamento_regencia=True,
        )
        _make_ac(turma_codigo="T3", componente_codigo=3, professor="f3")
        res = self.repo.listar_planejamento_por_turma_funcionario("T3", "f3")
        self.assertEqual(len(res), 1)

    def test_listar_regencia_por_ano_turma(self) -> None:
        """EP-2: busca via RegenciaComponenteCurricular + ComponenteCurricular."""
        ComponenteCurricular.objects.create(codigo=4, descricao="C4")
        RegenciaComponenteCurricular.objects.create(
            id_componente_curricular=4, ano=2024
        )
        res = self.repo.listar_regencia_por_ano_turma(2024)
        self.assertEqual(len(res), 1)
        self.assertIsNone(res[0]["ano_turma"])
        self.assertEqual(res[0]["ano_letivo"], 0)

    def test_listar_regencia_ano_nulo(self) -> None:
        """EP-2: anoTurma <= 0 retorna componentes com ano IS NULL."""
        ComponenteCurricular.objects.create(codigo=5, descricao="C5")
        RegenciaComponenteCurricular.objects.create(
            id_componente_curricular=5, ano=None
        )
        res = self.repo.listar_regencia_por_ano_turma(0)
        self.assertTrue(any(r["codigo"] == 5 for r in res))

    def test_turma_possui_componente_pap_verdadeiro(self) -> None:
        """EP-3: retorna True quando existe componente PAP na turma."""
        _make_ct(componente_codigo=10, turma_codigo="T10")
        _make_ac(turma_codigo="T10", componente_codigo=10, professor="f10")
        ComponenteCurricularPAP.objects.create(id_componente_curricular=10)
        self.assertTrue(self.repo.turma_possui_componente_pap("T10", "f10"))

    def test_turma_possui_componente_pap_falso(self) -> None:
        """EP-3: retorna False quando não há componente PAP."""
        _make_ct(componente_codigo=11, turma_codigo="T11")
        _make_ac(turma_codigo="T11", componente_codigo=11, professor="f11")
        self.assertFalse(self.repo.turma_possui_componente_pap("T11", "f11"))

    def test_listar_por_ue_modalidade_anos_escolares(self) -> None:
        """EP-4: filtra GradeComponenteCurricular por modalidade, ano e séries."""
        GradeComponenteCurricular.objects.create(
            codigo_componente_curricular=6,
            descricao_componente_curricular="C6",
            modalidade=5,
            ano_letivo=2024,
            codigo_ano_turma="1",
        )
        res = self.repo.listar_por_ue_modalidade_ano_e_anos_escolares(
            5, 2024, ["1"]
        )
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["codigo"], 6)
        self.assertFalse(res[0]["regencia"])

    def test_listar_por_ue_modalidade_anos_escolares_sem_filtro(self) -> None:
        """EP-4: sem anos_escolares retorna todos da grade."""
        GradeComponenteCurricular.objects.create(
            codigo_componente_curricular=60,
            descricao_componente_curricular="C60",
            modalidade=5,
            ano_letivo=2025,
        )
        res = self.repo.listar_por_ue_modalidade_ano_e_anos_escolares(
            5, 2025, []
        )
        self.assertEqual(len(res), 1)

    def test_listar_turma_programa(self) -> None:
        """EP-5: replica filtro especial de series apenas para EI."""
        with patch("apps.componentes_curriculares.repository._raw") as mock_raw:
            mock_raw.return_value = []
            res = self.repo.listar_turma_programa_por_ue_modalidade_ano(
                "1", 1, 2024
            )
        self.assertEqual(res, [])
        sql = mock_raw.call_args[0][0]
        params = mock_raw.call_args[0][1]
        self.assertIn("t.codigo_tipo_programa IS NOT NULL", sql)
        self.assertIn("ct.codigo_serie_ensino IN", sql)
        self.assertNotIn("t.codigo_modalidade_etapa IN", sql)
        self.assertNotIn("t.tipo_turma = 3", sql)
        self.assertEqual(params[:2], ["1", 2024])

    def test_listar_turma_programa_nao_filtra_series_para_fundamental(self) -> None:
        """EP-5: modalidades diferentes de EI não filtram codigo_serie_ensino."""
        with patch("apps.componentes_curriculares.repository._raw") as mock_raw:
            mock_raw.return_value = []
            res = self.repo.listar_turma_programa_por_ue_modalidade_ano(
                "1", 5, 2024
            )
        self.assertEqual(res, [])
        sql = mock_raw.call_args[0][0]
        self.assertNotIn("ct.codigo_serie_ensino IN", sql)
        self.assertNotIn("t.codigo_modalidade_etapa IN", sql)

    def test_listar_por_ue_e_turmas(self) -> None:
        """EP-6: filtra por turma, exclui componente_codigo=0, ordena por descricao."""
        _make_ct(componente_codigo=8, descricao="Matematica", turma_codigo="T8")
        _make_ct(componente_codigo=0, descricao="Zero", turma_codigo="T8")
        res = self.repo.listar_por_ue_e_turmas(["T8"])
        codigos = [r["codigo"] for r in res]
        self.assertIn(8, codigos)
        self.assertNotIn(0, codigos)

    def test_listar_por_lista_turmas(self) -> None:
        """EP-7: retorna componentes de múltiplas turmas via LEFT JOIN."""
        _make_ct(componente_codigo=9, turma_codigo="T9",
                 planejamento_regencia=True)
        res = self.repo.listar_por_lista_turmas(["T9"])
        self.assertEqual(len(res), 1)

    def test_listar_por_lista_turmas_deduplica_multiplos_professores(self) -> None:
        """EP-7: dois professores no mesmo componente/turma resulta em uma linha."""
        _make_ct(componente_codigo=91, turma_codigo="T91")
        _make_ac(turma_codigo="T91", componente_codigo=91, professor="pA")
        _make_ac(turma_codigo="T91", componente_codigo=91, professor="pB")
        res = self.repo.listar_por_lista_turmas(["T91"])
        self.assertEqual(len(res), 1)

    def test_listar_turmas_brutos(self) -> None:
        """EP-8: retorna componentes sem pós-processamento, professor=None."""
        _make_ct(componente_codigo=10, turma_codigo="T10b")
        res = self.repo.listar_turmas_brutos(["T10b"])
        self.assertEqual(len(res), 1)
        self.assertIsNone(res[0]["professor"])

    def test_listar_catalogo(self) -> None:
        """EP-9: retorna catálogo ordenado por codigo."""
        ComponenteCurricular.objects.create(codigo=100, descricao="CC100")
        res = self.repo.listar_catalogo()
        self.assertTrue(any(r["codigo"] == 100 for r in res))

    def test_listar_componentes_sem_atribuicao(self) -> None:
        """EP-12: retorna componentes sem linha em atribuicao_componente."""
        _make_ct(componente_codigo=17, descricao="C17", turma_codigo="T17")
        res = self.repo.listar_componentes_sem_atribuicao("T17")
        self.assertIn("C17", res)

    def test_listar_componentes_sem_atribuicao_exclui_com_professor(self) -> None:
        """EP-12: componente com atribuição não aparece no resultado."""
        _make_ct(componente_codigo=171, descricao="C171", turma_codigo="T171")
        _make_ac(turma_codigo="T171", componente_codigo=171, professor="pX")
        res = self.repo.listar_componentes_sem_atribuicao("T171")
        self.assertNotIn("C171", res)

    def test_listar_componentes_sem_atribuicao_turma_vazia(self) -> None:
        """EP-12: turma sem componentes retorna lista vazia."""
        res = self.repo.listar_componentes_sem_atribuicao("T_INEXISTENTE")
        self.assertEqual(res, [])

    def test_listar_agrupamentos_correlacionados_sem_origem(self) -> None:
        """EP-13: retorna [] quando cod_agrupamento não existe."""
        res = self.repo.listar_agrupamentos_correlacionados(99999, None)
        self.assertEqual(res, [])

    def test_listar_agrupamentos_correlacionados_com_origem(self) -> None:
        """EP-13: encontra agrupamentos que são subset da origem."""
        _make_agrupamento(
            cod_agrupamento=1001,
            cod_turma="T_AG",
            cod_territorio_saber=10,
            cod_componentes_curriculares="100,200,300",
        )
        _make_agrupamento(
            cod_agrupamento=1002,
            cod_turma="T_AG",
            cod_territorio_saber=10,
            cod_componentes_curriculares="100,200",
        )
        res = self.repo.listar_agrupamentos_correlacionados(1001, None)
        codigos = [r["codigo"] for r in res]
        self.assertIn(1001, codigos)
        self.assertIn(1002, codigos)

    def test_listar_agrupamentos_correlacionados_com_data_base(self) -> None:
        """EP-13: aplica filtro de data quando fornecido."""
        _make_agrupamento(
            cod_agrupamento=2001,
            cod_turma="T_DB",
            cod_territorio_saber=20,
            cod_componentes_curriculares="50",
            dt_inicio_atribuicao=datetime(2024, 6, 1, tzinfo=UTC),
        )
        res = self.repo.listar_agrupamentos_correlacionados(
            2001, date(2024, 7, 1)
        )
        self.assertEqual(len(res), 1)

    def test_listar_agrupamentos_correlacionados_data_exclui(self) -> None:
        """EP-13: data_base anterior ao início exclui o agrupamento."""
        _make_agrupamento(
            cod_agrupamento=2002,
            cod_turma="T_EX",
            cod_territorio_saber=21,
            cod_componentes_curriculares="51",
            dt_inicio_atribuicao=datetime(2024, 8, 1, tzinfo=UTC),
        )
        res = self.repo.listar_agrupamentos_correlacionados(
            2002, date(2024, 7, 1)
        )
        self.assertEqual(res, [])

    def test_listar_agrupamentos_correlacionados_lote(self) -> None:
        """EP-14: retorna agrupamentos de múltiplos IDs sem duplicatas."""
        _make_agrupamento(
            cod_agrupamento=3001,
            cod_turma="T_L",
            cod_territorio_saber=30,
            cod_componentes_curriculares="70",
        )
        res = self.repo.listar_agrupamentos_correlacionados_lote(
            [3001], None
        )
        self.assertEqual(len(res), 1)

    def test_listar_agrupamentos_correlacionados_lote_vazio(self) -> None:
        """EP-14: lista vazia retorna []."""
        res = self.repo.listar_agrupamentos_correlacionados_lote([], None)
        self.assertEqual(res, [])

    def test_listar_agrupamentos_territorio(self) -> None:
        """EP-15: retorna agrupamentos por IDs com CSV parsed."""
        _make_agrupamento(
            cod_agrupamento=4001,
            cod_componentes_curriculares="80,90",
        )
        res = self.repo.listar_agrupamentos_territorio([4001])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["codigo"], 4001)
        self.assertEqual(res[0]["codigosTerritoriosAgrupamento"], [80, 90])

    def test_listar_agrupamentos_territorio_vazio(self) -> None:
        """EP-15: lista vazia retorna []."""
        res = self.repo.listar_agrupamentos_territorio([])
        self.assertEqual(res, [])

    def test_listar_agrupamentos_territorio_deduplica(self) -> None:
        """EP-15: IDs duplicados na consulta retornam apenas um registro."""
        _make_agrupamento(
            cod_agrupamento=5001,
            cod_componentes_curriculares="99",
        )
        res = self.repo.listar_agrupamentos_territorio([5001, 5001])
        self.assertEqual(len(res), 1)
