"""Testes do repository do dominio Turmas."""

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

    @patch("apps.turmas.repository.AtribuicaoComponente.objects.using")
    @patch("apps.turmas.repository.ComponenteCurricular.objects.using")
    @patch("apps.turmas.repository.ComponenteTurma.objects.using")
    @patch(
        "apps.turmas.repository." "TurmaItinerarioEnsinoMedio.objects.using"
    )
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
            {"ue_codigo": "000532", "codigo": 2112345},
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
