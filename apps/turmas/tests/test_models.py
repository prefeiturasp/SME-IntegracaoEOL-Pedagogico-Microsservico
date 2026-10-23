"""Testes dos modelos do dominio Turmas."""

from django.test import TestCase

from apps.turmas.models import (
    EtapaEnsino,
    Turma,
    TurmaItinerarioEnsinoMedio,
)


class TestModelStr(TestCase):
    """Valida representacoes dos textos dos modelos."""

    def test_turma_str(self) -> None:
        """Valida formato textual da turma."""
        turma = Turma(codigo=123, nome_turma="3A EF")

        self.assertEqual(str(turma), "123 - 3A EF")

    def test_etapa_ensino_str(self) -> None:
        """Valida formato textual da etapa de ensino."""
        etapa = EtapaEnsino(codigo=5, descricao="Fundamental")

        self.assertEqual(str(etapa), "5 - Fundamental")

    def test_turma_itinerario_ensino_medio_str(self) -> None:
        """Valida formato textual do itinerario."""
        itinerario = TurmaItinerarioEnsinoMedio(nome="Ciencias da Natureza")

        self.assertEqual(str(itinerario), "Ciencias da Natureza")
