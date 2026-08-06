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
    tipo_escola = serializers.CharField(allow_null=True)
    exibir_componente_eol = serializers.BooleanField()
    professor = serializers.CharField(allow_null=True)
    codigos_territorios_agrupamento = serializers.ListField(
        child=serializers.IntegerField(), default=list
    )


class ComponenteSimplificadoSerializer(serializers.Serializer):
    """Serializa dados simplificados de componente curricular."""

    codigo = serializers.IntegerField()
    descricao = serializers.CharField()


class ComponenteCurricularApiEolSerializer(serializers.Serializer):
    """Serializa dados de componente curricular da API EOL."""

    id_relacao_origem = serializers.IntegerField(allow_null=True)
    id_componente_curricular = serializers.IntegerField()
    eh_regencia = serializers.BooleanField()
    eh_territorio = serializers.BooleanField()
    descricao = serializers.CharField(allow_null=True)
    id_componente_curricular_pai = serializers.IntegerField(allow_null=True)
    vigencia = serializers.DateTimeField(allow_null=True)


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


class TurmaAtribuidaAnoSerializer(serializers.Serializer):
    """Serializa uma atribuição agrupada de Território do Saber."""

    codigo_turma = serializers.CharField(allow_null=True)
    ano_letivo = serializers.IntegerField()
    nome_turma = serializers.CharField(allow_null=True)
    data_inicio_atribuicao = serializers.DateTimeField()
    data_fim_atribuicao = serializers.DateTimeField(allow_null=True)
    data_fim_turma = serializers.DateTimeField(allow_null=True)
    ano_atribuicao = serializers.IntegerField()
    codigo_rf = serializers.CharField(allow_null=True)
    disciplina_id = serializers.CharField()
    disciplina_nome = serializers.CharField()
    disciplinas_agrupadas_ids = serializers.ListField(
        child=serializers.IntegerField()
    )
    nome_professor = serializers.CharField(allow_null=True)


class AtribuicaoTerritorioTurmaSerializer(serializers.Serializer):
    """Serializa uma atribuição de Território do Saber da turma."""

    codigo_territorio_saber = serializers.IntegerField()
    codigo_experiencia_pedagogica = serializers.IntegerField(allow_null=True)
    dt_inicio_atribuicao = serializers.DateTimeField()
    ano_atribuicao = serializers.IntegerField()
    dt_fim_atribuicao = serializers.DateTimeField(allow_null=True)
    dt_fim_turma = serializers.DateTimeField(allow_null=True)
    codigo_motivo_disponibilizacao = serializers.IntegerField(allow_null=True)
    rf_professor = serializers.CharField(allow_null=True)
    codigo_turma = serializers.CharField(allow_null=True)
    ano_letivo = serializers.IntegerField()
    codigos_componentes_curriculares = serializers.CharField(allow_null=True)
    descricao_territorio_saber = serializers.CharField(allow_null=True)
    descricao_experiencia_pedagogica = serializers.CharField(allow_null=True)
    encerramento_atribuicao_via_atualizacao_componentes_agrupados = (
        serializers.BooleanField(allow_null=True)
    )
    atribuicao_externa = serializers.BooleanField()
    componentes_curriculares_agrupados = serializers.ListField(
        child=serializers.IntegerField()
    )


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


class ListagemTurmaComponenteSerializer(serializers.Serializer):
    """Serializa um item da listagem turma×componente."""

    id = serializers.CharField(allow_null=True)
    registro_funcional = serializers.CharField(allow_null=True)
    turma_codigo = serializers.CharField(allow_null=True)
    modalidade = serializers.IntegerField(allow_null=True)
    nome_turma = serializers.CharField(allow_null=True)
    ano = serializers.CharField(allow_null=True)
    complemento_turma_eja = serializers.CharField(allow_blank=True)
    nome_componente_curricular = serializers.CharField(allow_null=True)
    componente_curricular_codigo = serializers.IntegerField(allow_null=True)
    turno = serializers.CharField(allow_null=True)
    territorio_saber = serializers.BooleanField()
    componente_curricular_territorio_saber_codigo = serializers.IntegerField()
    ano_letivo = serializers.IntegerField(allow_null=True)
    tipo_turma = serializers.IntegerField(allow_null=True)
    tipo_escola = serializers.IntegerField(allow_null=True)
    situacao_turma_escola = serializers.CharField(allow_null=True)
    data_status_turma_escola = serializers.DateTimeField(allow_null=True)
    codigo_escola = serializers.CharField(allow_null=True)
    etapa_ensino = serializers.IntegerField(allow_null=True)
    ciclo_ensino = serializers.IntegerField(allow_null=True)
    serie_ensino = serializers.CharField(allow_null=True)
    tipo_grade_programa = serializers.IntegerField(allow_null=True)
    codigo_grade_programa = serializers.IntegerField(allow_null=True)
    descricao_grade_programa = serializers.CharField(allow_null=True)
    data_inicio_turma = serializers.DateTimeField(allow_null=True)
    data_fim_turma = serializers.DateTimeField(allow_null=True)
    data_atualizacao = serializers.DateTimeField(allow_null=True)
    duracao_turno = serializers.IntegerField(allow_null=True)
    ensino_especial = serializers.BooleanField(allow_null=True)
    semestre = serializers.IntegerField(allow_null=True)
    extinta = serializers.BooleanField(allow_null=True)


class ListagemTurmasComponentesPaginadoSerializer(serializers.Serializer):
    """Serializa a resposta paginada da listagem turma×componente."""

    items = ListagemTurmaComponenteSerializer(many=True)
    total_registros = serializers.IntegerField()
    total_paginas = serializers.IntegerField()
