"""Serializers do domínio Turmas."""

from typing import Any, cast

from django.http import QueryDict
from rest_framework import serializers


class TurmaListSerializer(serializers.Serializer):
    """Serializa dados resumidos de turma."""

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
    tipo_turno = serializers.IntegerField(allow_null=True)
    codigo_etapa_ensino = serializers.IntegerField(allow_null=True)
    codigo_ciclo_ensino = serializers.IntegerField(allow_null=True)


class TurmaAtribuidaDreUeSerializer(serializers.Serializer):
    """Serializa turma atribuída por DRE e UE."""

    codigo_escola = serializers.CharField()
    codigo_turma = serializers.IntegerField()
    ano_letivo = serializers.IntegerField()
    modalidade = serializers.CharField(allow_null=True)
    semestre = serializers.IntegerField(allow_null=True)
    codigo_modalidade = serializers.IntegerField(allow_null=True)
    codigo_dre = serializers.CharField()
    dre = serializers.CharField(allow_null=True)
    dre_abreviacao = serializers.CharField(allow_null=True)
    ue = serializers.CharField(allow_null=True)
    ue_abreviacao = serializers.CharField(allow_null=True)
    nome_turma = serializers.CharField(allow_null=True)
    ano = serializers.CharField(allow_null=True)
    tipo_ue = serializers.CharField(allow_null=True)
    codigo_tipo_ue = serializers.IntegerField(allow_null=True)
    codigo_tipo_escola = serializers.IntegerField(allow_null=True)
    tipo_escola = serializers.CharField(allow_null=True)
    duracao_turno = serializers.IntegerField(allow_null=True)
    tipo_turno = serializers.IntegerField(allow_null=True)


class TurmasElegiveisRequestSerializer(serializers.Serializer):
    """Valida filtros de turmas elegíveis."""

    codigo_rf = serializers.CharField()
    codigo_turma = serializers.IntegerField()
    componente_curricular = serializers.IntegerField()


class TurmaElegivelSerializer(serializers.Serializer):
    """Serializa turma elegível."""

    cod_turma = serializers.IntegerField()
    nome_turma = serializers.CharField()


class TurmaDadosSerializer(serializers.Serializer):
    """Serializa dados cadastrais de turma."""

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


class TurmaComponenteSincronizacaoSerializer(serializers.Serializer):
    """Serializa componente curricular vinculado à turma."""

    nome_componente_curricular = serializers.CharField(allow_null=True)
    componente_curricular_codigo = serializers.IntegerField()
    registro_funcional = serializers.CharField(allow_null=True)
    data_disponibizacao = serializers.DateTimeField(allow_null=True)


class TurmaSincronizacaoSerializer(serializers.Serializer):
    """Serializa dados de sincronização institucional da turma."""

    ano = serializers.CharField(allow_null=True)
    ano_letivo = serializers.IntegerField()
    codigo = serializers.IntegerField()
    tipo_turma = serializers.IntegerField(allow_null=True)
    modalidade = serializers.CharField(allow_null=True)
    codigo_modalidade = serializers.IntegerField(allow_null=True)
    nome_turma = serializers.CharField()
    semestre = serializers.IntegerField()
    duracao_turno = serializers.IntegerField(allow_null=True)
    tipo_turno = serializers.IntegerField(allow_null=True)
    data_fim_turma = serializers.DateTimeField(allow_null=True)
    ensino_especial = serializers.BooleanField()
    etapa_eja = serializers.IntegerField()
    serie_ensino = serializers.CharField(allow_null=True)
    codigo_serie_ensino = serializers.IntegerField(allow_null=True)
    data_inicio_turma = serializers.DateTimeField(allow_null=True)
    extinta = serializers.BooleanField()
    situacao = serializers.CharField(allow_null=True)
    ue_codigo = serializers.CharField()
    data_atualizacao = serializers.DateTimeField(allow_null=True)
    data_status_turma_escola = serializers.DateTimeField(allow_null=True)
    etapa_ensino = serializers.IntegerField()
    ciclo_ensino = serializers.IntegerField()
    tipo_escola = serializers.IntegerField(allow_null=True)
    descricao_grade_programa = serializers.CharField(allow_null=True)
    tipo_grade_programa = serializers.IntegerField()
    codigo_grade_programa = serializers.IntegerField(allow_null=True)
    nome_filtro = serializers.CharField(allow_null=True)
    componentes = TurmaComponenteSincronizacaoSerializer(many=True)


class TurmaHistoricaSerializer(serializers.Serializer):
    """Serializa dados históricos de turma do professor."""

    ano = serializers.CharField(allow_null=True)
    ano_letivo = serializers.IntegerField()
    codigo = serializers.IntegerField()
    modalidade = serializers.CharField(allow_null=True)
    codigo_modalidade = serializers.IntegerField(allow_null=True)
    nome_turma = serializers.CharField(allow_null=True)
    semestre = serializers.IntegerField()


class TurmaPorTipoSalaSerializer(serializers.Serializer):
    """Serializa turma por tipo de sala/UE/ano letivo (endpoints 2 e 4)."""

    codigo_turma = serializers.IntegerField()
    nome_turma = serializers.CharField()
    tipo_turma = serializers.IntegerField()
    situacao = serializers.CharField(allow_null=True)
    data_inicio_turma = serializers.DateTimeField(allow_null=True)
    data_fim_turma = serializers.DateTimeField(allow_null=True)


class TurmaPorEscolaSerializer(serializers.Serializer):
    """Serializa turma por UE/ano letivo com sigla de modalidade."""

    codigo_turma = serializers.IntegerField()
    nome_turma_eol = serializers.CharField()
    nome_turma = serializers.CharField()
    tipo_turma = serializers.IntegerField()
    situacao = serializers.CharField(allow_null=True)
    data_inicio_turma = serializers.DateTimeField(allow_null=True)
    data_fim_turma = serializers.DateTimeField(allow_null=True)
    sigla_modalidade = serializers.CharField(allow_null=True)


class TurmaItinerarioSerializer(serializers.Serializer):
    """Serializa dados de itinerário do Ensino Médio."""

    id = serializers.IntegerField()
    nome = serializers.CharField()
    serie = serializers.CharField()


class AnosLetivosVigenteQuerySerializer(serializers.Serializer):
    """Valida o filtro opcional de anos letivos vigentes."""

    anos_letivos_vigente = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
    )

    def to_internal_value(self, data: dict[str, Any]) -> dict[str, Any]:
        """Descarta itens vazios ou nulos antes de validar inteiros.

        Args:
            data: Query params recebidos.

        Returns:
            Dados normalizados sem entradas vazias no filtro.
        """
        if isinstance(data, QueryDict):
            brutos = data.getlist("anos_letivos_vigente")
            if brutos:
                limpos = [item for item in brutos if item not in ("", None)]
                query_data = data.copy()
                query_data.setlist("anos_letivos_vigente", limpos)
                data = cast(dict[str, Any], query_data)
        return cast(dict[str, Any], super().to_internal_value(data))
