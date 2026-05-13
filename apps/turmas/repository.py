"""Repository do domínio Turmas.

Executa SELECTs no banco e retorna dicts em snake_case.
Sem regras de negócio — apenas consultas ORM.
"""

from django.db.models import Q

from apps.componentes_curriculares.constants import (
    TIPO_TURMA_EVENTO_PARA_ATRIBUICAO,
    TIPO_TURMA_PROGRAMA,
    TIPO_TURMA_REGULAR,
)
from apps.componentes_curriculares.models import AtribuicaoComponente
from apps.turmas.models import Turma, TurmaItinerarioEnsinoMedio


def _turma_para_lista(t: Turma) -> dict:
    return {
        "codigo": t.codigo,
        "nome_turma": t.nome_turma,
        "ano_letivo": t.ano_letivo,
        "ano": t.ano,
        "tipo_turma": t.tipo_turma,
        "ue_codigo": t.ue_codigo,
        "modalidade": t.modalidade,
        "codigo_modalidade": t.codigo_modalidade,
        "semestre": t.semestre or 0,
        "ensino_especial": t.ensino_especial,
        "serie_ensino": t.serie_ensino,
        "codigo_serie_ensino": t.codigo_serie_ensino,
        "situacao": t.situacao,
        "extinta": t.extinta,
    }


def _turma_para_dados(t: Turma) -> dict:
    return {
        "codigo": t.codigo,
        "ano_letivo": t.ano_letivo,
        "ano": t.ano,
        "tipo_turma": t.tipo_turma,
        "nome_turma": t.nome_turma,
        "duracao_turno": t.duracao_turno,
        "tipo_turno": t.tipo_turno,
        "data_inicio_turma": t.data_inicio_turma,
        "data_fim": t.data_fim,
        "extinta": t.extinta,
        "situacao": t.situacao,
        "ue_codigo": t.ue_codigo,
        "serie_ensino": t.serie_ensino,
        "codigo_serie_ensino": t.codigo_serie_ensino,
        "modalidade": t.modalidade,
        "codigo_modalidade": t.codigo_modalidade,
        "codigo_tipo_programa": t.codigo_tipo_programa,
        "codigo_modalidade_etapa": t.codigo_modalidade_etapa,
        "semestre": t.semestre or 0,
        "ensino_especial": t.ensino_especial,
        "data_atualizacao": t.data_atualizacao,
        "data_status_turma_escola": t.data_status_turma_escola,
    }


def _turma_para_sincronizacao(t: Turma) -> dict:
    return {
        "codigo": t.codigo,
        "ue_codigo": t.ue_codigo,
        "ano_letivo": t.ano_letivo,
        "data_inicio_turma": t.data_inicio_turma,
        "data_fim": t.data_fim,
        "data_atualizacao": t.data_atualizacao,
        "data_status_turma_escola": t.data_status_turma_escola,
        "situacao": t.situacao,
        "extinta": t.extinta,
        "codigo_modalidade": t.codigo_modalidade,
        "modalidade": t.modalidade,
        "semestre": t.semestre or 0,
        "ensino_especial": t.ensino_especial,
        "codigo_serie_ensino": t.codigo_serie_ensino,
        "serie_ensino": t.serie_ensino,
    }


def _turma_para_historico(t: Turma) -> dict:
    ehistorico = t.extinta or t.situacao == "C"
    return {
        "ano": t.ano,
        "ano_letivo": t.ano_letivo,
        "codigo": t.codigo,
        "tipo_turma": t.tipo_turma or 0,
        "modalidade": t.modalidade,
        "codigo_modalidade": t.codigo_modalidade,
        "nome_turma": t.nome_turma,
        "semestre": t.semestre or 0,
        "duracao_turno": t.duracao_turno or 0,
        "tipo_turno": t.tipo_turno or 0,
        "data_fim": t.data_fim,
        "ehistorico": ehistorico,
        "ensino_especial": t.ensino_especial,
        "etapa_eja": 0,
        "serie_ensino": t.serie_ensino,
        "data_inicio_turma": t.data_inicio_turma,
        "extinta": t.extinta,
        "situacao": t.situacao,
        "ue_codigo": t.ue_codigo,
    }


class TurmasRepository:
    """Queries ORM para o domínio Turmas"""

    _DB = "default"

    def turmas_regulares(self, codigos: list[int]) -> list[dict]:
        """Turmas regulares (tipo_turma=1) filtradas por lista de códigos"""
        turmas = Turma.objects.using(self._DB).filter(
            tipo_turma=TIPO_TURMA_REGULAR,
            codigo__in=codigos,
        )
        return [_turma_para_lista(t) for t in turmas]

    def turmas_programa(self, codigos: list[int]) -> list[dict]:
        """Turmas programa (tipo_turma=3) filtradas por lista de códigos"""
        turmas = Turma.objects.using(self._DB).filter(
            tipo_turma=TIPO_TURMA_PROGRAMA,
            codigo__in=codigos,
        )
        return [_turma_para_lista(t) for t in turmas]

    def listar_turmas(self, codigos: list[int]) -> list[dict]:
        """Turmas pelos códigos fornecidos, sem filtro de tipo"""
        turmas = Turma.objects.using(self._DB).filter(codigo__in=codigos)
        return [_turma_para_lista(t) for t in turmas]

    def dados_turma(self, codigo: int) -> dict | None:
        """Dados cadastrais de uma turma; None se não encontrada"""
        turma = Turma.objects.using(self._DB).filter(codigo=codigo).first()
        if turma is None:
            return None
        return _turma_para_dados(turma)

    def sincronizacoes_institucionais(
        self,
        ue_codigo: str,
        turma_codigo: int,
    ) -> dict | None:
        """Sincronização institucional de uma turma por UE; None se não encontrada"""
        turma = (
            Turma.objects.using(self._DB)
            .filter(ue_codigo=ue_codigo, codigo=turma_codigo)
            .first()
        )
        if turma is None:
            return None
        return _turma_para_sincronizacao(turma)

    def anos_letivos_por_ue(self, ue_codigo: str) -> list[int]:
        """Anos letivos distintos com turmas na UE, excluindo tipo_turma=4"""
        return list(
            Turma.objects.using(self._DB)
            .filter(ue_codigo=ue_codigo)
            .exclude(tipo_turma=TIPO_TURMA_EVENTO_PARA_ATRIBUICAO)
            .values_list("ano_letivo", flat=True)
            .distinct()
            .order_by("ano_letivo")
        )

    def turmas_historicas_professor(
        self,
        ano_letivo: int,
        professor_rf: str,
    ) -> list[dict]:
        """Turmas históricas do professor via AtribuicaoComponente.

        turma_codigo (varchar) é normalizado para int antes do filtro ORM.
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

    def itinerarios_ensino_medio(self) -> list[dict]:
        """Itinerários do Ensino Médio ordenados por nome"""
        return [
            {"nome": i.nome, "serie": i.serie}
            for i in TurmaItinerarioEnsinoMedio.objects.using(self._DB).order_by("nome")
        ]
