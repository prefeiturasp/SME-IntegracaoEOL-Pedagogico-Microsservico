"""Consultas do domínio de abrangência."""

from django.db.models import QuerySet

from apps.abrangencia.models import CicloEnsino


class AbrangenciaRepository:
    """Consulta os dados de abrangência materializados pelo ETL."""

    def listar_ciclos_ensino(self) -> QuerySet[CicloEnsino]:
        """Lista os ciclos de ensino ordenados por código."""
        return CicloEnsino.objects.only(
            "codigo_modalidade_ensino",
            "codigo_etapa_ensino",
            "codigo",
            "descricao",
            "data_atualizacao",
        ).order_by("codigo")
