"""Serializers do domínio de abrangência."""

from typing import Any

from django.utils import timezone
from rest_framework import serializers

from apps.abrangencia.models import CicloEnsino


class DataHoraLegadoField(serializers.DateTimeField):
    """Serializa data e hora no formato publicado pelo EOL."""

    def to_representation(self, value: Any) -> str:
        """Formata a data sem fuso e sem zeros fracionários excedentes.

        Args:
            value: Data e hora a ser serializada.

        Returns:
            Data e hora no formato ISO utilizado pelo contrato legado.
        """
        if timezone.is_aware(value):
            value = timezone.localtime(value)
        texto = value.replace(tzinfo=None).isoformat(timespec="microseconds")
        return texto.rstrip("0").rstrip(".")


class CicloEnsinoSerializer(serializers.ModelSerializer):
    """Serializa dados de ciclo de ensino."""

    codigoModalidadeEnsino = serializers.IntegerField(  # noqa: N815
        source="codigo_modalidade_ensino"
    )
    codigoEtapaEnsino = serializers.IntegerField(  # noqa: N815
        source="codigo_etapa_ensino"
    )
    dtAtualizacao = DataHoraLegadoField(  # noqa: N815
        source="data_atualizacao"
    )

    class Meta:
        model = CicloEnsino
        fields = (
            "codigoModalidadeEnsino",
            "codigoEtapaEnsino",
            "codigo",
            "descricao",
            "dtAtualizacao",
        )
