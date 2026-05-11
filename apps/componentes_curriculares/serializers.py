"""Serializers do domínio Componentes Curriculares."""
from rest_framework import serializers


class ComponenteCurricularSerializer(serializers.Serializer):
    """Contrato de resposta completo (EP-1, EP-4 a EP-8)."""

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
    """Contrato reduzido (EP-6, EP-9)."""

    codigo = serializers.IntegerField()
    descricao = serializers.CharField()


class ComponenteRegenciaSerializer(serializers.Serializer):
    """Contrato de resposta de regência (EP-2)."""

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
    """Contrato de resposta de vigência de componentes (EP-10)."""

    componente_codigo = serializers.CharField()
    componente_descricao = serializers.CharField()
    turma_codigo = serializers.CharField()
    data_inicio_turma = serializers.DateTimeField(allow_null=True)


class GradeCurricularSerializer(serializers.Serializer):
    """Contrato de resposta da grade curricular por ano letivo (EP-11)."""

    codigo_componente_curricular = serializers.IntegerField()
    descricao_componente_curricular = serializers.CharField()
    codigo_ano_turma = serializers.CharField(allow_null=True)
    descricao_serie_ensino = serializers.CharField(allow_null=True)
    codigo_serie_ensino = serializers.IntegerField(allow_null=True)
    modalidade = serializers.IntegerField(allow_null=True)
