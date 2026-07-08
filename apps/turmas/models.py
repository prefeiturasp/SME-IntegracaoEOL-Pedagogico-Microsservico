"""Modelos de leitura do domínio Turmas."""

from django.db import models

from apps.core.models import ModeloBase


class Turma(ModeloBase):
    """Representa turma escolar do EOL."""

    codigo = models.BigIntegerField(unique=True)
    ano_letivo = models.IntegerField()
    ano = models.CharField(max_length=5, null=True, blank=True)  # NOSONAR
    tipo_turma = models.IntegerField()
    nome_turma = models.CharField(max_length=200)
    duracao_turno = models.IntegerField(null=True, blank=True)
    tipo_turno = models.IntegerField(null=True, blank=True)
    data_inicio_turma = models.DateTimeField(null=True, blank=True)
    data_fim = models.DateTimeField(null=True, blank=True)
    extinta = models.BooleanField(default=False)
    situacao = models.CharField(max_length=1, null=True, blank=True)  # NOSONAR
    ue_codigo = models.CharField(max_length=20)
    serie_ensino = models.CharField(
        max_length=200, null=True, blank=True  # NOSONAR
    )
    codigo_serie_ensino = models.IntegerField(null=True, blank=True)
    modalidade = models.CharField(
        max_length=50, null=True, blank=True  # NOSONAR
    )
    codigo_modalidade = models.IntegerField(null=True, blank=True)
    codigo_tipo_programa = models.IntegerField(null=True, blank=True)
    codigo_modalidade_etapa = models.IntegerField(null=True, blank=True)
    codigo_etapa_ensino = models.IntegerField(null=True, blank=True)
    codigo_ciclo_ensino = models.IntegerField(null=True, blank=True)
    semestre = models.IntegerField(null=True, blank=True, default=0)
    ensino_especial = models.BooleanField(default=False)
    data_atualizacao = models.DateTimeField(null=True, blank=True)
    data_status_turma_escola = models.DateTimeField(null=True, blank=True)
    tipo_escola = models.IntegerField(null=True, blank=True)
    codigo_grade_programa = models.IntegerField(null=True, blank=True)
    descricao_grade_programa = models.CharField(
        max_length=300, null=True, blank=True
    )
    tipo_grade_programa = models.IntegerField(default=0)

    class Meta:
        db_table = "turma"
        verbose_name = "turma"
        verbose_name_plural = "turmas"
        indexes = [
            models.Index(
                fields=["ue_codigo", "ano_letivo"], name="idx_turma_ue_ano"
            ),
            models.Index(fields=["tipo_turma"], name="idx_turma_tipo"),
            models.Index(fields=["ano_letivo"], name="idx_turma_ano_letivo"),
        ]

    def __str__(self) -> str:
        return f"{self.codigo} - {self.nome_turma}"


class TurmaItinerarioEnsinoMedio(models.Model):
    """Representa itinerário do Ensino Médio."""

    nome = models.CharField(max_length=100)
    serie = models.CharField(max_length=10, blank=True, default="")

    class Meta:
        db_table = "turma_itinerario_ensino_medio"
        verbose_name = "itinerário ensino médio"
        verbose_name_plural = "itinerários ensino médio"
        ordering = ["nome"]

    def __str__(self) -> str:
        return str(self.nome)


class TurmaAtribuidaDreUe(ModeloBase):
    """Representa turma consolidada por DRE e UE."""

    codigo_escola = models.CharField(max_length=6)
    codigo_turma = models.BigIntegerField()
    ano_letivo = models.IntegerField()
    modalidade = models.CharField(max_length=15, null=True, blank=True)
    semestre = models.IntegerField(null=True, blank=True)
    codigo_modalidade = models.IntegerField(null=True, blank=True)
    codigo_dre = models.CharField(max_length=6)
    dre = models.CharField(max_length=60, null=True, blank=True)
    dre_abreviacao = models.CharField(max_length=60, null=True, blank=True)
    ue = models.CharField(max_length=60, null=True, blank=True)
    ue_abreviacao = models.CharField(max_length=60, null=True, blank=True)
    nome_turma = models.CharField(max_length=15, null=True, blank=True)
    ano = models.CharField(max_length=18, null=True, blank=True)
    tipo_ue = models.CharField(max_length=25, null=True, blank=True)
    codigo_tipo_ue = models.IntegerField(null=True, blank=True)
    codigo_tipo_escola = models.IntegerField(null=True, blank=True)
    tipo_escola = models.CharField(max_length=12, null=True, blank=True)
    duracao_turno = models.IntegerField(null=True, blank=True)
    tipo_turno = models.IntegerField(null=True, blank=True)

    class Meta(ModeloBase.Meta):
        db_table = "turma_atribuida_dre_ue"
