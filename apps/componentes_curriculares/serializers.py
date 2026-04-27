"""Serializers do domínio Componentes Curriculares."""
from rest_framework import serializers


class ComponenteCurricularSerializer(serializers.Serializer):
    """Contrato de resposta completo (EP-1, EP-4 a EP-8)."""

    codigo = serializers.IntegerField()
    codigoComponenteTerritorioSaber = serializers.IntegerField(
        source="codigo_componente_territorio_saber"
    )
    codigoComponenteCurricularPai = serializers.IntegerField(
        source="codigo_componente_curricular_pai", allow_null=True
    )
    descricao = serializers.CharField()
    regencia = serializers.BooleanField()
    planejamentoRegencia = serializers.BooleanField(
        source="planejamento_regencia"
    )
    territorioSaber = serializers.BooleanField(source="territorio_saber")
    turmaCodigo = serializers.CharField(
        source="turma_codigo", allow_null=True
    )
    exibirComponenteEOL = serializers.BooleanField(
        source="exibir_componente_eol"
    )
    professor = serializers.CharField(allow_null=True)
    codigosTerritoriosAgrupamento = serializers.ListField(
        child=serializers.IntegerField(), default=list
    )


class ComponenteSimplificadoSerializer(serializers.Serializer):
    """Contrato reduzido (EP-6, EP-9)."""

    codigo = serializers.IntegerField()
    descricao = serializers.CharField()


class ComponenteRegenciaSerializer(serializers.Serializer):
    """Contrato de resposta de regência (EP-2)."""

    anoTurma = serializers.CharField(source="ano_turma", allow_null=True)
    anoLetivo = serializers.IntegerField(source="ano_letivo")
    codigo = serializers.IntegerField()
    codigoComponenteTerritorioSaber = serializers.IntegerField(
        source="codigo_componente_territorio_saber"
    )
    descricao = serializers.CharField()
    territorioSaber = serializers.BooleanField(source="territorio_saber")
    tipoEscola = serializers.CharField(
        source="tipo_escola", allow_null=True
    )
    turnoTurma = serializers.IntegerField(
        source="turno_turma", allow_null=True
    )
    componentePlanejamentoRegencia = serializers.BooleanField(
        source="componente_planejamento_regencia"
    )
    turmaCodigo = serializers.CharField(
        source="turma_codigo", allow_null=True
    )
    professor = serializers.CharField(allow_null=True)
    inicioAtribuicao = serializers.DateTimeField(
        source="inicio_atribuicao", allow_null=True
    )
    fimAtribuicao = serializers.DateTimeField(
        source="fim_atribuicao", allow_null=True
    )


class VigenciaComponenteSerializer(serializers.Serializer):
    """Contrato de resposta de vigência de componentes (EP-10)."""

    componenteCurricularCodigo = serializers.CharField(
        source="componente_codigo"
    )
    componenteCurricularDescricao = serializers.CharField(
        source="componente_descricao"
    )
    turmaCodigo = serializers.CharField(source="turma_codigo")
    dataInicioTurma = serializers.DateTimeField(
        source="data_inicio_turma", allow_null=True
    )


class GradeCurricularSerializer(serializers.Serializer):
    """Contrato de resposta da grade curricular por ano letivo (EP-11)."""

    codigoComponenteCurricular = serializers.IntegerField(
        source="codigo_componente_curricular"
    )
    descricaoComponenteCurricular = serializers.CharField(
        source="descricao_componente_curricular"
    )
    codigoAnoTurma = serializers.CharField(
        source="codigo_ano_turma", allow_null=True
    )
    descricaoSerieEnsino = serializers.CharField(
        source="descricao_serie_ensino", allow_null=True
    )
    codigoSerieEnsino = serializers.IntegerField(
        source="codigo_serie_ensino", allow_null=True
    )
    modalidade = serializers.IntegerField(allow_null=True)
