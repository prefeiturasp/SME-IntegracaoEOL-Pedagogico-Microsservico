"""Testes das regras puras do domínio Turmas."""

from django.test import SimpleTestCase

from apps.turmas.regras import ciclo_eja


class TestCicloEja(SimpleTestCase):
    """Valida a identificação do ciclo EJA pela descrição da série."""

    def test_marcador_primeiro_ciclo_retorna_um(self):
        self.assertEqual(ciclo_eja("EJA I - Ciclo"), 1)

    def test_sufixo_primeiro_ciclo_retorna_um(self):
        self.assertEqual(ciclo_eja("EJA MODULAR I"), 1)

    def test_marcador_segundo_ciclo_retorna_dois(self):
        self.assertEqual(ciclo_eja("EJA II - Ciclo"), 2)

    def test_sufixo_segundo_ciclo_retorna_dois(self):
        self.assertEqual(ciclo_eja("EJA MODULAR II"), 2)

    def test_ambos_os_marcadores_retorna_zero(self):
        self.assertEqual(ciclo_eja("EJA I E II"), 0)

    def test_sem_marcador_retorna_zero(self):
        self.assertEqual(ciclo_eja("EJA COMPLEMENTAR"), 0)

    def test_serie_ausente_retorna_zero(self):
        self.assertEqual(ciclo_eja(None), 0)

    def test_serie_curta_retorna_zero(self):
        self.assertEqual(ciclo_eja("I"), 0)
