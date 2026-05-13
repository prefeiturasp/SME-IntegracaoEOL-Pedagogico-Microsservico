"""Repository do domínio Turmas.

Todas as funções executam SELECTs no banco e retornam dicts em camelCase
para compatibilidade com o contrato legado EOL/SGP.
Sem regras de negócio — apenas consultas ORM.
"""

from django.db.models import Q

from apps.componentes_curriculares.models import AtribuicaoComponente
from apps.turmas.models import Turma, TurmaItinerarioEnsinoMedio


def _turma_para_lista(t: Turma) -> dict:
    return {
        "codigo": t.codigo,
        "nomeTurma": t.nome_turma,
        "anoLetivo": t.ano_letivo,
        "ano": t.ano,
        "tipoTurma": t.tipo_turma,
        "ueCodigo": t.ue_codigo,
        "modalidade": t.modalidade,
        "codigoModalidade": t.codigo_modalidade,
        "semestre": t.semestre or 0,
        "ensinoEspecial": t.ensino_especial,
        "serieEnsino": t.serie_ensino,
        "codigoSerieEnsino": t.codigo_serie_ensino,
        "situacao": t.situacao,
        "extinta": t.extinta,
    }


def _turma_para_dados(t: Turma) -> dict:
    return {
        "codigo": t.codigo,
        "anoLetivo": t.ano_letivo,
        "ano": t.ano,
        "tipoTurma": t.tipo_turma,
        "nomeTurma": t.nome_turma,
        "duracaoTurno": t.duracao_turno,
        "tipoTurno": t.tipo_turno,
        "dataInicioTurma": t.data_inicio_turma,
        "dataFim": t.data_fim,
        "extinta": t.extinta,
        "situacao": t.situacao,
        "ueCodigo": t.ue_codigo,
        "serieEnsino": t.serie_ensino,
        "codigoSerieEnsino": t.codigo_serie_ensino,
        "modalidade": t.modalidade,
        "codigoModalidade": t.codigo_modalidade,
        "codigoTipoPrograma": t.codigo_tipo_programa,
        "codigoModalidadeEtapa": t.codigo_modalidade_etapa,
        "semestre": t.semestre or 0,
        "ensinoEspecial": t.ensino_especial,
        "dataAtualizacao": t.data_atualizacao,
        "dataStatusTurmaEscola": t.data_status_turma_escola,
    }


def _turma_para_sincronizacao(t: Turma) -> dict:
    return {
        "codigo": t.codigo,
        "ueCodigo": t.ue_codigo,
        "anoLetivo": t.ano_letivo,
        "dataInicioTurma": t.data_inicio_turma,
        "dataFim": t.data_fim,
        "dataAtualizacao": t.data_atualizacao,
        "dataStatusTurmaEscola": t.data_status_turma_escola,
        "situacao": t.situacao,
        "extinta": t.extinta,
        "codigoModalidade": t.codigo_modalidade,
        "modalidade": t.modalidade,
        "semestre": t.semestre or 0,
        "ensinoEspecial": t.ensino_especial,
        "codigoSerieEnsino": t.codigo_serie_ensino,
        "serieEnsino": t.serie_ensino,
    }


def _turma_para_historico(t: Turma) -> dict:
    ehistorico = t.extinta or t.situacao == "C"
    return {
        "ano": t.ano,
        "anoLetivo": t.ano_letivo,
        "codigo": t.codigo,
        "tipoTurma": t.tipo_turma or 0,
        "modalidade": t.modalidade,
        "codigoModalidade": t.codigo_modalidade,
        "nomeTurma": t.nome_turma,
        "semestre": t.semestre or 0,
        "duracaoTurno": t.duracao_turno or 0,
        "tipoTurno": t.tipo_turno or 0,
        "dataFim": t.data_fim,
        "ehistorico": ehistorico,
        "ensinoEspecial": t.ensino_especial,
        "etapaEJA": 0,
        "serieEnsino": t.serie_ensino,
        "dataInicioTurma": t.data_inicio_turma,
        "extinta": t.extinta,
        "situacao": t.situacao,
        "ueCodigo": t.ue_codigo,
    }


class TurmasRepository:
    """Queries ORM para o domínio Turmas."""

    _DB = "default"

    # -------------------------------------------------------------------------
    # POST turmas-regulares
    # -------------------------------------------------------------------------

    def turmas_regulares(self, codigos: list[int]) -> list[dict]:
        """Retorna turmas regulares (tipo_turma=1) dentro da lista de códigos."""
        turmas = Turma.objects.using(self._DB).filter(
            tipo_turma=1,
            codigo__in=codigos,
        )
        return [_turma_para_lista(t) for t in turmas]

    # -------------------------------------------------------------------------
    # POST turmas-programa
    # -------------------------------------------------------------------------

    def turmas_programa(self, codigos: list[int]) -> list[dict]:
        """Retorna turmas programa (tipo_turma=3) dentro da lista de códigos."""
        turmas = Turma.objects.using(self._DB).filter(
            tipo_turma=3,
            codigo__in=codigos,
        )
        return [_turma_para_lista(t) for t in turmas]

    # -------------------------------------------------------------------------
    # POST listar-turmas
    # -------------------------------------------------------------------------

    def listar_turmas(self, codigos: list[int]) -> list[dict]:
        """Retorna turmas pelos códigos fornecidos, sem filtro de tipo."""
        turmas = Turma.objects.using(self._DB).filter(codigo__in=codigos)
        return [_turma_para_lista(t) for t in turmas]

    # -------------------------------------------------------------------------
    # GET {codigoTurma}/dados
    # -------------------------------------------------------------------------

    def dados_turma(self, codigo: int) -> dict | None:
        """Retorna todos os dados cadastrais de uma turma. None se não existir."""
        turma = Turma.objects.using(self._DB).filter(codigo=codigo).first()
        if turma is None:
            return None
        return _turma_para_dados(turma)

    # -------------------------------------------------------------------------
    # GET /api/ues/{ueCodigo}/turmas/{turmaCodigo}/sincronizacoes-institucionais
    # -------------------------------------------------------------------------

    def sincronizacoes_institucionais(
        self,
        ue_codigo: str,
        turma_codigo: int,
    ) -> dict | None:
        """Retorna dados de sincronização institucional de uma turma por UE."""
        turma = (
            Turma.objects.using(self._DB)
            .filter(ue_codigo=ue_codigo, codigo=turma_codigo)
            .first()
        )
        if turma is None:
            return None
        return _turma_para_sincronizacao(turma)

    # -------------------------------------------------------------------------
    # GET ue/{ueCodigo}/sincronizacoes-institucionais/anosLetivos
    # -------------------------------------------------------------------------

    def anos_letivos_por_ue(self, ue_codigo: str) -> list[int]:
        """Retorna anos letivos distintos com turmas na UE (exclui tipo_turma=4)."""
        return list(
            Turma.objects.using(self._DB)
            .filter(ue_codigo=ue_codigo)
            .exclude(tipo_turma=4)
            .values_list("ano_letivo", flat=True)
            .distinct()
            .order_by("ano_letivo")
        )

    # -------------------------------------------------------------------------
    # GET anos-letivos/{anoLetivo}/professor/{professorRf}/turmas-historicas-geral
    # -------------------------------------------------------------------------

    def turmas_historicas_professor(
        self,
        ano_letivo: int,
        professor_rf: str,
    ) -> list[dict]:
        """Retorna turmas históricas do professor via AtribuicaoComponente.

        O join entre atribuicao_componente.turma_codigo (varchar) e
        turma.codigo (bigint) é normalizado em Python antes do filtro ORM.
        """
        codigos_str = (
            AtribuicaoComponente.objects.using(self._DB)
            .filter(professor=professor_rf, ano_letivo=ano_letivo)
            .values_list("turma_codigo", flat=True)
            .distinct()
        )
        codigos_int = [int(c) for c in codigos_str if c and c.isdigit()]
        if not codigos_int:
            return []
        turmas = Turma.objects.using(self._DB).filter(
            codigo__in=codigos_int,
        ).filter(Q(extinta=True) | Q(situacao__in=["C", "E"]))
        return [_turma_para_historico(t) for t in turmas]

    # -------------------------------------------------------------------------
    # GET itinerario/ensino-medio
    # -------------------------------------------------------------------------

    def itinerarios_ensino_medio(self) -> list[dict]:
        """Retorna os itinerários do Ensino Médio ordenados por nome."""
        return [
            {"nome": i.nome, "serie": i.serie}
            for i in TurmaItinerarioEnsinoMedio.objects.using(self._DB).order_by("nome")
        ]
