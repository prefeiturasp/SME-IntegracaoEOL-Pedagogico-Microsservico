"""Serializers do domínio Turmas."""

from rest_framework import serializers


class TurmaListSerializer(serializers.Serializer):
    """Contrato de lista de turmas (turmas-regulares, turmas-programa, listar-turmas)."""

    codigo = serializers.IntegerField()
    nome_turma = serializers.CharField()
    ano_letivo = serializers.IntegerField()
    ano = serializers.CharField(allow_null=True)
    tipo_turma = serializers.IntegerField()
    ue_codigo = serializers.CharField()
    modalidade = serializers.CharField(allow_null=True)
    codigo_modalidade = serializers.IntegerField(allow_null=True)
    semestre = serializers.IntegerField()
    ensino_especial = serializers.BooleanField()
    serie_ensino = serializers.CharField(allow_null=True)
    codigo_serie_ensino = serializers.IntegerField(allow_null=True)
    situacao = serializers.CharField(allow_null=True)
    extinta = serializers.BooleanField()


class TurmaDadosSerializer(serializers.Serializer):
    """Contrato canônico de dados da turma — GET {codigoTurma}/dados."""

    codigo = serializers.IntegerField()
    ano_letivo = serializers.IntegerField()
    ano = serializers.CharField(allow_null=True)
    tipo_turma = serializers.IntegerField()
    nome_turma = serializers.CharField()
    duracao_turno = serializers.IntegerField(allow_null=True)
    tipo_turno = serializers.IntegerField(allow_null=True)
    data_inicio_turma = serializers.DateTimeField(allow_null=True)
    data_fim = serializers.DateTimeField(allow_null=True)
    extinta = serializers.BooleanField()
    situacao = serializers.CharField(allow_null=True)
    ue_codigo = serializers.CharField()
    serie_ensino = serializers.CharField(allow_null=True)
    codigo_serie_ensino = serializers.IntegerField(allow_null=True)
    modalidade = serializers.CharField(allow_null=True)
    codigo_modalidade = serializers.IntegerField(allow_null=True)
    codigo_tipo_programa = serializers.IntegerField(allow_null=True)
    codigo_modalidade_etapa = serializers.IntegerField(allow_null=True)
    semestre = serializers.IntegerField()
    ensino_especial = serializers.BooleanField()
    data_atualizacao = serializers.DateTimeField(allow_null=True)
    data_status_turma_escola = serializers.DateTimeField(allow_null=True)


class TurmaSincronizacaoSerializer(serializers.Serializer):
    """Contrato de sincronizações institucionais da turma."""

    codigo = serializers.IntegerField()
    ue_codigo = serializers.CharField()
    ano_letivo = serializers.IntegerField()
    data_inicio_turma = serializers.DateTimeField(allow_null=True)
    data_fim = serializers.DateTimeField(allow_null=True)
    data_atualizacao = serializers.DateTimeField(allow_null=True)
    data_status_turma_escola = serializers.DateTimeField(allow_null=True)
    situacao = serializers.CharField(allow_null=True)
    extinta = serializers.BooleanField()
    codigo_modalidade = serializers.IntegerField(allow_null=True)
    modalidade = serializers.CharField(allow_null=True)
    semestre = serializers.IntegerField()
    ensino_especial = serializers.BooleanField()
    codigo_serie_ensino = serializers.IntegerField(allow_null=True)
    serie_ensino = serializers.CharField(allow_null=True)


class TurmaHistoricaSerializer(serializers.Serializer):
    """Contrato TurmaDTO — GET turmas-historicas-geral."""

    ano = serializers.CharField(allow_null=True)
    ano_letivo = serializers.IntegerField()
    codigo = serializers.IntegerField()
    tipo_turma = serializers.IntegerField()
    modalidade = serializers.CharField(allow_null=True)
    codigo_modalidade = serializers.IntegerField(allow_null=True)
    nome_turma = serializers.CharField(allow_null=True)
    semestre = serializers.IntegerField()
    duracao_turno = serializers.IntegerField()
    tipo_turno = serializers.IntegerField()
    data_fim = serializers.DateTimeField(allow_null=True)
    ehistorico = serializers.BooleanField()
    ensino_especial = serializers.BooleanField()
    etapa_eja = serializers.IntegerField()
    serie_ensino = serializers.CharField(allow_null=True)
    data_inicio_turma = serializers.DateTimeField(allow_null=True)
    extinta = serializers.BooleanField()
    situacao = serializers.CharField(allow_null=True)
    ue_codigo = serializers.CharField()


class TurmaItinerarioSerializer(serializers.Serializer):
    """Contrato de itinerário do Ensino Médio — GET itinerario/ensino-medio."""

    nome = serializers.CharField()
    serie = serializers.CharField()
