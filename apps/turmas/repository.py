"""Repositório do domínio Turmas."""

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
    """Executa consultas ORM do domínio Turmas."""

    _DB = "default"

    def turmas_regulares(self, codigos: list[int]) -> list[dict]:
        """Lista turmas regulares pelos códigos informados.

        Args:
            codigos: Códigos das turmas a consultar.

        Returns:
            Lista de turmas regulares encontradas.
        """
        turmas = Turma.objects.using(self._DB).filter(
            tipo_turma=TIPO_TURMA_REGULAR,
            codigo__in=codigos,
        )
        return [_turma_para_lista(t) for t in turmas]

    def turmas_programa(self, codigos: list[int]) -> list[dict]:
        """Lista turmas programa pelos códigos informados.

        Args:
            codigos: Códigos das turmas a consultar.

        Returns:
            Lista de turmas programa encontradas.
        """
        turmas = Turma.objects.using(self._DB).filter(
            tipo_turma=TIPO_TURMA_PROGRAMA,
            codigo__in=codigos,
        )
        return [_turma_para_lista(t) for t in turmas]

    def listar_turmas(self, codigos: list[int]) -> list[dict]:
        """Lista turmas pelos códigos informados.

        Args:
            codigos: Códigos das turmas a consultar.

        Returns:
            Lista de turmas encontradas.
        """
        turmas = Turma.objects.using(self._DB).filter(codigo__in=codigos)
        return [_turma_para_lista(t) for t in turmas]

    def dados_turma(self, codigo: int) -> dict | None:
        """Retorna dados cadastrais de uma turma.

        Args:
            codigo: Código da turma.

        Returns:
            Dados da turma, ou None se não encontrada.
        """
        turma = Turma.objects.using(self._DB).filter(codigo=codigo).first()
        if turma is None:
            return None
        return _turma_para_dados(turma)

    def sincronizacoes_institucionais(
        self,
        ue_codigo: str,
        turma_codigo: int,
    ) -> dict | None:
        """Retorna dados de sincronização institucional da turma.

        Args:
            ue_codigo: Código da unidade educacional.
            turma_codigo: Código da turma.

        Returns:
            Dados de sincronização, ou None se não encontrada.
        """
        turma = (
            Turma.objects.using(self._DB)
            .filter(ue_codigo=ue_codigo, codigo=turma_codigo)
            .first()
        )
        if turma is None:
            return None
        return _turma_para_sincronizacao(turma)

    def anos_letivos_por_ue(self, ue_codigo: str) -> list[int]:
        """Lista anos letivos com turmas na UE.

        Args:
            ue_codigo: Código da unidade educacional.

        Returns:
            Anos letivos com turmas na UE, em ordem crescente.
        """
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
        """Lista turmas históricas do professor no ano letivo.

        Args:
            ano_letivo: Ano letivo consultado.
            professor_rf: Registro funcional do professor.

        Returns:
            Lista de turmas históricas do professor.
        """
        codigos_str = (
            AtribuicaoComponente.objects.using(self._DB)
            .filter(professor=professor_rf, ano_letivo=ano_letivo)
            .values_list("turma_codigo", flat=True)
            .distinct()
        )
        # O código de turma sincronizado como texto precisa ser filtrado como
        # inteiro no modelo de turma.
        codigos_int = [int(c) for c in codigos_str if c and c.isdigit()]
        if not codigos_int:
            return []
        turmas = (
            Turma.objects.using(self._DB)
            .filter(
                codigo__in=codigos_int,
            )
            .filter(Q(extinta=True) | Q(situacao__in=["C", "E"]))
        )
        return [_turma_para_historico(t) for t in turmas]

    def itinerarios_ensino_medio(self) -> list[dict]:
        """Lista itinerários do Ensino Médio ordenados por nome.

        Returns:
            Lista de itinerários do Ensino Médio.
        """
        return [
            {"id": i.id, "nome": i.nome, "serie": i.serie}
            for i in TurmaItinerarioEnsinoMedio.objects.using(
                self._DB
            ).order_by("nome")
        ]
