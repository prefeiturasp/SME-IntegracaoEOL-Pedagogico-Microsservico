"""Testes do repository do dominio Turmas."""

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase

from apps.componentes_curriculares.constants import (
    TIPO_TURMA_ED_FISICA,
    TIPO_TURMA_EVENTO_PARA_ATRIBUICAO,
    TIPO_TURMA_ITINERARIOS_2A_ANO,
    TIPO_TURMA_PROGRAMA,
    TIPO_TURMA_REGULAR,
)
from apps.turmas.repository import TurmasRepository, _nome_filtro


class FakeQuerySet:
    """QuerySet minimo para validação do repository."""

    def __init__(self, items=None, values=None, values_list_mode=False):
        self.items = list(items or [])
        self._data = values or []
        self.calls = []
        self._values_mode = values_list_mode

    def __iter__(self):
        return iter(self._data if self._values_mode else self.items)

    def filter(self, *args, **kwargs):
        self.calls.append(("filter", args, kwargs))
        return self

    def exclude(self, *args, **kwargs):
        self.calls.append(("exclude", args, kwargs))
        return self

    def values(self, *args, **kwargs):
        self.calls.append(("values", args, kwargs))
        if not self._data:
            self._data = [
                {campo: getattr(item, campo) for campo in args}
                for item in self.items
            ]
        self._values_mode = True
        return self

    def values_list(self, *args, **kwargs):
        self.calls.append(("values_list", args, kwargs))
        self._values_mode = True
        return self

    def distinct(self):
        self.calls.append(("distinct", (), {}))
        return self

    def order_by(self, *args):
        self.calls.append(("order_by", args, {}))
        return self

    def first(self):
        return self.items[0] if self.items else None

    def exists(self):
        return bool(self.items or self._data)


def _turma(**kwargs):
    defaults = {
        "codigo": 2112345,
        "nome_turma": "3A EF",
        "ano_letivo": 2024,
        "ano": "3",
        "tipo_turma": TIPO_TURMA_REGULAR,
        "ue_codigo": "000532",
        "modalidade": "Ensino Fundamental",
        "codigo_modalidade": 5,
        "semestre": None,
        "ensino_especial": False,
        "serie_ensino": "3 ano",
        "codigo_serie_ensino": 3,
        "situacao": "A",
        "extinta": False,
        "data_inicio_turma": None,
        "duracao_turno": None,
        "tipo_turno": None,
        "data_fim": None,
        "codigo_tipo_programa": None,
        "codigo_modalidade_etapa": None,
        "codigo_etapa_ensino": None,
        "codigo_ciclo_ensino": None,
        "data_atualizacao": None,
        "data_status_turma_escola": None,
        "tipo_escola": None,
        "codigo_grade_programa": None,
        "descricao_grade_programa": None,
        "tipo_grade_programa": 0,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _turma_atribuida(**kwargs):
    defaults = {
        "codigo_escola": "019362",
        "codigo_turma": 3011229,
        "ano_letivo": 2026,
        "modalidade": "Fundamental",
        "semestre": 0,
        "codigo_modalidade": 5,
        "codigo_dre": "108900",
        "dre": "DIRETORIA REGIONAL DE EDUCACAO PENHA",
        "dre_abreviacao": "P",
        "ue": "EMEF TESTE",
        "ue_abreviacao": "EMEF TESTE",
        "nome_turma": "5A",
        "ano": "5",
        "tipo_ue": "DIRETA",
        "codigo_tipo_ue": 1,
        "codigo_tipo_escola": 1,
        "tipo_escola": "EMEF",
        "duracao_turno": 6,
        "tipo_turno": 1,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


class TestTurmasRepository(TestCase):
    """Valida consultas e mapeamentos do repository."""

    def setUp(self) -> None:
        self.repo = TurmasRepository()

    def test_nome_filtro_prioriza_tipo_itinerario(self):
        itinerario = SimpleNamespace(
            id=6,
            serie=2,
            nome="Ciências da Natureza",
        )

        resultado = _nome_filtro(
            _turma(
                tipo_turma=6,
                descricao_grade_programa="Descrição ignorada",
            ),
            itinerario,
        )

        self.assertEqual(
            resultado,
            "3A EF - 2ª Série - Ciências da Natureza",
        )

    def test_nome_filtro_regular_magisterio(self):
        resultado = _nome_filtro(
            _turma(codigo_etapa_ensino=9, serie_ensino="4ª Série"),
            None,
        )

        self.assertEqual(resultado, "3A EF - 4ª Série - Magistério")

    def test_nome_filtro_educacao_fisica(self):
        resultado = _nome_filtro(
            _turma(tipo_turma=TIPO_TURMA_ED_FISICA),
            None,
        )

        self.assertEqual(resultado, "3A EF - Ed Física")

    def test_nome_filtro_programa_remove_espacos_da_descricao(self):
        resultado = _nome_filtro(
            _turma(
                tipo_turma=TIPO_TURMA_PROGRAMA,
                descricao_grade_programa="  Xadrez  ",
            ),
            None,
        )

        self.assertEqual(resultado, "3A EF - Xadrez")

    def test_nome_filtro_itinerario_segundo_ano_normaliza_descricao(self):
        resultado = _nome_filtro(
            _turma(
                tipo_turma=TIPO_TURMA_ITINERARIOS_2A_ANO,
                tipo_grade_programa=23,
                codigo_grade_programa=5149,
                descricao_grade_programa="Descrição original",
            ),
            None,
        )

        self.assertEqual(resultado, "3A EF - Humanas e Sociais")

    def test_nome_filtro_sem_descricao_usa_serie(self):
        resultado = _nome_filtro(
            _turma(descricao_grade_programa=None),
            None,
        )

        self.assertEqual(resultado, "3A EF - 3 ano")

    @patch("apps.turmas.repository.Turma.objects.using")
    def test_turmas_regulares_filtra_tipo_e_mapeia_lista(self, mock_using):
        qs = FakeQuerySet([_turma(duracao_turno=2, tipo_turno=1)])
        mock_using.return_value = qs

        resultado = self.repo.turmas_regulares([2112345])

        self.assertEqual(resultado[0]["codigo"], 2112345)
        self.assertEqual(resultado[0]["semestre"], 0)
        self.assertEqual(resultado[0]["duracao_turno"], 2)
        self.assertEqual(
            qs.calls[0],
            (
                "filter",
                (),
                {
                    "tipo_turma": TIPO_TURMA_REGULAR,
                    "codigo__in": [2112345],
                },
            ),
        )

    @patch("apps.turmas.repository.Turma.objects.using")
    def test_turmas_programa_filtra_tipo_programa(self, mock_using):
        qs = FakeQuerySet([_turma(tipo_turma=TIPO_TURMA_PROGRAMA)])
        mock_using.return_value = qs

        resultado = self.repo.turmas_programa([2112345])

        self.assertEqual(resultado[0]["tipo_turma"], TIPO_TURMA_PROGRAMA)
        self.assertEqual(qs.calls[0][2]["tipo_turma"], TIPO_TURMA_PROGRAMA)

    @patch("apps.turmas.repository.Turma.objects.using")
    def test_listar_turmas_filtra_codigos(self, mock_using):
        qs = FakeQuerySet([_turma()])
        mock_using.return_value = qs

        resultado = self.repo.listar_turmas([2112345])

        self.assertEqual(resultado[0]["nome_turma"], "3A EF")
        self.assertEqual(qs.calls[0][2], {"codigo__in": [2112345]})

    def test_turmas_atribuidas_dre_ue_sem_codigos_retorna_vazio(self):
        resultado = self.repo.turmas_atribuidas_dre_ue([])

        self.assertEqual(resultado, [])

    @patch("apps.turmas.repository.TurmaAtribuidaDreUe.objects.using")
    def test_turmas_atribuidas_dre_ue_filtra_e_mapeia(self, mock_using):
        qs = FakeQuerySet([_turma_atribuida()])
        mock_using.return_value = qs

        resultado = self.repo.turmas_atribuidas_dre_ue(["019362"])

        self.assertEqual(resultado[0]["codigo_escola"], "019362")
        self.assertEqual(resultado[0]["codigo_turma"], 3011229)
        self.assertEqual(resultado[0]["codigo_dre"], "108900")
        self.assertEqual(qs.calls[0][2], {"codigo_escola__in": ["019362"]})
        self.assertEqual(
            qs.calls[1],
            (
                "order_by",
                (
                    "codigo_dre",
                    "codigo_escola",
                    "ano_letivo",
                    "nome_turma",
                    "codigo_turma",
                ),
                {},
            ),
        )

    @patch("apps.turmas.repository.TurmaAtribuidaDreUe.objects.using")
    def test_todas_turmas_atribuidas_dre_ue_recorta_tipo_escola(
        self, mock_using
    ):
        from apps.turmas.repository import _TIPOS_ESCOLA_SGP

        qs = FakeQuerySet([_turma_atribuida()])
        mock_using.return_value = qs

        resultado = self.repo.todas_turmas_atribuidas_dre_ue()

        turma = resultado["dres"][0]["ues"][0]["turmas"][0]
        self.assertEqual(turma["codigo"], 3011229)
        self.assertEqual(resultado["dres"][0]["codigo"], "108900")
        self.assertEqual(
            qs.calls[0],
            ("filter", (), {"codigo_tipo_escola__in": _TIPOS_ESCOLA_SGP}),
        )

    @patch("apps.turmas.repository.Turma.objects.using")
    def test_turmas_recorte_filtra_codigos_e_etapa(self, mock_using):
        """Verifica filtro por código de turma e recorte de etapa."""
        from apps.turmas.repository import _ETAPAS_RECORTE_FUND_MEDIO_EJA

        qs = FakeQuerySet([_turma(codigo_etapa_ensino=4)])
        mock_using.return_value = qs

        resultado = self.repo.turmas_recorte_fund_medio_eja([2112345])

        self.assertEqual(resultado[0]["codigo"], 2112345)
        kwargs = qs.calls[0][2]
        self.assertEqual(kwargs["codigo__in"], [2112345])
        self.assertEqual(
            kwargs["codigo_etapa_ensino__in"],
            _ETAPAS_RECORTE_FUND_MEDIO_EJA,
        )

    @patch("apps.turmas.repository.Turma.objects.using")
    def test_recorte_por_tipo_aplica_filtros(self, mock_using):
        """Aplica tipo de turma, UE e semestre e devolve os códigos."""
        qs = FakeQuerySet(values=[2112345])
        mock_using.return_value = qs

        resultado = self.repo.turmas_recorte_por_tipo(
            [2112345, 9],
            tipos_turma=[1, 5],
            ue_codigo="000532",
            semestre=1,
        )

        self.assertEqual(resultado, [2112345])
        filtros = {
            chave: valor
            for nome, _args, kwargs in qs.calls
            if nome == "filter"
            for chave, valor in kwargs.items()
        }
        self.assertEqual(filtros["codigo__in"], [2112345, 9])
        self.assertEqual(filtros["tipo_turma__in"], [1, 5])
        self.assertEqual(filtros["ue_codigo"], "000532")
        self.assertEqual(filtros["codigo_tipo_periodicidade__in"], (1, 3))

    @patch("apps.turmas.repository.Turma.objects.using")
    def test_recorte_por_tipo_sem_filtros_opcionais(self, mock_using):
        """Sem tipo/UE/semestre aplica apenas o filtro de códigos."""
        qs = FakeQuerySet(values=[2112345])
        mock_using.return_value = qs

        resultado = self.repo.turmas_recorte_por_tipo([2112345])

        self.assertEqual(resultado, [2112345])
        filtros = [kwargs for nome, _a, kwargs in qs.calls if nome == "filter"]
        self.assertEqual(filtros, [{"codigo__in": [2112345]}])

    @patch("apps.turmas.repository.Turma.objects.using")
    def test_recorte_por_tipo_semestre_fora_do_mapa_nao_filtra(
        self, mock_using
    ):
        """Semestre sem periodicidade mapeada não aplica o filtro."""
        qs = FakeQuerySet(values=[2112345])
        mock_using.return_value = qs

        self.repo.turmas_recorte_por_tipo([2112345], semestre=9)

        filtros = [kwargs for nome, _a, kwargs in qs.calls if nome == "filter"]
        self.assertEqual(filtros, [{"codigo__in": [2112345]}])

    def test_recorte_por_tipo_sem_codigos_retorna_vazio(self):
        """Lista de códigos vazia curto-circuita sem consultar o banco."""
        self.assertEqual(self.repo.turmas_recorte_por_tipo([]), [])

    @patch("apps.turmas.repository.Turma.objects.using")
    def test_codigos_turmas_contagem_aplica_filtros(self, mock_using):
        """Aplica UEs, situação, tipo de escola, ano e modalidade."""
        qs = FakeQuerySet(values=[3011258])
        mock_using.return_value = qs

        resultado = self.repo.codigos_turmas_por_ano_modalidade_dre(
            ["019370", "108200"],
            ano_turma="1",
            codigo_modalidade=5,
            ano_letivo=2026,
        )

        self.assertEqual(resultado, [3011258])
        filtros = {
            chave: valor
            for nome, _args, kwargs in qs.calls
            if nome == "filter"
            for chave, valor in kwargs.items()
        }
        self.assertEqual(filtros["ue_codigo__in"], ["019370", "108200"])
        self.assertIn("O", filtros["situacao__in"])
        self.assertEqual(filtros["ano"], "1")
        self.assertEqual(filtros["codigo_modalidade"], 5)
        self.assertEqual(filtros["ano_letivo"], 2026)
        exclui = [kwargs for nome, _a, kwargs in qs.calls if nome == "exclude"]
        self.assertEqual(exclui, [{"tipo_turma": 4}])

    @patch("apps.turmas.repository.Turma.objects.using")
    def test_codigos_turmas_contagem_sem_filtros_opcionais(self, mock_using):
        """Sem ano/modalidade/ano_letivo aplica apenas o recorte base."""
        qs = FakeQuerySet(values=[3011258])
        mock_using.return_value = qs

        self.repo.codigos_turmas_por_ano_modalidade_dre(["019370"])

        filtros = {
            chave: valor
            for nome, _a, kwargs in qs.calls
            if nome == "filter"
            for chave, valor in kwargs.items()
        }
        self.assertNotIn("ano", filtros)
        self.assertNotIn("codigo_modalidade", filtros)

    def test_codigos_turmas_contagem_sem_ues_retorna_vazio(self):
        """Lista de UEs vazia curto-circuita sem consultar o banco."""
        self.assertEqual(
            self.repo.codigos_turmas_por_ano_modalidade_dre([]), []
        )

    @patch("apps.turmas.repository.Turma.objects.using")
    def test_dados_turma_retorna_none_quando_nao_encontrada(self, mock_using):
        mock_using.return_value = FakeQuerySet([])

        self.assertIsNone(self.repo.dados_turma(9999999))

    @patch("apps.turmas.repository.Turma.objects.using")
    def test_dados_turma_mapeia_dados(self, mock_using):
        qs = FakeQuerySet(
            [
                _turma(
                    data_fim="2024-12-20",
                    codigo_tipo_programa=1,
                    codigo_modalidade_etapa=2,
                    data_atualizacao="2024-01-01",
                    data_status_turma_escola="2024-01-02",
                )
            ]
        )
        mock_using.return_value = qs

        resultado = self.repo.dados_turma(2112345)

        self.assertEqual(resultado["codigo"], 2112345)
        self.assertEqual(resultado["data_fim"], "2024-12-20")
        self.assertEqual(resultado["codigo_tipo_programa"], 1)

    @patch("apps.turmas.repository.Turma.objects.using")
    def test_sincronizacoes_retorna_none_quando_nao_encontrada(
        self, mock_using
    ):
        mock_using.return_value = FakeQuerySet([])

        self.assertIsNone(
            self.repo.sincronizacoes_institucionais("000532", 9999999)
        )

    @patch("apps.turmas.repository.Turma.objects.using")
    def test_sincronizacoes_ignora_ue_e_filtra_so_por_codigo(self, mock_using):
        """Independente da UE informada, filtra a turma só pelo código."""
        qs_turma = FakeQuerySet([])
        mock_using.return_value = qs_turma

        self.repo.sincronizacoes_institucionais("000532", 2112345)

        filtros = [c for c in qs_turma.calls if c[0] == "filter"]
        self.assertEqual(filtros[0][2], {"codigo": 2112345})

    @patch("apps.turmas.repository.Turma.objects.using")
    def test_turmas_elegiveis_sem_turma_base_retorna_vazio(self, mock_turma):
        mock_turma.return_value = FakeQuerySet([])

        resultado = self.repo.turmas_elegiveis("1234567", 2112345, 138)

        self.assertEqual(resultado, [])

    @patch("apps.turmas.repository.Turma.objects.using")
    @patch("apps.turmas.repository.TurmaAtribuidaDreUe.objects.using")
    @patch("apps.turmas.repository.AtribuicaoComponente.objects.using")
    def test_turmas_elegiveis_regular_filtra_e_mapeia(
        self,
        mock_atribuicao,
        mock_turma_atribuida,
        mock_turma,
    ):
        turma_base = _turma(codigo=2112345, ano="5")
        turma_destino = _turma(codigo=2112346, nome_turma="5B", ano="5")
        turma_atribuida_base = _turma_atribuida(
            codigo_turma=2112345,
            semestre=1,
        )
        qs_base = FakeQuerySet([turma_base])
        qs_turmas = FakeQuerySet([turma_destino])
        qs_atribuicoes = FakeQuerySet(values=["2112346", "abc"])
        qs_turma_atribuida_base = FakeQuerySet([turma_atribuida_base])
        qs_turma_atribuida_destino = FakeQuerySet(values=[2112346])
        mock_turma.side_effect = [qs_base, qs_turmas]
        mock_turma_atribuida.side_effect = [
            qs_turma_atribuida_base,
            qs_turma_atribuida_destino,
        ]
        mock_atribuicao.return_value = qs_atribuicoes

        resultado = self.repo.turmas_elegiveis("1234567", 2112345, 138)

        self.assertEqual(
            resultado,
            [{"cod_turma": 2112346, "nome_turma": "5B"}],
        )
        self.assertEqual(qs_base.calls[0][2], {"codigo": 2112345})
        self.assertEqual(
            qs_atribuicoes.calls[0][2],
            {
                "professor": "1234567",
                "componente_codigo": 138,
                "ano_letivo": turma_base.ano_letivo,
                "dt_cancelamento__isnull": True,
            },
        )
        self.assertEqual(
            qs_atribuicoes.calls[1][2], {"turma_codigo": "2112345"}
        )
        self.assertEqual(
            qs_turma_atribuida_base.calls[0][2], {"codigo_turma": 2112345}
        )
        self.assertEqual(
            qs_turma_atribuida_destino.calls[0][2],
            {"codigo_turma__in": [2112346]},
        )
        self.assertEqual(
            qs_turma_atribuida_destino.calls[1][2],
            {"semestre": turma_atribuida_base.semestre},
        )
        self.assertEqual(
            qs_turmas.calls[0][2],
            {
                "codigo__in": [2112346],
                "ue_codigo": turma_base.ue_codigo,
                "ano_letivo": turma_base.ano_letivo,
                "codigo_etapa_ensino": turma_base.codigo_etapa_ensino,
                "situacao__in": ("A", "C", "O"),
                "tipo_escola__in": frozenset({1, 3, 4, 16}),
            },
        )
        self.assertEqual(qs_turmas.calls[1][2], {"ano": "5"})
        self.assertEqual(
            qs_turmas.calls[-1],
            ("order_by", ("nome_turma", "codigo"), {}),
        )

    @patch("apps.turmas.repository.Turma.objects.using")
    @patch("apps.turmas.repository.TurmaAtribuidaDreUe.objects.using")
    @patch("apps.turmas.repository.AtribuicaoComponente.objects.using")
    def test_turmas_elegiveis_programa_nao_filtra_ano(
        self,
        mock_atribuicao,
        mock_turma_atribuida,
        mock_turma,
    ):
        turma_base = _turma(tipo_turma=TIPO_TURMA_PROGRAMA)
        turma_atribuida_base = _turma_atribuida(
            codigo_turma=2112345,
            semestre=1,
        )
        qs_base = FakeQuerySet([turma_base])
        qs_turmas = FakeQuerySet([_turma(codigo=2112346, nome_turma="P1")])
        mock_turma.side_effect = [qs_base, qs_turmas]
        mock_turma_atribuida.side_effect = [
            FakeQuerySet([turma_atribuida_base]),
            FakeQuerySet(values=[2112346]),
        ]
        mock_atribuicao.return_value = FakeQuerySet(values=["2112346"])

        resultado = self.repo.turmas_elegiveis("1234567", 2112345, 138)

        self.assertEqual(resultado[0]["cod_turma"], 2112346)
        filtros_ano = [
            call for call in qs_turmas.calls if call[2] == {"ano": "3"}
        ]
        self.assertEqual(filtros_ano, [])

    @patch("apps.turmas.repository.Turma.objects.using")
    @patch("apps.turmas.repository.TurmaAtribuidaDreUe.objects.using")
    @patch("apps.turmas.repository.AtribuicaoComponente.objects.using")
    def test_turmas_elegiveis_sem_consolidacao_limita_atribuicao_inicial(
        self,
        mock_atribuicao,
        mock_turma_atribuida,
        mock_turma,
    ):
        turma_base = _turma(codigo=2112345, ano="5", semestre=0)
        turma_destino = _turma(codigo=2112346, nome_turma="5B", ano="5")
        qs_base = FakeQuerySet([turma_base])
        qs_turmas = FakeQuerySet([turma_destino])
        qs_atribuicoes = FakeQuerySet(values=["2112346"])
        qs_turma_atribuida_base = FakeQuerySet([])
        qs_turma_atribuida_destino = FakeQuerySet([])
        mock_turma.side_effect = [qs_base, qs_turmas]
        mock_turma_atribuida.side_effect = [
            qs_turma_atribuida_base,
            qs_turma_atribuida_destino,
        ]
        mock_atribuicao.return_value = qs_atribuicoes

        resultado = self.repo.turmas_elegiveis("1234567", 2112345, 138)

        self.assertEqual(
            resultado,
            [{"cod_turma": 2112346, "nome_turma": "5B"}],
        )
        self.assertEqual(
            qs_atribuicoes.calls[4][2],
            {"dt_atribuicao__lt": datetime(2024, 1, 1, tzinfo=UTC)},
        )
        self.assertEqual(
            qs_turmas.calls[0][2],
            {
                "codigo__in": [2112346],
                "ue_codigo": turma_base.ue_codigo,
                "ano_letivo": turma_base.ano_letivo,
                "codigo_etapa_ensino": turma_base.codigo_etapa_ensino,
                "situacao__in": ("A", "C", "O"),
                "semestre": turma_base.semestre,
            },
        )

    @patch("apps.turmas.repository.AtribuicaoComponente.objects.using")
    @patch("apps.turmas.repository.ComponenteCurricular.objects.using")
    @patch("apps.turmas.repository.ComponenteTurma.objects.using")
    @patch("apps.turmas.repository.TurmaItinerarioEnsinoMedio.objects.using")
    @patch("apps.turmas.repository.Turma.objects.using")
    def test_sincronizacoes_mapeia_contrato_legado(
        self,
        mock_turma_using,
        mock_itinerario_using,
        mock_ct_using,
        mock_cc_using,
        mock_ac_using,
    ):
        """Mapeia o contrato legado ampliado com componentes."""
        qs_turma = FakeQuerySet(
            [
                _turma(
                    semestre=2,
                    codigo_etapa_ensino=1,
                    codigo_ciclo_ensino=2,
                    tipo_escola=4,
                    codigo_grade_programa=10,
                    descricao_grade_programa="GRADE EMEI",
                    tipo_grade_programa=1,
                    data_fim="2026-12-20",
                )
            ]
        )
        qs_ct = FakeQuerySet(values=[512], values_list_mode=True)
        qs_cc = FakeQuerySet(values=[{"codigo": 512, "descricao": "ED.INF."}])
        qs_ac = FakeQuerySet(
            values=[
                {
                    "componente_codigo": 512,
                    "professor": "1234567",
                    "dt_disponibilizacao": "2026-02-01T00:00:00",
                }
            ]
        )
        mock_turma_using.return_value = qs_turma
        qs_itinerario = FakeQuerySet([])
        mock_itinerario_using.return_value = qs_itinerario
        mock_ct_using.return_value = qs_ct
        mock_cc_using.return_value = qs_cc
        mock_ac_using.return_value = qs_ac

        resultado = self.repo.sincronizacoes_institucionais("000532", 2112345)

        self.assertEqual(resultado["ue_codigo"], "000532")
        self.assertEqual(resultado["semestre"], 2)
        self.assertEqual(resultado["etapa_eja"], 0)
        self.assertEqual(resultado["etapa_ensino"], 1)
        self.assertEqual(resultado["ciclo_ensino"], 2)
        self.assertEqual(resultado["tipo_escola"], 4)
        self.assertEqual(resultado["codigo_grade_programa"], 10)
        self.assertEqual(resultado["descricao_grade_programa"], "GRADE EMEI")
        self.assertEqual(resultado["tipo_grade_programa"], 1)
        self.assertEqual(resultado["data_fim_turma"], "2026-12-20")
        self.assertEqual(resultado["nome_filtro"], "3A EF - 3 ano")
        self.assertEqual(
            resultado["componentes"],
            [
                {
                    "nome_componente_curricular": "ED.INF.",
                    "componente_curricular_codigo": 512,
                    "registro_funcional": "1234567",
                    "data_disponibizacao": "2026-02-01T00:00:00",
                }
            ],
        )
        self.assertEqual(
            qs_turma.calls[0][2],
            {"codigo": 2112345},
        )
        self.assertEqual(qs_ct.calls[0][2], {"turma_codigo": "2112345"})
        self.assertEqual(qs_ac.calls[0][2], {"turma_codigo": "2112345"})
        self.assertEqual(qs_itinerario.calls[0][2], {"id": TIPO_TURMA_REGULAR})

    @patch("apps.turmas.repository.AtribuicaoComponente.objects.using")
    @patch("apps.turmas.repository.ComponenteCurricular.objects.using")
    @patch("apps.turmas.repository.ComponenteTurma.objects.using")
    @patch("apps.turmas.repository.Turma.objects.using")
    def test_sincronizacoes_componente_sem_atribuicao(
        self, mock_turma_using, mock_ct_using, mock_cc_using, mock_ac_using
    ):
        """Componente sem atribuição vem com RF e data nulos."""
        qs_turma = FakeQuerySet([_turma()])
        qs_ct = FakeQuerySet(values=[512], values_list_mode=True)
        qs_cc = FakeQuerySet(values=[{"codigo": 512, "descricao": "ED.INF."}])
        qs_ac = FakeQuerySet(values=[])
        mock_turma_using.return_value = qs_turma
        mock_ct_using.return_value = qs_ct
        mock_cc_using.return_value = qs_cc
        mock_ac_using.return_value = qs_ac

        resultado = self.repo.sincronizacoes_institucionais("000532", 2112345)

        self.assertEqual(
            resultado["componentes"],
            [
                {
                    "nome_componente_curricular": "ED.INF.",
                    "componente_curricular_codigo": 512,
                    "registro_funcional": None,
                    "data_disponibizacao": None,
                }
            ],
        )
        self.assertEqual(resultado["tipo_grade_programa"], 0)
        self.assertEqual(resultado["etapa_ensino"], 0)
        self.assertEqual(resultado["ciclo_ensino"], 0)

    @patch("apps.turmas.repository.AtribuicaoComponente.objects.using")
    @patch("apps.turmas.repository.ComponenteCurricular.objects.using")
    @patch("apps.turmas.repository.ComponenteTurma.objects.using")
    @patch("apps.turmas.repository.Turma.objects.using")
    def test_sincronizacoes_multiplas_atribuicoes_geram_itens(
        self, mock_turma_using, mock_ct_using, mock_cc_using, mock_ac_using
    ):
        """Componente com vários professores gera um item por atribuição."""
        qs_turma = FakeQuerySet([_turma()])
        qs_ct = FakeQuerySet(values=[512], values_list_mode=True)
        qs_cc = FakeQuerySet(values=[{"codigo": 512, "descricao": "ED.INF."}])
        qs_ac = FakeQuerySet(
            values=[
                {
                    "componente_codigo": 512,
                    "professor": "1111111",
                    "dt_disponibilizacao": None,
                },
                {
                    "componente_codigo": 512,
                    "professor": "2222222",
                    "dt_disponibilizacao": None,
                },
            ]
        )
        mock_turma_using.return_value = qs_turma
        mock_ct_using.return_value = qs_ct
        mock_cc_using.return_value = qs_cc
        mock_ac_using.return_value = qs_ac

        resultado = self.repo.sincronizacoes_institucionais("000532", 2112345)

        self.assertEqual(len(resultado["componentes"]), 2)
        self.assertEqual(
            [c["registro_funcional"] for c in resultado["componentes"]],
            ["1111111", "2222222"],
        )

    @patch("apps.turmas.repository.AtribuicaoComponente.objects.using")
    @patch("apps.turmas.repository.ComponenteCurricular.objects.using")
    @patch("apps.turmas.repository.ComponenteTurma.objects.using")
    @patch("apps.turmas.repository.Turma.objects.using")
    def test_sincronizacoes_sem_componentes_e_serie_nula(
        self, mock_turma_using, mock_ct_using, mock_cc_using, mock_ac_using
    ):
        """Retorna lista vazia e nome_filtro só com nome_turma."""
        qs_turma = FakeQuerySet([_turma(serie_ensino=None)])
        qs_ct = FakeQuerySet(values=[], values_list_mode=True)
        qs_cc = FakeQuerySet(values=[])
        qs_ac = FakeQuerySet(values=[])
        mock_turma_using.return_value = qs_turma
        mock_ct_using.return_value = qs_ct
        mock_cc_using.return_value = qs_cc
        mock_ac_using.return_value = qs_ac

        resultado = self.repo.sincronizacoes_institucionais("000532", 2112345)

        self.assertEqual(resultado["componentes"], [])
        self.assertEqual(resultado["nome_filtro"], "3A EF - ")

    @patch("apps.turmas.repository.Turma.objects.using")
    def test_codigos_turmas_por_ue_sem_filtro_lista_todos(self, mock_using):
        """Sem anos letivos, lista todos os códigos da UE."""
        qs = FakeQuerySet(values=[3036225, 3036295, 3082921])
        mock_using.return_value = qs

        resultado = self.repo.codigos_turmas_por_ue("019437", None)

        self.assertEqual(resultado, [3036225, 3036295, 3082921])
        self.assertEqual(qs.calls[0][2], {"ue_codigo": "019437"})
        self.assertEqual(
            qs.calls[1][2],
            {"tipo_turma": TIPO_TURMA_EVENTO_PARA_ATRIBUICAO},
        )
        self.assertEqual(
            qs.calls[2], ("values_list", ("codigo",), {"flat": True})
        )
        self.assertEqual(qs.calls[-1], ("order_by", ("codigo",), {}))

    @patch("apps.turmas.repository.Turma.objects.using")
    def test_codigos_turmas_por_ue_filtra_anos_letivos(self, mock_using):
        """Com anos letivos, aplica filtro ano_letivo__in."""
        qs = FakeQuerySet(values=[3036225, 3082921])
        mock_using.return_value = qs

        resultado = self.repo.codigos_turmas_por_ue("019437", [2025, 2026])

        self.assertEqual(resultado, [3036225, 3082921])
        self.assertEqual(qs.calls[0][2], {"ue_codigo": "019437"})
        self.assertEqual(
            qs.calls[1][2],
            {"tipo_turma": TIPO_TURMA_EVENTO_PARA_ATRIBUICAO},
        )
        self.assertEqual(
            qs.calls[2][2],
            {"ano_letivo__in": [2025, 2026]},
        )

    @patch("apps.turmas.repository.Turma.objects.using")
    def test_codigos_turmas_por_ue_sem_turmas_retorna_vazio(self, mock_using):
        """UE sem turmas elegíveis retorna lista vazia."""
        qs = FakeQuerySet(values=[])
        mock_using.return_value = qs

        self.assertEqual(self.repo.codigos_turmas_por_ue("019437", None), [])

    @patch("apps.turmas.repository.AtribuicaoComponente.objects.using")
    def test_turmas_historicas_professor_sem_codigos_validos(
        self, mock_atribuicao_using
    ):
        qs_atribuicao = FakeQuerySet(values=[("", 1), ("abc", 2), (None, 3)])
        mock_atribuicao_using.return_value = qs_atribuicao

        self.assertEqual(
            self.repo.turmas_historicas_professor(2024, "RF1"),
            [],
        )
        self.assertEqual(
            qs_atribuicao.calls[0][2],
            {
                "professor": "RF1",
                "ano_letivo": 2024,
                "dt_cancelamento__isnull": True,
                "dt_disponibilizacao__isnull": False,
            },
        )

    @patch("apps.turmas.repository.Turma.objects.using")
    @patch("apps.turmas.repository.AtribuicaoComponente.objects.using")
    def test_turmas_historicas_professor_aplica_filtros_legados(
        self, mock_atribuicao_using, mock_turma_using
    ):
        qs_atribuicao = FakeQuerySet(
            values=[
                ("2112346", 100),
                ("2112345", 100),
                ("2112347", 101),
                ("abc", 102),
            ]
        )
        qs_turma = FakeQuerySet(
            [
                _turma(
                    codigo=2112345,
                    tipo_turma=1,
                    duracao_turno=8,
                    tipo_turno=6,
                    data_fim="2024-12-20",
                    ensino_especial=True,
                    serie_ensino="INFANTIL UNIFICADO",
                    data_inicio_turma="2024-02-05",
                    situacao="C",
                    ue_codigo="090751",
                )
            ]
        )
        mock_atribuicao_using.return_value = qs_atribuicao
        mock_turma_using.return_value = qs_turma

        resultado = self.repo.turmas_historicas_professor(2024, "RF1")

        self.assertEqual(
            resultado[0],
            {
                "ano": "3",
                "ano_letivo": 2024,
                "codigo": 2112345,
                "modalidade": "Ensino Fundamental",
                "codigo_modalidade": 5,
                "nome_turma": "3A EF",
                "semestre": 0,
            },
        )
        self.assertEqual(
            qs_atribuicao.calls[0][2],
            {
                "professor": "RF1",
                "ano_letivo": 2024,
                "dt_cancelamento__isnull": True,
                "dt_disponibilizacao__isnull": False,
            },
        )
        self.assertEqual(
            qs_turma.calls[0][2],
            {
                "codigo__in": [2112345, 2112347],
                "ano_letivo": 2024,
                "tipo_escola__in": (1, 2, 3, 4, 16, 28, 31),
                "codigo_etapa_ensino__in": (
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    10,
                    11,
                    12,
                    13,
                    14,
                    17,
                ),
            },
        )
        self.assertEqual(
            qs_atribuicao.calls[1],
            (
                "values_list",
                ("turma_codigo", "id_atribuicao_origem"),
                {},
            ),
        )
        self.assertEqual(qs_turma.calls[-1], ("distinct", (), {}))

    @patch("apps.turmas.repository.Turma.objects.using")
    @patch("apps.turmas.repository.AtribuicaoComponente.objects.using")
    def test_turmas_historicas_professor_inclui_codigo_sem_origem(
        self, mock_atribuicao_using, mock_turma_using
    ):
        """Atribuição sem origem mantém o código no filtro de turmas."""
        qs_atribuicao = FakeQuerySet(values=[("2112345", None)])
        qs_turma = FakeQuerySet([_turma(codigo=2112345)])
        mock_atribuicao_using.return_value = qs_atribuicao
        mock_turma_using.return_value = qs_turma

        resultado = self.repo.turmas_historicas_professor(2024, "RF1")

        self.assertEqual(resultado[0]["codigo"], 2112345)
        self.assertEqual(qs_turma.calls[0][2]["codigo__in"], [2112345])

    @patch("apps.turmas.repository.TurmaItinerarioEnsinoMedio.objects.using")
    def test_itinerarios_ensino_medio_ordena_por_id(self, mock_using):
        qs = FakeQuerySet(
            [
                SimpleNamespace(id=1, nome="B", serie="2"),
                SimpleNamespace(id=2, nome="A", serie="1"),
            ]
        )
        mock_using.return_value = qs

        resultado = self.repo.itinerarios_ensino_medio()

        self.assertEqual(resultado[0], {"id": 1, "nome": "B", "serie": "2"})
        self.assertEqual(qs.calls[0], ("order_by", ("id",), {}))
