"""Serializers do domínio Componentes Curriculares."""

from rest_framework import serializers


class ComponenteCurricularSerializer(serializers.Serializer):
    """Serializa dados completos de componente curricular."""

    codigo = serializers.IntegerField()
    codigo_componente_territorio_saber = serializers.IntegerField()
    codigo_componente_curricular_pai = serializers.IntegerField(
        allow_null=True
    )
    descricao = serializers.CharField()
    regencia = serializers.BooleanField()
    planejamento_regencia = serializers.BooleanField()
    territorio_saber = serializers.BooleanField()
    turma_codigo = serializers.CharField(allow_null=True)
    exibir_componente_eol = serializers.BooleanField()
    professor = serializers.CharField(allow_null=True)
    codigos_territorios_agrupamento = serializers.ListField(
        child=serializers.IntegerField(), default=list
    )


class ComponenteSimplificadoSerializer(serializers.Serializer):
    """Serializa dados simplificados de componente curricular."""

    codigo = serializers.IntegerField()
    descricao = serializers.CharField()


class ComponenteRegenciaSerializer(serializers.Serializer):
    """Serializa dados de componente de regência."""

    ano_turma = serializers.CharField(allow_null=True)
    ano_letivo = serializers.IntegerField()
    codigo = serializers.IntegerField()
    codigo_componente_territorio_saber = serializers.IntegerField()
    descricao = serializers.CharField()
    territorio_saber = serializers.BooleanField()
    tipo_escola = serializers.CharField(allow_null=True)
    turno_turma = serializers.IntegerField(allow_null=True)
    componente_planejamento_regencia = serializers.BooleanField()
    turma_codigo = serializers.CharField(allow_null=True)
    professor = serializers.CharField(allow_null=True)
    inicio_atribuicao = serializers.DateTimeField(allow_null=True)
    fim_atribuicao = serializers.DateTimeField(allow_null=True)


class VigenciaComponenteSerializer(serializers.Serializer):
    """Serializa dados de vigência de componente curricular."""

    componente_codigo = serializers.CharField()
    componente_descricao = serializers.CharField()
    turma_codigo = serializers.CharField()
    data_inicio_turma = serializers.DateTimeField(allow_null=True)


class GradeCurricularSerializer(serializers.Serializer):
    """Serializa dados de grade curricular."""

    codigo_componente_curricular = serializers.IntegerField()
    descricao_componente_curricular = serializers.CharField()
    codigo_ano_turma = serializers.CharField(allow_null=True)
    descricao_serie_ensino = serializers.CharField(allow_null=True)
    codigo_serie_ensino = serializers.IntegerField(allow_null=True)
    modalidade = serializers.IntegerField(allow_null=True)
