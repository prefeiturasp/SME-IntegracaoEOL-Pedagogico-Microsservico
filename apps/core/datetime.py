"""Tratamento de data e hora compartilhado entre os domínios."""

from datetime import datetime, tzinfo
from functools import cached_property

from django.utils import timezone
from rest_framework import serializers


class DataHoraLegadoField(serializers.DateTimeField):
    """Serializa data e hora no formato publicado pelo EOL."""

    @cached_property
    def _fuso_local(self) -> tzinfo:
        return timezone.get_current_timezone()

    def to_representation(self, value: datetime) -> str:
        """Formata a data sem fuso e sem zeros excedentes.

        Args:
            value: Data e hora a ser serializada.

        Returns:
            Data e hora no formato ISO utilizado pelo contrato legado.
        """
        if value.tzinfo is not None:
            value = value.astimezone(self._fuso_local).replace(tzinfo=None)
        texto = value.isoformat(timespec="microseconds")
        return texto.rstrip("0").rstrip(".")
