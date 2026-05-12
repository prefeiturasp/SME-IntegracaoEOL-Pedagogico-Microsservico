"""Serializers do domínio Turmas — definem o schema do Swagger.

Todos os campos usam camelCase para compatibilidade com o contrato
legado EOL/SGP. Os dicts retornados pelo repository já chegam em
camelCase, portanto não há mapeamento source aqui.
"""

from rest_framework import serializers


class TurmaListSerializer(serializers.Serializer):
    """Contrato de lista de turmas (turmas-regulares, turmas-programa, listar-turmas)."""

    codigo = serializers.IntegerField()
    nomeTurma = serializers.CharField()
    anoLetivo = serializers.IntegerField()
    ano = serializers.CharField(allow_null=True)
    tipoTurma = serializers.IntegerField()
    ueCodigo = serializers.CharField()
    modalidade = serializers.CharField(allow_null=True)
    codigoModalidade = serializers.IntegerField(allow_null=True)
    semestre = serializers.IntegerField()
    ensinoEspecial = serializers.BooleanField()
    serieEnsino = serializers.CharField(allow_null=True)
    codigoSerieEnsino = serializers.IntegerField(allow_null=True)
    situacao = serializers.CharField(allow_null=True)
    extinta = serializers.BooleanField()


class TurmaDadosSerializer(serializers.Serializer):
    """Contrato canônico de dados da turma — GET {codigoTurma}/dados."""

    codigo = serializers.IntegerField()
    anoLetivo = serializers.IntegerField()
    ano = serializers.CharField(allow_null=True)
    tipoTurma = serializers.IntegerField()
    nomeTurma = serializers.CharField()
    duracaoTurno = serializers.IntegerField(allow_null=True)
    tipoTurno = serializers.IntegerField(allow_null=True)
    dataInicioTurma = serializers.DateTimeField(allow_null=True)
    dataFim = serializers.DateTimeField(allow_null=True)
    extinta = serializers.BooleanField()
    situacao = serializers.CharField(allow_null=True)
    ueCodigo = serializers.CharField()
    serieEnsino = serializers.CharField(allow_null=True)
    codigoSerieEnsino = serializers.IntegerField(allow_null=True)
    modalidade = serializers.CharField(allow_null=True)
    codigoModalidade = serializers.IntegerField(allow_null=True)
    codigoTipoPrograma = serializers.IntegerField(allow_null=True)
    codigoModalidadeEtapa = serializers.IntegerField(allow_null=True)
    semestre = serializers.IntegerField()
    ensinoEspecial = serializers.BooleanField()
    dataAtualizacao = serializers.DateTimeField(allow_null=True)
    dataStatusTurmaEscola = serializers.DateTimeField(allow_null=True)


class TurmaSincronizacaoSerializer(serializers.Serializer):
    """Contrato de sincronizações institucionais da turma."""

    codigo = serializers.IntegerField()
    ueCodigo = serializers.CharField()
    anoLetivo = serializers.IntegerField()
    dataInicioTurma = serializers.DateTimeField(allow_null=True)
    dataFim = serializers.DateTimeField(allow_null=True)
    dataAtualizacao = serializers.DateTimeField(allow_null=True)
    dataStatusTurmaEscola = serializers.DateTimeField(allow_null=True)
    situacao = serializers.CharField(allow_null=True)
    extinta = serializers.BooleanField()
    codigoModalidade = serializers.IntegerField(allow_null=True)
    modalidade = serializers.CharField(allow_null=True)
    semestre = serializers.IntegerField()
    ensinoEspecial = serializers.BooleanField()
    codigoSerieEnsino = serializers.IntegerField(allow_null=True)
    serieEnsino = serializers.CharField(allow_null=True)


class TurmaHistoricaSerializer(serializers.Serializer):
    """Contrato TurmaDTO — GET turmas-historicas-geral."""

    ano = serializers.CharField(allow_null=True)
    anoLetivo = serializers.IntegerField()
    codigo = serializers.IntegerField()
    tipoTurma = serializers.IntegerField()
    modalidade = serializers.CharField(allow_null=True)
    codigoModalidade = serializers.IntegerField(allow_null=True)
    nomeTurma = serializers.CharField(allow_null=True)
    semestre = serializers.IntegerField()
    duracaoTurno = serializers.IntegerField()
    tipoTurno = serializers.IntegerField()
    dataFim = serializers.DateTimeField(allow_null=True)
    ehistorico = serializers.BooleanField()
    ensinoEspecial = serializers.BooleanField()
    etapaEJA = serializers.IntegerField()
    serieEnsino = serializers.CharField(allow_null=True)
    dataInicioTurma = serializers.DateTimeField(allow_null=True)
    extinta = serializers.BooleanField()
    situacao = serializers.CharField(allow_null=True)
    ueCodigo = serializers.CharField()


class TurmaItinerarioSerializer(serializers.Serializer):
    """Contrato de itinerário do Ensino Médio — GET itinerario/ensino-medio."""

    nome = serializers.CharField()
    serie = serializers.CharField()
