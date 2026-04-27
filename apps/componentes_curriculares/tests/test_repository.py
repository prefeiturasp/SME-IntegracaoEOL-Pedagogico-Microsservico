"""Testes de repository do domínio Componentes Curriculares."""
from datetime import UTC, date, datetime
from uuid import uuid4

from django.test import TestCase

from apps.componentes_curriculares.models import (
    AgrupamentoAtribuicaoTerritorioSaber,
    ComponenteCurricular,
    ComponenteCurricularPAP,
    ComponenteCurricularPorTurma,
    ComponenteInicioTurma,
    GradeCurricularSerie,
    RegenciaComponenteCurricular,
)
from apps.componentes_curriculares.repository import (
    ComponentesRepository,
    _agrupamento_para_dict,
    _grade_para_componente,
    _parse_csv,
)


def _make_ccpt(**kwargs) -> ComponenteCurricularPorTurma:
    """Cria ComponenteCurricularPorTurma com defaults."""
    defaults = {
        "codigo": 1,
        "descricao": "Comp",
        "regencia": False,
        "planejamento_regencia": False,
        "territorio_saber": False,
        "exibir_componente_eol": True,
        "ano_letivo": 2024,
    }
    defaults.update(kwargs)
    return ComponenteCurricularPorTurma.objects.create(**defaults)


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
        """EP-1: filtra por turma e login."""
        _make_ccpt(codigo=1, turma_codigo="T1", professor="u1")
        res = self.repo.listar_por_turma_funcionario("T1", "u1")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["turma_codigo"], "T1")
        self.assertIn("codigosTerritoriosAgrupamento", res[0])

    def test_listar_por_funcionario(self) -> None:
        """EP-1: filtra componentes por login sem turma."""
        _make_ccpt(codigo=2, turma_codigo="T2", professor="f2")
        res = self.repo.listar_por_funcionario("f2")
        self.assertEqual(len(res), 1)

    def test_listar_planejamento_por_turma_funcionario(self) -> None:
        """EP-1: filtra planejamento_regencia=True."""
        _make_ccpt(
            codigo=3,
            turma_codigo="T3",
            professor="f3",
            planejamento_regencia=True,
        )
        res = self.repo.listar_planejamento_por_turma_funcionario(
            "T3", "f3"
        )
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
        _make_ccpt(codigo=10, turma_codigo="T10", professor="f10")
        ComponenteCurricularPAP.objects.create(id_componente_curricular=10)
        self.assertTrue(
            self.repo.turma_possui_componente_pap("T10", "f10")
        )

    def test_turma_possui_componente_pap_falso(self) -> None:
        """EP-3: retorna False quando não há componente PAP."""
        _make_ccpt(codigo=11, turma_codigo="T11", professor="f11")
        self.assertFalse(
            self.repo.turma_possui_componente_pap(
                "T11", "f11"
            )
        )

    def test_listar_por_ue_modalidade_anos_escolares(self) -> None:
        """EP-4: filtra GradeCurricularSerie por modalidade, ano e séries."""
        GradeCurricularSerie.objects.create(
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
        GradeCurricularSerie.objects.create(
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
        """EP-5: filtra GradeCurricularSerie por modalidade e ano."""
        GradeCurricularSerie.objects.create(
            codigo_componente_curricular=7,
            descricao_componente_curricular="C7",
            modalidade=1,
            ano_letivo=2024,
        )
        res = self.repo.listar_turma_programa_por_ue_modalidade_ano(
            1, 2024
        )
        self.assertEqual(len(res), 1)

    def test_listar_por_ue_e_turmas(self) -> None:
        """EP-6: filtra por turma, exclui codigo=0, ordena por descricao."""
        _make_ccpt(codigo=8, descricao="Matematica", turma_codigo="T8")
        _make_ccpt(codigo=0, descricao="Zero", turma_codigo="T8")
        res = self.repo.listar_por_ue_e_turmas(["T8"])
        codigos = [r["codigo"] for r in res]
        self.assertIn(8, codigos)
        self.assertNotIn(0, codigos)

    def test_listar_por_lista_turmas(self) -> None:
        """EP-7: filtra componentes de múltiplas turmas."""
        _make_ccpt(codigo=9, turma_codigo="T9", planejamento_regencia=True)
        res = self.repo.listar_por_lista_turmas(["T9"])
        self.assertEqual(len(res), 1)

    def test_listar_turmas_brutos(self) -> None:
        """EP-8: retorna componentes sem pós-processamento."""
        _make_ccpt(codigo=10, turma_codigo="T10b")
        res = self.repo.listar_turmas_brutos(["T10b"])
        self.assertEqual(len(res), 1)

    def test_listar_catalogo(self) -> None:
        """EP-9: retorna catálogo ordenado por codigo."""
        ComponenteCurricular.objects.create(codigo=100, descricao="CC100")
        res = self.repo.listar_catalogo()
        self.assertTrue(any(r["codigo"] == 100 for r in res))

    def test_listar_vigencia_componentes_com_semestre(self) -> None:
        """EP-10: filtra por UE, ano, componentes e semestre."""
        ComponenteInicioTurma.objects.create(
            componente_codigo="12",
            componente_descricao="C12",
            turma_codigo="T12",
            ue_codigo="U12",
            ano_letivo=2024,
            tipo_periodicidade=1,
            data_inicio_turma=datetime(2024, 2, 1, tzinfo=UTC),
        )
        res = self.repo.listar_vigencia_componentes("U12", 2024, ["12"], 1)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["componente_codigo"], "12")

    def test_listar_vigencia_componentes_sem_semestre(self) -> None:
        """EP-10: sem semestre não aplica filtro de periodicidade."""
        ComponenteInicioTurma.objects.create(
            componente_codigo="13",
            componente_descricao="C13",
            turma_codigo="T13",
            ue_codigo="U13",
            ano_letivo=2024,
        )
        res = self.repo.listar_vigencia_componentes("U13", 2024, ["13"], None)
        self.assertEqual(len(res), 1)

    def test_listar_grade_curricular(self) -> None:
        """EP-11: retorna grade curricular por ano letivo."""
        GradeCurricularSerie.objects.create(
            codigo_componente_curricular=16,
            descricao_componente_curricular="C16",
            codigo_ano_turma="1",
            descricao_serie_ensino="S1",
            codigo_serie_ensino=1,
            modalidade=5,
            ano_letivo=2026,
        )
        res = self.repo.listar_grade_curricular(2026)
        self.assertEqual(len(res), 1)
        self.assertIn("codigo_componente_curricular", res[0])

    def test_listar_componentes_sem_atribuicao(self) -> None:
        """EP-12: retorna descrições onde professor IS NULL."""
        _make_ccpt(
            codigo=17, descricao="C17", turma_codigo="T17", professor=None
        )
        res = self.repo.listar_componentes_sem_atribuicao(
            "T17"
        )
        self.assertIn("C17", res)

    def test_listar_componentes_sem_atribuicao_data_none(self) -> None:
        """EP-12: funciona com data_base=None."""
        _make_ccpt(
            codigo=170, descricao="C170", turma_codigo="T170", professor=None
        )
        res = self.repo.listar_componentes_sem_atribuicao("T170")
        self.assertIn("C170", res)

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
