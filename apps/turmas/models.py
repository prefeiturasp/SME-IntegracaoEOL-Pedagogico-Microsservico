"""Modelos de leitura do domínio Turmas.

Turma usa managed=False: tabela criada e gerenciada pelo ETL.
TurmaItinerarioEnsinoMedio é fixture local (managed=True).

AtribuicaoComponente vive em apps.componentes_curriculares.models e deve
ser importada de lá quando necessário no repository.
"""

from django.db import models

from apps.core.models import ModeloBase


class Turma(ModeloBase):
    """Dados cadastrais de uma turma no EOL.

    Fonte de verdade para todos os endpoints de turma. Campos derivados
    (modalidade, semestre, ensino_especial, extinta) chegam prontos pelo ETL
    e não devem ser recalculados no MS.

    Alimenta:
    - POST turmas-regulares       (tipo_turma=1)
    - POST turmas-programa        (tipo_turma=3 ou codigo_tipo_programa IS NOT NULL)
    - POST listar-turmas
    - GET  {codigoTurma}/dados
    - GET  /api/ues/{ue}/turmas/{cod}/sincronizacoes-institucionais
    - GET  ue/{ue}/sincronizacoes-institucionais/anosLetivos
    """

    codigo = models.BigIntegerField(unique=True)
    ano_letivo = models.IntegerField()
    ano = models.CharField(max_length=5, null=True, blank=True)
    tipo_turma = models.IntegerField()
    nome_turma = models.CharField(max_length=200)
    duracao_turno = models.IntegerField(null=True, blank=True)
    tipo_turno = models.IntegerField(null=True, blank=True)
    data_inicio_turma = models.DateTimeField(null=True, blank=True)
    data_fim = models.DateTimeField(null=True, blank=True)
    extinta = models.BooleanField(default=False)
    situacao = models.CharField(max_length=1, null=True, blank=True)
    ue_codigo = models.CharField(max_length=20)
    serie_ensino = models.CharField(max_length=200, null=True, blank=True)
    codigo_serie_ensino = models.IntegerField(null=True, blank=True)
    modalidade = models.CharField(max_length=50, null=True, blank=True)
    codigo_modalidade = models.IntegerField(null=True, blank=True)
    codigo_tipo_programa = models.IntegerField(null=True, blank=True)
    codigo_modalidade_etapa = models.IntegerField(null=True, blank=True)
    semestre = models.IntegerField(null=True, blank=True, default=0)
    ensino_especial = models.BooleanField(default=False)
    data_atualizacao = models.DateTimeField(null=True, blank=True)
    data_status_turma_escola = models.DateTimeField(null=True, blank=True)

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
    """Fixture local de itinerários do Ensino Médio.

    Não sincronizada pelo ETL — populada via fixture Django.
    Alimenta: GET itinerario/ensino-medio
    """

    nome = models.CharField(max_length=100)
    serie = models.CharField(max_length=10, blank=True, default="")

    class Meta:
        db_table = "turma_itinerario_ensino_medio"
        verbose_name = "itinerário ensino médio"
        verbose_name_plural = "itinerários ensino médio"
        ordering = ["nome"]

    def __str__(self) -> str:
        return str(self.nome)
