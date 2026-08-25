"""Modelos de leitura do domínio de abrangência."""

from django.db import models

from apps.core.models import ModeloBase


class CicloEnsino(ModeloBase):
    """Representa um ciclo de ensino do EOL."""

    codigo_modalidade_ensino = models.IntegerField()
    codigo_etapa_ensino = models.IntegerField()
    codigo = models.IntegerField(unique=True)
    descricao = models.CharField(max_length=300)
    data_atualizacao = models.DateTimeField()

    class Meta:
        db_table = "ciclo_ensino"
        managed = False

    def __str__(self) -> str:
        return f"{self.codigo} - {self.descricao}"
