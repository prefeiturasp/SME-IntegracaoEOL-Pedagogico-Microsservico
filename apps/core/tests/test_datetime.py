"""Testes do tratamento de data e hora compartilhado."""

from datetime import UTC, datetime

from django.test import SimpleTestCase

from apps.core.datetime import DataHoraLegadoField


class TestDataHoraLegadoField(SimpleTestCase):
    """Valida o formato de data e hora publicado pelo EOL."""

    def setUp(self) -> None:
        self.campo = DataHoraLegadoField()

    def test_converte_utc_para_horario_local_sem_fuso(self):
        valor = datetime(2025, 9, 12, 18, 53, 35, 473000, tzinfo=UTC)

        self.assertEqual(
            self.campo.to_representation(valor), "2025-09-12T15:53:35.473"
        )

    def test_remove_zeros_fracionarios_excedentes(self):
        valor = datetime(2025, 9, 11, 16, 9, 45, 300000, tzinfo=UTC)

        self.assertEqual(
            self.campo.to_representation(valor), "2025-09-11T13:09:45.3"
        )

    def test_omite_fracao_zerada(self):
        valor = datetime(2026, 2, 2, 3, tzinfo=UTC)

        self.assertEqual(
            self.campo.to_representation(valor), "2026-02-02T00:00:00"
        )

    def test_mantem_data_sem_fuso(self):
        valor = datetime(2026, 2, 2, 10, 30)

        self.assertEqual(
            self.campo.to_representation(valor), "2026-02-02T10:30:00"
        )
