"""Testes dos métodos __str__ dos models."""

from django.test import TestCase

from apps.componentes_curriculares.models import (
    AgrupamentoAtribuicaoTerritorioSaber,
    AtribuicaoComponente,
    ComponenteCurricular,
    ComponenteCurricularAgrupamento,
    ComponenteTurma,
    GradeComponenteCurricular,
)


class TestModelStr(TestCase):
    """Garante coverage para os métodos __str__ dos models."""

    def test_componente_curricular_str(self) -> None:
        """Garante formato correto para ComponenteCurricular."""
        obj = ComponenteCurricular(codigo=123, descricao="Matemática")

        self.assertEqual(str(obj), "123 - Matemática")

    def test_componente_turma_str(self) -> None:
        """Garante formato correto para ComponenteTurma."""
        obj = ComponenteTurma(componente_codigo=456, turma_codigo="T1")

        self.assertEqual(str(obj), "456 turma=T1")

    def test_atribuicao_componente_str(self) -> None:
        """Garante formato correto para AtribuicaoComponente."""
        obj = AtribuicaoComponente(
            componente_codigo=789,
            turma_codigo="T2",
            professor="RF123",
        )

        self.assertEqual(str(obj), "789 turma=T2 professor=RF123")

    def test_componente_curricular_agrupamento_str(self) -> None:
        """Garante formato correto para ComponenteCurricularAgrupamento."""
        obj = ComponenteCurricularAgrupamento(
            componente_codigo=789,
            turma_codigo="T2",
            codigo_agrupamento=999,
        )

        self.assertEqual(str(obj), "componente=789 turma=T2 agrupamento=999")

    def test_grade_componente_curricular_str(self) -> None:
        """Garante formato correto para GradeComponenteCurricular."""
        obj = GradeComponenteCurricular(
            codigo_componente_curricular=123,
            ano_letivo=2024,
            modalidade=1,
        )

        self.assertEqual(str(obj), "123 ano_letivo=2024 modalidade=1")

    def test_agrupamento_atribuicao_territorio_saber_str(self) -> None:
        """Garante formato correto para AgrupamentoAtribuicaoTerritorioSaber."""
        obj = AgrupamentoAtribuicaoTerritorioSaber(
            cod_agrupamento=333,
            cod_territorio_saber=444,
            ano_letivo=2024,
        )

        self.assertEqual(
            str(obj),
            "agrupamento=333 territorio=444 ano_letivo=2024",
        )
