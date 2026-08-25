"""Serviços do domínio de abrangência."""

from django.db.models import QuerySet

from apps.abrangencia.models import CicloEnsino
from apps.abrangencia.repository import AbrangenciaRepository


class AbrangenciaService:
    """Orquestra as consultas de abrangência."""

    def __init__(self) -> None:
        self._repository = AbrangenciaRepository()

    def listar_ciclos_ensino(self) -> QuerySet[CicloEnsino]:
        """Lista os ciclos de ensino disponíveis."""
        return self._repository.listar_ciclos_ensino()
