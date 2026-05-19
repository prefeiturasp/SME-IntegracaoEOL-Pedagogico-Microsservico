"""Modelos de leitura do domínio Componentes Curriculares."""

from django.db import models

from apps.core.models import ModeloBase


class ComponenteCurricular(ModeloBase):
    """Representa componente curricular ativo do EOL."""

    codigo = models.IntegerField(unique=True)
    descricao = models.CharField(max_length=300)
    regencia = models.BooleanField(default=False)

    class Meta:
        db_table = "componente_curricular"
        verbose_name = "componente curricular"
        verbose_name_plural = "componentes curriculares"

    def __str__(self) -> str:
        return f"{self.codigo} - {self.descricao}"


class ComponenteTurma(ModeloBase):
    """Representa componente curricular vinculado a uma turma."""

    componente_codigo = models.IntegerField()
    codigo_componente_territorio_saber = models.IntegerField(null=True, blank=True)  # NOSONAR  # noqa: E501  # fmt: skip
    turma_codigo = models.CharField(max_length=20)

    class Meta:
        db_table = "componente_turma"
        verbose_name = "componente turma"
        verbose_name_plural = "componentes turma"
        constraints = [
            models.UniqueConstraint(
                fields=["turma_codigo", "componente_codigo"],
                name="uq_componente_turma",
            ),
        ]
        indexes = [
            models.Index(fields=["turma_codigo"], name="idx_ct_turma_codigo"),
            models.Index(
                fields=["componente_codigo"], name="idx_ct_componente_codigo"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.componente_codigo} turma={self.turma_codigo}"


class AtribuicaoComponente(ModeloBase):
    """Representa atribuição de professor a turma e componente."""

    turma_codigo = models.CharField(max_length=20)
    componente_codigo = models.IntegerField()
    professor = models.CharField(max_length=20, null=True, blank=True)  # NOSONAR  # noqa: E501  # fmt: skip
    atribuicao_externa = models.BooleanField()
    ano_letivo = models.IntegerField()

    class Meta:
        db_table = "atribuicao_componente"
        verbose_name = "atribuição de componente"
        verbose_name_plural = "atribuições de componente"
        constraints = [
            models.UniqueConstraint(
                fields=["turma_codigo", "componente_codigo", "professor"],
                name="uq_atribuicao_componente",
                nulls_distinct=False,
            ),
        ]
        indexes = [
            models.Index(fields=["turma_codigo"], name="idx_ac_turma_codigo"),
            models.Index(
                fields=["professor", "ano_letivo"], name="idx_ac_prof_ano"
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.componente_codigo} turma={self.turma_codigo}"
            f" professor={self.professor}"
        )


class ComponenteCurricularAgrupamento(ModeloBase):
    """Representa item de agrupamento de território do saber."""

    componente_codigo = models.IntegerField()
    turma_codigo = models.CharField(max_length=20)
    codigo_agrupamento = models.BigIntegerField()
    rf_professor = models.CharField(
        max_length=20, null=True, blank=True
    )  # NOSONAR
    ano_letivo = models.IntegerField()

    class Meta:
        db_table = "componente_curricular_agrupamento"
        verbose_name = "componente curricular agrupamento"
        verbose_name_plural = "componentes curriculares agrupamento"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "componente_codigo",
                    "turma_codigo",
                    "codigo_agrupamento",
                ],
                name="uq_componente_agrupamento",
            ),
        ]
        indexes = [
            models.Index(fields=["turma_codigo"], name="idx_cca_turma_codigo"),
            models.Index(
                fields=["componente_codigo"], name="idx_cca_componente_codigo"
            ),
        ]

    def __str__(self) -> str:
        return (
            f"componente={self.componente_codigo} "
            f"turma={self.turma_codigo} "
            f"agrupamento={self.codigo_agrupamento}"
        )


class GradeComponenteCurricular(ModeloBase):
    """Representa componente previsto na grade por série e modalidade."""

    codigo_componente_curricular = models.IntegerField()
    descricao_componente_curricular = models.CharField(max_length=300)
    codigo_ano_turma = models.CharField(max_length=10, null=True, blank=True)  # NOSONAR  # noqa: E501  # fmt: skip
    descricao_serie_ensino = models.CharField(max_length=200, null=True, blank=True)  # NOSONAR  # noqa: E501  # fmt: skip
    codigo_serie_ensino = models.IntegerField(null=True, blank=True)
    modalidade = models.IntegerField(null=True, blank=True)
    ano_letivo = models.IntegerField()

    class Meta:
        db_table = "grade_componente_curricular"
        verbose_name = "grade componente curricular"
        verbose_name_plural = "grades componente curricular"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "codigo_componente_curricular",
                    "ano_letivo",
                    "modalidade",
                    "codigo_ano_turma",
                    "codigo_serie_ensino",
                ],
                name="uq_grade_curricular_serie",
                nulls_distinct=False,
            ),
        ]
        indexes = [
            models.Index(
                fields=["ano_letivo", "modalidade"],
                name="idx_gcs_ano_letivo_modalidade",
            ),
            models.Index(
                fields=["codigo_ano_turma"], name="idx_gcs_codigo_ano_turma"
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.codigo_componente_curricular} "
            f"ano_letivo={self.ano_letivo} "
            f"modalidade={self.modalidade}"
        )


class AgrupamentoAtribuicaoTerritorioSaber(ModeloBase):
    """Representa agrupamento de território atribuído a professor."""

    cod_agrupamento = models.BigIntegerField(unique=True)
    cod_territorio_saber = models.IntegerField()
    cod_experiencia_pedagogica = models.IntegerField(null=True, blank=True)
    dt_inicio_atribuicao = models.DateTimeField()
    ano_atribuicao = models.IntegerField()
    dt_fim_atribuicao = models.DateTimeField(null=True, blank=True)
    dt_fim_turma = models.DateTimeField(null=True, blank=True)
    rf_professor = models.CharField(
        max_length=20, null=True, blank=True
    )  # NOSONAR
    cod_turma = models.CharField(
        max_length=20, null=True, blank=True
    )  # NOSONAR
    cod_componentes_curriculares = models.CharField(max_length=500, null=True, blank=True)  # NOSONAR  # noqa: E501  # fmt: skip
    ano_letivo = models.IntegerField()
    cod_motivo_disponibilizacao = models.IntegerField(null=True, blank=True)
    desc_territorio_saber = models.CharField(max_length=200, null=True, blank=True)  # NOSONAR  # noqa: E501  # fmt: skip
    desc_experiencia_pedagogica = models.CharField(max_length=200, null=True, blank=True)  # NOSONAR  # noqa: E501  # fmt: skip
    encerramento_atribuicao_agrupamento_atualizado = models.BooleanField(null=True, blank=True)  # NOSONAR  # noqa: E501  # fmt: skip

    class Meta:
        db_table = "agrupamento_atribuicao_territorio_saber"
        verbose_name = "agrupamento atribuição território saber"
        verbose_name_plural = "agrupamentos atribuição território saber"
        indexes = [
            models.Index(fields=["cod_turma"], name="idx_aats_cod_turma"),
            models.Index(
                fields=["rf_professor"], name="idx_aats_rf_professor"
            ),
            models.Index(fields=["ano_letivo"], name="idx_aats_ano_letivo"),
        ]

    def __str__(self) -> str:
        return (
            f"agrupamento={self.cod_agrupamento} "
            f"territorio={self.cod_territorio_saber} "
            f"ano_letivo={self.ano_letivo}"
        )


class ComponenteCurricularPlanejamentoRegencia(models.Model):
    """Representa componentes de planejamento de regência."""

    id_componente_curricular = models.IntegerField()
    turno = models.IntegerField(null=True, blank=True)
    ano = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "componente_curricular_planejamento_regencia"


class ComponenteCurricularHierarquia(models.Model):
    """Mapeia componentes filhos para seus componentes curriculares pais."""

    id_componente_curricular_pai = models.IntegerField(
        db_column="idcomponentecurricularpai"
    )
    id_componente_curricular = models.IntegerField(
        db_column="idcomponentecurricular"
    )
    vigencia = models.DateTimeField()

    class Meta:
        db_table = "componente_curricular_hierarquia"


class ComponenteCurricularPAP(models.Model):
    """Representa componente curricular PAP."""

    id_componente_curricular = models.IntegerField(unique=True)

    class Meta:
        db_table = "componente_curricular_pap"
