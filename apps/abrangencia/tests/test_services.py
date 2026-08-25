"""Testes dos serviços de abrangência."""

from unittest.mock import MagicMock

from django.test import SimpleTestCase

from apps.abrangencia.services import AbrangenciaService


class AbrangenciaServiceTest(SimpleTestCase):
    """Valida a orquestração das consultas de abrangência."""

    def test_delega_listagem_ao_repositorio(self) -> None:
        """Delega a consulta de ciclos ao repositório."""
        service = AbrangenciaService()
        service._repository = MagicMock()
        service._repository.listar_ciclos_ensino.return_value = ["ciclo"]

        resultado = service.listar_ciclos_ensino()

        self.assertEqual(resultado, ["ciclo"])
        service._repository.listar_ciclos_ensino.assert_called_once_with()
