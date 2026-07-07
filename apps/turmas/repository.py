"""Repositório do domínio Turmas."""

from collections.abc import Sequence
from datetime import datetime
from typing import cast

from apps.componentes_curriculares.constants import (
    TIPO_TURMA_ED_FISICA,
    TIPO_TURMA_EVENTO_PARA_ATRIBUICAO,
    TIPO_TURMA_ITINERARIOS_2A_ANO,
    TIPO_TURMA_PROGRAMA,
    TIPO_TURMA_REGULAR,
)
from apps.componentes_curriculares.models import (
    AtribuicaoComponente,
    ComponenteCurricular,
    ComponenteTurma,
)
from apps.turmas.constants import (
    DESCRICOES_GRADE_PROGRAMA_ITINERARIO,
    ETAPA_ENSINO_MAGISTERIO,
    ETAPAS_ENSINO_TURMAS_HISTORICAS_PROFESSOR,
    PERIODICIDADES_POR_SEMESTRE,
    TIPO_GRADE_PROGRAMA_ITINERARIO,
    TIPOS_ESCOLA_TURMAS_HISTORICAS_PROFESSOR,
)
from apps.turmas.models import Turma, TurmaItinerarioEnsinoMedio

# (EOL cd_etapa_ensino): EJA (2,3,7,11) + Fundamental (4,5,12,13)
# + Médio (6,7,8,14,17). Exclui Infantil (1,10).
_ETAPAS_RECORTE_FUND_MEDIO_EJA = frozenset(
    {2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 17}
)


def _nome_filtro(
    turma: Turma,
    itinerario: TurmaItinerarioEnsinoMedio | None,
) -> str:
    if itinerario is not None:
        return (
            f"{turma.nome_turma} - {itinerario.serie}ª Série - "
            f"{itinerario.nome}"
        )

    serie_ensino = turma.serie_ensino or ""
    if (
        turma.tipo_turma == TIPO_TURMA_REGULAR
        and turma.codigo_etapa_ensino == ETAPA_ENSINO_MAGISTERIO
        and turma.serie_ensino is not None
    ):
        return f"{turma.nome_turma} - {turma.serie_ensino} - Magistério"
    if turma.tipo_turma == TIPO_TURMA_ED_FISICA:
        return f"{turma.nome_turma} - Ed Física"
    if turma.descricao_grade_programa is None:
        return f"{turma.nome_turma} - {serie_ensino}"
    if turma.tipo_turma == TIPO_TURMA_PROGRAMA:
        return (
            f"{turma.nome_turma} - "
            f"{turma.descricao_grade_programa.strip()}"
        )
    if turma.tipo_turma == TIPO_TURMA_ITINERARIOS_2A_ANO:
        descricao = turma.descricao_grade_programa
        if (
            turma.tipo_grade_programa == TIPO_GRADE_PROGRAMA_ITINERARIO
            and turma.codigo_grade_programa is not None
        ):
            descricao = DESCRICOES_GRADE_PROGRAMA_ITINERARIO.get(
                turma.codigo_grade_programa,
                descricao,
            )
        return f"{turma.nome_turma} - {descricao}"
    return f"{turma.nome_turma} - {serie_ensino}"


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
        "data_inicio_turma": t.data_inicio_turma,
        "data_fim": t.data_fim,
        "duracao_turno": t.duracao_turno,
        "tipo_turno": t.tipo_turno,
        "codigo_etapa_ensino": t.codigo_etapa_ensino,
        "codigo_ciclo_ensino": t.codigo_ciclo_ensino,
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


def _turma_para_sincronizacao(
    t: Turma,
    componentes: list[dict],
    itinerario: TurmaItinerarioEnsinoMedio | None,
) -> dict:
    return {
        "ano": t.ano,
        "ano_letivo": t.ano_letivo,
        "codigo": t.codigo,
        "tipo_turma": t.tipo_turma,
        "modalidade": t.modalidade,
        "codigo_modalidade": t.codigo_modalidade,
        "nome_turma": t.nome_turma,
        "semestre": t.semestre or 0,
        "duracao_turno": t.duracao_turno,
        "tipo_turno": t.tipo_turno,
        "data_fim_turma": t.data_fim,
        "ensino_especial": t.ensino_especial,
        "etapa_eja": 0,
        "serie_ensino": t.serie_ensino,
        "codigo_serie_ensino": t.codigo_serie_ensino,
        "data_inicio_turma": t.data_inicio_turma,
        "extinta": t.extinta,
        "situacao": t.situacao,
        "ue_codigo": t.ue_codigo,
        "data_atualizacao": t.data_atualizacao,
        "data_status_turma_escola": t.data_status_turma_escola,
        "etapa_ensino": t.codigo_etapa_ensino or 0,
        "ciclo_ensino": t.codigo_ciclo_ensino or 0,
        "tipo_escola": t.tipo_escola,
        "descricao_grade_programa": t.descricao_grade_programa,
        "tipo_grade_programa": t.tipo_grade_programa or 0,
        "codigo_grade_programa": t.codigo_grade_programa,
        "nome_filtro": _nome_filtro(t, itinerario),
        "componentes": componentes,
    }


def _turma_para_historico(t: Turma) -> dict:
    return {
        "ano": t.ano,
        "ano_letivo": t.ano_letivo,
        "codigo": t.codigo,
        "modalidade": t.modalidade,
        "codigo_modalidade": t.codigo_modalidade,
        "nome_turma": t.nome_turma,
        "semestre": t.semestre or 0,
    }


def _codigos_por_atribuicao_origem(
    registros: Sequence[tuple[str | None, int | None]],
) -> list[int]:
    codigos_por_origem: dict[int, int] = {}
    codigos_sem_origem: set[int] = set()

    for codigo_texto, atribuicao_origem in registros:
        if not codigo_texto or not codigo_texto.isdigit():
            continue
        codigo = int(codigo_texto)
        if atribuicao_origem is None:
            codigos_sem_origem.add(codigo)
            continue
        codigo_atual = codigos_por_origem.get(atribuicao_origem)
        if codigo_atual is None or codigo < codigo_atual:
            codigos_por_origem[atribuicao_origem] = codigo

    return sorted(codigos_sem_origem | set(codigos_por_origem.values()))


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

    def turmas_recorte_fund_medio_eja(self, codigos: list[int]) -> list[dict]:
        """Lista turmas no recorte de etapa (Fund/Médio/EJA).

        Args:
            codigos: Códigos das turmas a consultar.

        Returns:
            Lista de turmas no recorte de etapa encontradas.
        """
        turmas = Turma.objects.using(self._DB).filter(
            codigo__in=codigos,
            codigo_etapa_ensino__in=_ETAPAS_RECORTE_FUND_MEDIO_EJA,
        )
        return [_turma_para_lista(t) for t in turmas]

    def turmas_recorte_por_tipo(
        self,
        codigos: list[int],
        tipos_turma: list[int] | None = None,
        ue_codigo: str | None = None,
        semestre: int | None = None,
    ) -> list[int]:
        """Filtra os códigos de turma por tipo de turma, UE e semestre.

        Um semestre fora do mapeamento ``PERIODICIDADES_POR_SEMESTRE`` não aplica
        filtro de periodicidade.

        Args:
            codigos: Códigos de turma candidatos.
            tipos_turma: Tipos de turma aceitos; sem filtro quando vazio.
            ue_codigo: Código da UE; sem filtro quando ausente.
            semestre: Semestre da turma; sem filtro quando ausente.

        Returns:
            Subconjunto dos códigos informados que atende ao recorte.
        """
        if not codigos:
            return []
        consulta = Turma.objects.using(self._DB).filter(codigo__in=codigos)
        if tipos_turma:
            consulta = consulta.filter(tipo_turma__in=tipos_turma)
        if ue_codigo:
            consulta = consulta.filter(ue_codigo=ue_codigo)
        if semestre is not None:
            periodicidades = PERIODICIDADES_POR_SEMESTRE.get(semestre)
            if periodicidades:
                consulta = consulta.filter(
                    codigo_tipo_periodicidade__in=periodicidades
                )
        return list(consulta.values_list("codigo", flat=True).distinct())

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
        _ue_codigo: str,
        turma_codigo: int,
    ) -> dict | None:
        """Retorna dados de sincronização institucional da turma.

        Args:
            _ue_codigo: Código da unidade educacional, obrigatório no
                contrato mas não usado na consulta.
            turma_codigo: Código da turma.

        Returns:
            Dados de sincronização, ou None se não encontrada.
        """
        turma = (
            Turma.objects.using(self._DB).filter(codigo=turma_codigo).first()
        )
        if turma is None:
            return None
        componentes = self._componentes_da_turma(turma.codigo)
        itinerario = (
            TurmaItinerarioEnsinoMedio.objects.using(self._DB)
            .filter(id=turma.tipo_turma)
            .first()
        )
        return _turma_para_sincronizacao(turma, componentes, itinerario)

    def _componentes_da_turma(self, turma_codigo: int) -> list[dict]:
        codigos = list(
            ComponenteTurma.objects.using(self._DB)
            .filter(turma_codigo=str(turma_codigo))
            .values_list("componente_codigo", flat=True)
        )
        if not codigos:
            return []
        rows_descricoes = (
            ComponenteCurricular.objects.using(self._DB)
            .filter(codigo__in=codigos)
            .values_list("codigo", "descricao")
        )
        descricoes: dict[int, str | None] = {}
        for row in rows_descricoes:
            if isinstance(row, dict):
                codigo = cast(int, row["codigo"])
                descricao = cast(str | None, row["descricao"])
            else:
                codigo, descricao = cast(tuple[int, str | None], row)
            descricoes[codigo] = descricao

        atribuicoes = self._atribuicoes_da_turma(turma_codigo)
        componentes: list[dict] = []
        for codigo in codigos:
            descricao = descricoes.get(codigo)
            for rf, data_disp in atribuicoes.get(codigo, [(None, None)]):
                componentes.append(
                    {
                        "nome_componente_curricular": descricao,
                        "componente_curricular_codigo": codigo,
                        "registro_funcional": rf,
                        "data_disponibizacao": data_disp,
                    }
                )
        return componentes

    def _atribuicoes_da_turma(
        self,
        turma_codigo: int,
    ) -> dict[int, list[tuple[str | None, datetime | None]]]:
        atribuicoes: dict[int, list[tuple[str | None, datetime | None]]] = {}
        registros = (
            AtribuicaoComponente.objects.using(self._DB)
            .filter(turma_codigo=str(turma_codigo))
            .values_list(
                "componente_codigo",
                "professor",
                "dt_disponibilizacao",
            )
        )
        for row in registros:
            if isinstance(row, dict):
                componente_codigo = cast(int, row["componente_codigo"])
                professor = cast(str | None, row["professor"])
                dt_disponibilizacao = cast(
                    datetime | None,
                    row["dt_disponibilizacao"],
                )
            else:
                componente_codigo, professor, dt_disponibilizacao = cast(
                    tuple[int, str | None, datetime | None],
                    row,
                )
            atribuicoes.setdefault(componente_codigo, []).append(
                (professor, dt_disponibilizacao)
            )
        return atribuicoes

    def codigos_turmas_por_ue(
        self,
        ue_codigo: str,
        anos_letivos: list[int] | None,
    ) -> list[int]:
        """Lista códigos de turma da UE, exceto turmas de evento.

        Args:
            ue_codigo: Código da unidade educacional.
            anos_letivos: Anos letivos a filtrar; quando vazio, lista todos.

        Returns:
            Códigos de turma da UE, em ordem crescente e sem duplicatas.
        """
        consulta = (
            Turma.objects.using(self._DB)
            .filter(ue_codigo=ue_codigo)
            .exclude(tipo_turma=TIPO_TURMA_EVENTO_PARA_ATRIBUICAO)
        )
        if anos_letivos:
            consulta = consulta.filter(ano_letivo__in=anos_letivos)
        return list(
            consulta.values_list("codigo", flat=True)
            .distinct()
            .order_by("codigo")
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
        atribuicoes = list(
            AtribuicaoComponente.objects.using(self._DB)
            .filter(
                professor=professor_rf,
                ano_letivo=ano_letivo,
                dt_cancelamento__isnull=True,
                dt_disponibilizacao__isnull=False,
            )
            .values_list("turma_codigo", "id_atribuicao_origem")
            .distinct()
        )
        codigos_int = _codigos_por_atribuicao_origem(atribuicoes)
        if not codigos_int:
            return []
        turmas = (
            Turma.objects.using(self._DB)
            .filter(
                codigo__in=codigos_int,
                ano_letivo=ano_letivo,
                tipo_escola__in=TIPOS_ESCOLA_TURMAS_HISTORICAS_PROFESSOR,
                codigo_etapa_ensino__in=ETAPAS_ENSINO_TURMAS_HISTORICAS_PROFESSOR,
            )
            .distinct()
        )
        return [_turma_para_historico(t) for t in turmas]

    def itinerarios_ensino_medio(self) -> list[dict]:
        """Lista itinerários do Ensino Médio ordenados por id.

        Returns:
            Lista de itinerários do Ensino Médio.
        """
        return [
            {"id": i.id, "nome": i.nome, "serie": i.serie}
            for i in TurmaItinerarioEnsinoMedio.objects.using(
                self._DB
            ).order_by("id")
        ]
