"""Testes dos modelos de abrangência."""

from django.test import SimpleTestCase

from apps.abrangencia.models import CicloEnsino


class CicloEnsinoModelTest(SimpleTestCase):
    """Valida o modelo de ciclo de ensino."""

    def test_modelo_e_somente_leitura(self) -> None:
        """Mantém a tabela sob responsabilidade do ETL."""
        self.assertFalse(CicloEnsino._meta.managed)
        self.assertEqual(CicloEnsino._meta.db_table, "ciclo_ensino")

    def test_representacao_textual(self) -> None:
        """Representa o ciclo pelo código e pela descrição."""
        ciclo = CicloEnsino(codigo=3, descricao="Alfabetização")
        self.assertEqual(str(ciclo), "3 - Alfabetização")
