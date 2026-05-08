"""Testes dos métodos __str__ dos models."""
from django.test import TestCase

from apps.componentes_curriculares.models import (
    AgrupamentoAtribuicaoTerritorioSaber,
    ComponenteCurricular,
    ComponenteCurricularAgrupamento,
)


class TestModelStr(TestCase):
    """Garante 100% de coverage para os métodos __str__ dos models."""

    def test_componente_curricular_str(self) -> None:
        """Garante formato correto para ComponenteCurricular."""
        obj = ComponenteCurricular(codigo=123, descricao="Matemática")
        self.assertEqual(str(obj), "123 - Matemática")

    def test_componente_curricular_agrupamento_str(self) -> None:
        """Garante formato correto para ComponenteCurricularAgrupamento."""
        obj = ComponenteCurricularAgrupamento(
            componente_codigo=789, turma_codigo="T2", codigo_agrupamento=999
        )
        self.assertEqual(str(obj), "componente=789 turma=T2 agrupamento=999")

    def test_agrupamento_atribuicao_territorio_saber_str(self) -> None:
        """Garante formato correto para AgrupamentoAtribuicaoTerritorioSaber."""
        obj = AgrupamentoAtribuicaoTerritorioSaber(
            cod_agrupamento=333, cod_territorio_saber=444, ano_letivo=2024
        )
        self.assertEqual(
            str(obj), "agrupamento=333 territorio=444 ano_letivo=2024")
