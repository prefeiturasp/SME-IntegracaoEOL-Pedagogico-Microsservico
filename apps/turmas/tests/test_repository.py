"""Testes do repository do dominio Turmas."""

from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase

from apps.componentes_curriculares.constants import (
    TIPO_TURMA_EVENTO_PARA_ATRIBUICAO,
    TIPO_TURMA_PROGRAMA,
    TIPO_TURMA_REGULAR,
)
from apps.turmas.repository import TurmasRepository


class FakeQuerySet:
    """QuerySet minimo para validação do repository."""

    def __init__(self, items=None, values=None):
        self.items = list(items or [])
        self.values = values or []
        self.calls = []
        self._values_mode = False

    def __iter__(self):
        return iter(self.values if self._values_mode else self.items)

    def filter(self, *args, **kwargs):
        self.calls.append(("filter", args, kwargs))
        return self

    def exclude(self, *args, **kwargs):
        self.calls.append(("exclude", args, kwargs))
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
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


class TestTurmasRepository(TestCase):
    """Valida consultas e mapeamentos do repository."""

    def setUp(self) -> None:
        self.repo = TurmasRepository()

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
    def test_turmas_recorte_filtra_codigos_e_etapa(self, mock_using):
        """Verifica se o filtro aplica tanto o código de turma quanto o recorte de etapa."""
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
    def test_sincronizacoes_mapeia_dados(self, mock_using):
        qs = FakeQuerySet([_turma(semestre=2)])
        mock_using.return_value = qs

        resultado = self.repo.sincronizacoes_institucionais(
            "000532", 2112345
        )

        self.assertEqual(resultado["ue_codigo"], "000532")
        self.assertEqual(resultado["semestre"], 2)
        self.assertEqual(
            qs.calls[0][2],
            {"ue_codigo": "000532", "codigo": 2112345},
        )

    @patch("apps.turmas.repository.Turma.objects.using")
    def test_anos_letivos_por_ue_ordena_e_exclui_evento(self, mock_using):
        qs = FakeQuerySet(values=[2023, 2024])
        mock_using.return_value = qs

        resultado = self.repo.anos_letivos_por_ue("000532")

        self.assertEqual(resultado, [2023, 2024])
        self.assertEqual(qs.calls[0][2], {"ue_codigo": "000532"})
        self.assertEqual(
            qs.calls[1][2],
            {"tipo_turma": TIPO_TURMA_EVENTO_PARA_ATRIBUICAO},
        )

    @patch("apps.turmas.repository.AtribuicaoComponente.objects.using")
    def test_turmas_historicas_professor_sem_codigos_validos(
        self, mock_atribuicao_using
    ):
        qs_atribuicao = FakeQuerySet(values=["", "abc", None])
        mock_atribuicao_using.return_value = qs_atribuicao

        self.assertEqual(
            self.repo.turmas_historicas_professor(2024, "RF1"),
            [],
        )

    @patch("apps.turmas.repository.Turma.objects.using")
    @patch("apps.turmas.repository.AtribuicaoComponente.objects.using")
    def test_turmas_historicas_professor_mapeia_historico(
        self, mock_atribuicao_using, mock_turma_using
    ):
        qs_atribuicao = FakeQuerySet(values=["2112345", "abc", "2112346"])
        qs_turma = FakeQuerySet(
            [
                _turma(
                    tipo_turma=None,
                    duracao_turno=None,
                    tipo_turno=None,
                    situacao="C",
                )
            ]
        )
        mock_atribuicao_using.return_value = qs_atribuicao
        mock_turma_using.return_value = qs_turma

        resultado = self.repo.turmas_historicas_professor(2024, "RF1")

        self.assertEqual(resultado[0]["codigo"], 2112345)
        self.assertEqual(resultado[0]["tipo_turma"], 0)
        self.assertEqual(resultado[0]["duracao_turno"], 0)
        self.assertTrue(resultado[0]["ehistorico"])
        self.assertEqual(qs_turma.calls[0][2], {"codigo__in": [2112345, 2112346]})

    @patch("apps.turmas.repository.TurmaItinerarioEnsinoMedio.objects.using")
    def test_itinerarios_ensino_medio_ordena_por_nome(self, mock_using):
        qs = FakeQuerySet(
            [
                SimpleNamespace(id=2, nome="B", serie="2"),
                SimpleNamespace(id=1, nome="A", serie="1"),
            ]
        )
        mock_using.return_value = qs

        resultado = self.repo.itinerarios_ensino_medio()

        self.assertEqual(resultado[0], {"id": 2, "nome": "B", "serie": "2"})
        self.assertEqual(qs.calls[0], ("order_by", ("nome",), {}))
