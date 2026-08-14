"""Repositório do domínio Turmas."""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any, cast

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
    SITUACOES_TURMA_VIGENTE,
    TIPO_GRADE_PROGRAMA_ITINERARIO,
    TIPO_TURMA_EXCLUIDO_CONTAGEM,
    TIPOS_ESCOLA_CONTAGEM_ALUNOS,
    TIPOS_ESCOLA_TURMAS_HISTORICAS_PROFESSOR,
)
from apps.turmas.models import (
    EtapaEnsino,
    Turma,
    TurmaAtribuidaDreUe,
    TurmaItinerarioEnsinoMedio,
)

# (EOL cd_etapa_ensino): EJA (2,3,7,11) + Fundamental (4,5,12,13)
# + Médio (6,7,8,14,17). Exclui Infantil (1,10).
_ETAPAS_RECORTE_FUND_MEDIO_EJA = frozenset(
    {2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 17}
)
_TIPOS_ESCOLA_TURMAS_ELEGIVEIS = frozenset({1, 3, 4, 16})
_SITUACOES_TURMAS_ELEGIVEIS = ("A", "C", "O")

# Sigla exibida por turma (Turma.modalidade materializado pelo ETL).
_SIGLAS_MODALIDADE = {
    "Infantil": "EI",
    "EJA": "EJA",
    "Fundamental": "EF",
    "Médio": "EM",
}
_NOME_TURMA_COMECA_COM_DIGITO = r"^[1-9]"
_ETAPA_ENSINO_SONDAGEM = 5
_SITUACAO_EXTINTA = "E"


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


def _etapa_eja(turma: Turma) -> int:
    """Deriva o ciclo EJA (I/II) a partir do texto da série ensino.

    Só se aplica a turmas de modalidade EJA. O ciclo não é uma coluna do
    EOL: é inferido de marcadores romanos (" I "/" II") presentes no texto
    de ``serie_ensino``.

    Args:
        turma: Turma consultada.

    Returns:
        1 para ciclo I, 2 para ciclo II, 0 quando não aplicável/detectável.
    """
    serie = turma.serie_ensino
    if turma.modalidade != "EJA" or not serie or len(serie) <= 2:
        return 0
    etapa = serie[-2:].strip()
    index_primeiro_ciclo = serie.find(" I ")
    index_segundo_ciclo = serie.find(" II")
    if (etapa == "I" and index_segundo_ciclo < 0) or (
        index_primeiro_ciclo >= 0 and index_segundo_ciclo < 0
    ):
        return 1
    if (etapa == "II" and index_primeiro_ciclo < 0) or (
        index_primeiro_ciclo < 0 and index_segundo_ciclo >= 0
    ):
        return 2
    return 0


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
        "data_fim_turma": t.data_fim_turma,
        "ensino_especial": t.ensino_especial,
        "etapa_eja": _etapa_eja(t),
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


def _turma_para_sala(t: Turma) -> dict:
    return {
        "codigo_turma": t.codigo,
        "nome_turma": t.nome_turma,
        "tipo_turma": t.tipo_turma,
        "situacao": t.situacao,
        "data_inicio_turma": t.data_inicio_turma,
        "data_fim_turma": t.data_fim_turma,
    }


def _sigla_modalidade(turma: Turma) -> str | None:
    return _SIGLAS_MODALIDADE.get(turma.modalidade or "")


def _turma_para_escola(t: Turma) -> dict:
    sigla = _sigla_modalidade(t)
    nome_turma = f"{sigla} - {t.nome_turma}" if sigla else t.nome_turma
    return {
        "codigo_turma": t.codigo,
        "nome_turma_eol": t.nome_turma,
        "nome_turma": nome_turma,
        "tipo_turma": t.tipo_turma,
        "situacao": t.situacao,
        "data_inicio_turma": t.data_inicio_turma,
        "data_fim_turma": t.data_fim_turma,
        "sigla_modalidade": sigla,
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


def _turma_atribuida_para_lista(t: TurmaAtribuidaDreUe) -> dict:
    return {
        "codigo_escola": t.codigo_escola,
        "codigo_turma": t.codigo_turma,
        "ano_letivo": t.ano_letivo,
        "modalidade": t.modalidade,
        "semestre": t.semestre,
        "codigo_modalidade": t.codigo_modalidade,
        "codigo_dre": t.codigo_dre,
        "dre": t.dre,
        "dre_abreviacao": t.dre_abreviacao,
        "ue": t.ue,
        "ue_abreviacao": t.ue_abreviacao,
        "nome_turma": t.nome_turma,
        "ano": t.ano,
        "tipo_ue": t.tipo_ue,
        "codigo_tipo_ue": t.codigo_tipo_ue,
        "codigo_tipo_escola": t.codigo_tipo_escola,
        "tipo_escola": t.tipo_escola,
        "duracao_turno": t.duracao_turno,
        "tipo_turno": t.tipo_turno,
    }


# Tipos de escola considerados pela abrangência de SME (parâmetro
# tipo_escola_sgp do legado); recorta o universo de turmas atribuídas.
_TIPOS_ESCOLA_SGP = (
    1,
    2,
    3,
    4,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    22,
    23,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    33,
    38,
)

_CAMPOS_TURMA_ATRIBUIDA = (
    "codigo_escola",
    "codigo_turma",
    "ano_letivo",
    "modalidade",
    "semestre",
    "codigo_modalidade",
    "codigo_dre",
    "dre",
    "dre_abreviacao",
    "ue",
    "ue_abreviacao",
    "nome_turma",
    "ano",
    "tipo_ue",
    "codigo_tipo_ue",
    "codigo_tipo_escola",
    "tipo_escola",
    "duracao_turno",
    "tipo_turno",
)


def _turma_abrangencia(item: dict) -> dict:
    """Monta a turma no contrato de abrangência."""
    return {
        "ano": item.get("ano"),
        "anoLetivo": item.get("ano_letivo"),
        "codigo": item.get("codigo_turma"),
        "tipoTurma": 0,
        "modalidade": item.get("modalidade"),
        "codigoModalidade": item.get("codigo_modalidade") or 0,
        "nomeTurma": item.get("nome_turma"),
        "semestre": item.get("semestre"),
        "duracaoTurno": item.get("duracao_turno"),
        "tipoTurno": item.get("tipo_turno"),
        "dataFim": None,
        "ehistorico": False,
        "ensinoEspecial": False,
        "etapaEJA": 0,
        "serieEnsino": None,
        "dataInicioTurma": None,
        "extinta": False,
        "situacao": None,
        "ueCodigo": None,
    }


def _agrupar_abrangencia_dre_ue(rows: Any) -> dict:
    """Agrupa as turmas atribuídas por DRE e UE no contrato de abrangência.

    Feito no domínio para o gateway apenas repassar, evitando reprocessar
    todo o conjunto de turmas.
    """
    dres: dict[str, dict] = {}
    ues_por_dre: dict[tuple[str, str], dict] = {}
    turmas_vistas: set[tuple[str, str, Any]] = set()

    for item in rows:
        codigo_ue = item.get("codigo_escola")
        if not codigo_ue:
            continue
        codigo_dre = item.get("codigo_dre")
        chave_dre = str(codigo_dre) if codigo_dre else "__sem_dre__"
        dre = dres.get(chave_dre)
        if dre is None:
            dre = {
                "abreviacao": item.get("dre_abreviacao"),
                "codigo": codigo_dre,
                "nome": item.get("dre"),
                "ues": [],
            }
            dres[chave_dre] = dre

        chave_ue = (chave_dre, str(codigo_ue))
        ue = ues_por_dre.get(chave_ue)
        if ue is None:
            ue = {
                "codigo": codigo_ue,
                "nome": item.get("ue"),
                "codTipoEscola": item.get("codigo_tipo_escola"),
                "turmas": [],
            }
            ues_por_dre[chave_ue] = ue
            dre["ues"].append(ue)

        chave_turma = (chave_dre, str(codigo_ue), item.get("codigo_turma"))
        if chave_turma in turmas_vistas:
            continue
        turmas_vistas.add(chave_turma)
        ue["turmas"].append(_turma_abrangencia(item))

    return {"abrangencia": None, "dres": list(dres.values())}


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

    def turmas_atribuidas_dre_ue(self, codigos_ue: list[str]) -> list[dict]:
        """Lista turmas atribuídas por unidades.

        Args:
            codigos_ue: Códigos das unidades educacionais.

        Returns:
            Lista de turmas atribuídas encontradas.
        """
        if not codigos_ue:
            return []
        turmas = (
            TurmaAtribuidaDreUe.objects.using(self._DB)
            .filter(codigo_escola__in=codigos_ue)
            .order_by(
                "codigo_dre",
                "codigo_escola",
                "ano_letivo",
                "nome_turma",
                "codigo_turma",
            )
            .values(*_CAMPOS_TURMA_ATRIBUIDA)
        )
        return list(turmas)

    def todas_turmas_atribuidas_dre_ue(self) -> dict:
        """Abrangência SME agrupada por DRE/UE (recorte de tipo de escola)."""
        turmas = (
            TurmaAtribuidaDreUe.objects.using(self._DB)
            .filter(codigo_tipo_escola__in=_TIPOS_ESCOLA_SGP)
            .values(*_CAMPOS_TURMA_ATRIBUIDA)
        )
        return _agrupar_abrangencia_dre_ue(turmas)

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

        Um semestre fora do mapeamento ``PERIODICIDADES_POR_SEMESTRE`` não
        aplica filtro de periodicidade.

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

    def codigos_turmas_por_ano_modalidade_dre(
        self,
        ues_codigos: Sequence[str],
        ano_turma: str | None = None,
        codigo_modalidade: int | None = None,
        ano_letivo: int | None = None,
    ) -> list[int]:
        """Lista códigos de turmas vigentes para a contagem de alunos.

        Restringe às turmas vigentes (``situacao`` em ``('O','A','E','C')``,
        tipo de turma diferente de ``4`` e tipo de escola no recorte de
        contagem), nas UEs informadas, no ano letivo da chamada — ou no ano
        corrente quando a chamada não informa um. Aplica também os filtros de
        ano e modalidade materializada.

        Args:
            ues_codigos: Códigos EOL das UEs consideradas.
            ano_turma: Primeiro caractere da nomenclatura da turma; sem filtro
                quando ausente.
            codigo_modalidade: Modalidade materializada; sem filtro quando
                ausente ou não positiva.
            ano_letivo: Ano letivo da chamada; usa o ano corrente quando
                ausente ou não positivo.

        Returns:
            Códigos distintos das turmas que atendem ao recorte.
        """
        if not ues_codigos:
            return []
        ano_letivo_filtro = (
            ano_letivo
            if ano_letivo and ano_letivo > 0
            else datetime.now(UTC).year
        )
        consulta = (
            Turma.objects.using(self._DB)
            .filter(
                ue_codigo__in=ues_codigos,
                ano_letivo=ano_letivo_filtro,
                situacao__in=SITUACOES_TURMA_VIGENTE,
                tipo_escola__in=TIPOS_ESCOLA_CONTAGEM_ALUNOS,
            )
            .exclude(tipo_turma=TIPO_TURMA_EXCLUIDO_CONTAGEM)
        )
        if ano_turma:
            consulta = consulta.filter(ano=ano_turma)
        if codigo_modalidade and codigo_modalidade > 0:
            consulta = consulta.filter(codigo_modalidade=codigo_modalidade)
        return list(consulta.values_list("codigo", flat=True).distinct())

    def turmas_elegiveis(
        self,
        codigo_rf: str,
        codigo_turma: int,
        componente_curricular: int,
    ) -> list[dict]:
        """Lista turmas elegíveis por atribuição de componente.

        Args:
            codigo_rf: RF usado na consulta.
            codigo_turma: Turma base da consulta.
            componente_curricular: Componente usado no filtro.

        Returns:
            Turmas elegíveis encontradas.
        """
        turma_base = (
            Turma.objects.using(self._DB).filter(codigo=codigo_turma).first()
        )
        if turma_base is None:
            return []

        turma_atribuida_base = (
            TurmaAtribuidaDreUe.objects.using(self._DB)
            .filter(codigo_turma=codigo_turma)
            .first()
        )
        semestre_base = (
            turma_atribuida_base.semestre
            if turma_atribuida_base is not None
            else turma_base.semestre
        )

        atribuicoes = AtribuicaoComponente.objects.using(self._DB).filter(
            professor=codigo_rf,
            componente_codigo=componente_curricular,
            ano_letivo=turma_base.ano_letivo,
            dt_cancelamento__isnull=True,
        )
        codigos = (
            atribuicoes.exclude(turma_codigo=str(codigo_turma))
            .values_list("turma_codigo", flat=True)
            .distinct()
        )
        codigos_turma = [
            int(codigo) for codigo in codigos if str(codigo).isdigit()
        ]
        if not codigos_turma:
            return []

        turmas_atribuidas = TurmaAtribuidaDreUe.objects.using(self._DB).filter(
            codigo_turma__in=codigos_turma,
        )
        if semestre_base is not None:
            turmas_atribuidas = turmas_atribuidas.filter(
                semestre=semestre_base,
            )

        if turmas_atribuidas.exists():
            codigos_turma = list(
                turmas_atribuidas.values_list(
                    "codigo_turma", flat=True
                ).distinct()
            )
        else:
            limite_ano_letivo = datetime(
                turma_base.ano_letivo, 1, 1, tzinfo=UTC
            )
            codigos = (
                atribuicoes.filter(dt_atribuicao__lt=limite_ano_letivo)
                .exclude(turma_codigo=str(codigo_turma))
                .values_list("turma_codigo", flat=True)
                .distinct()
            )
            codigos_turma = [
                int(codigo) for codigo in codigos if str(codigo).isdigit()
            ]
            if not codigos_turma:
                return []

        filtros_turma = {
            "codigo__in": codigos_turma,
            "ue_codigo": turma_base.ue_codigo,
            "ano_letivo": turma_base.ano_letivo,
            "codigo_etapa_ensino": turma_base.codigo_etapa_ensino,
            "situacao__in": _SITUACOES_TURMAS_ELEGIVEIS,
        }
        if turma_atribuida_base is not None:
            filtros_turma["tipo_escola__in"] = _TIPOS_ESCOLA_TURMAS_ELEGIVEIS
        if turma_atribuida_base is None and semestre_base is not None:
            filtros_turma["semestre"] = semestre_base

        turmas = Turma.objects.using(self._DB).filter(**filtros_turma)
        if turma_base.tipo_turma != TIPO_TURMA_PROGRAMA:
            turmas = turmas.filter(ano=turma_base.ano)

        return [
            {"cod_turma": turma.codigo, "nome_turma": turma.nome_turma}
            for turma in turmas.order_by("nome_turma", "codigo")
        ]

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

    def modalidades_ensino(self) -> list[str]:
        """Lista as descrições do catálogo de etapas de ensino.

        Returns:
            Descrições das etapas de ensino, ordenadas por código.
        """
        return list(
            EtapaEnsino.objects.using(self._DB)
            .order_by("codigo")
            .values_list("descricao", flat=True)
        )

    def turmas_por_tipo_sala(
        self,
        ue_codigo: str,
        tipo_turma: int,
        ano_letivo: int,
    ) -> list[dict]:
        """Lista turmas de uma UE/ano letivo por tipo de sala.

        Sem filtro de situação — inclui turmas extintas/canceladas.

        Args:
            ue_codigo: Código da unidade educacional.
            tipo_turma: Tipo de turma (sala) filtrado.
            ano_letivo: Ano letivo consultado.

        Returns:
            Turmas encontradas no recorte.
        """
        turmas = Turma.objects.using(self._DB).filter(
            ue_codigo=ue_codigo,
            tipo_turma=tipo_turma,
            ano_letivo=ano_letivo,
        )
        return [_turma_para_sala(t) for t in turmas]

    def turmas_por_escola(
        self,
        ue_codigo: str,
        ano_letivo: int,
    ) -> list[dict]:
        """Lista turmas de uma UE/ano letivo cujo nome começa com dígito.

        Só turmas regulares: turmas de Educação Física, Programa e outros
        tipos administrativos nunca têm série/grade curricular vinculada no
        EOL.

        Args:
            ue_codigo: Código da unidade educacional.
            ano_letivo: Ano letivo consultado.

        Returns:
            Turmas encontradas, ordenadas por nome.
        """
        turmas = (
            Turma.objects.using(self._DB)
            .filter(
                ue_codigo=ue_codigo,
                ano_letivo=ano_letivo,
                tipo_turma=TIPO_TURMA_REGULAR,
                nome_turma__regex=_NOME_TURMA_COMECA_COM_DIGITO,
            )
            .order_by("nome_turma")
        )
        return [_turma_para_escola(t) for t in turmas]

    def turmas_sondagem(
        self,
        ue_codigo: str,
        ano_letivo: int,
    ) -> list[dict]:
        """Lista turmas regulares de 5º ano do Fundamental para Sondagem.

        Args:
            ue_codigo: Código da unidade educacional.
            ano_letivo: Ano letivo consultado.

        Returns:
            Turmas encontradas, ordenadas por nome.
        """
        turmas = (
            Turma.objects.using(self._DB)
            .filter(
                ue_codigo=ue_codigo,
                ano_letivo=ano_letivo,
                codigo_etapa_ensino=_ETAPA_ENSINO_SONDAGEM,
                tipo_turma=TIPO_TURMA_REGULAR,
                nome_turma__regex=_NOME_TURMA_COMECA_COM_DIGITO,
            )
            .exclude(situacao=_SITUACAO_EXTINTA)
            .order_by("nome_turma")
        )
        return [_turma_para_sala(t) for t in turmas]
