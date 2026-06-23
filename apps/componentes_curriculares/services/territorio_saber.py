"""Serviços de Território do Saber."""

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date

from django.db.models import F

from apps.componentes_curriculares.constants import (
    MOTIVO_DISPONIBILIZACAO_FIM_ANO_LETIVO,
)
from apps.componentes_curriculares.models import (
    AgrupamentoAtribuicaoTerritorioSaber,
    AtribuicaoComponente,
    ComponenteTurma,
)


@dataclass
class AgrupamentosTerritorioSelecionados:
    """Agrupamentos e metadados selecionados para uma turma."""

    agrupamentos: list[AgrupamentoAtribuicaoTerritorioSaber] = field(
        default_factory=list
    )
    codigos_agrupados: set[int] = field(default_factory=set)
    primeiros_codigos: set[int] = field(default_factory=set)
    descricoes_primeiros_codigos: dict[int, str] = field(default_factory=dict)


def parse_csv(csv_str: str | None) -> list[int]:
    """Retorna códigos de componentes extraídos de CSV.

    Args:
        csv_str: Texto CSV com códigos de componentes.

    Returns:
        Lista de códigos inteiros válidos.
    """
    if not csv_str:
        return []
    return [int(c.strip()) for c in csv_str.split(",") if c.strip().isdigit()]


def agrupamento_para_dict(
    agrupamento: AgrupamentoAtribuicaoTerritorioSaber,
) -> dict:
    """Formata agrupamento de território para resposta.

    Args:
        agrupamento: Agrupamento de território do saber.

    Returns:
        Agrupamento no formato interno de resposta.
    """
    codigos = parse_csv(agrupamento.cod_componentes_curriculares)
    primeiro = codigos[0] if codigos else 0
    ts = agrupamento.desc_territorio_saber or ""
    ep = agrupamento.desc_experiencia_pedagogica or ""
    descricao = f"{ts} - {ep}" if ep else ts
    return {
        "codigo": agrupamento.cod_agrupamento,
        "codigo_componente_territorio_saber": primeiro,
        "codigo_componente_curricular_pai": None,
        "descricao": descricao,
        "regencia": False,
        "planejamento_regencia": False,
        "territorio_saber": True,
        "turma_codigo": agrupamento.cod_turma,
        "exibir_componente_eol": False,
        "professor": agrupamento.rf_professor,
        "codigos_territorios_agrupamento": codigos,
    }


def agrupamento_vigente_na_data(
    agrupamento: AgrupamentoAtribuicaoTerritorioSaber,
    data_base: date | None,
) -> bool:
    """Verifica se o agrupamento está vigente na data informada.

    Args:
        agrupamento: Agrupamento de Território do Saber avaliado.
        data_base: Data de referência; None ignora o filtro de data.

    Returns:
        True quando o agrupamento deve ser considerado vigente na data.
    """
    if data_base is None:
        return True
    if (
        agrupamento.cod_motivo_disponibilizacao
        == MOTIVO_DISPONIBILIZACAO_FIM_ANO_LETIVO
    ):
        return True

    data_fim = agrupamento.dt_fim_atribuicao or agrupamento.dt_fim_turma
    if agrupamento.dt_inicio_atribuicao.date() <= data_base and (
        data_fim is None or data_fim.date() >= data_base
    ):
        return True
    return bool(
        data_fim
        and agrupamento.dt_fim_turma
        and data_fim.date() >= agrupamento.dt_fim_turma.date()
    )


def componentes_agrupados_sao_subconjunto(
    agrupamento: AgrupamentoAtribuicaoTerritorioSaber,
    origem: AgrupamentoAtribuicaoTerritorioSaber,
) -> bool:
    """Indica se os componentes do agrupamento pertencem à origem.

    Args:
        agrupamento: Agrupamento candidato a entrar na resposta.
        origem: Agrupamento usado como origem da consulta.

    Returns:
        True quando todos os componentes do candidato estão na origem.
    """
    codigos = set(parse_csv(agrupamento.cod_componentes_curriculares))
    codigos_origem = set(parse_csv(origem.cod_componentes_curriculares))
    return bool(codigos) and codigos.issubset(codigos_origem)


def atribuicao_nao_agrupada_para_dict(
    componente: ComponenteTurma,
    atribuicao: AtribuicaoComponente,
    origem: AgrupamentoAtribuicaoTerritorioSaber,
) -> dict:
    """Formata atribuição única de território como componente.

    Args:
        componente: Vínculo turma-componente de Território do Saber.
        atribuicao: Atribuição do professor ao componente.
        origem: Agrupamento usado para compor a descrição da resposta.

    Returns:
        Componente individual no formato interno de resposta.
    """
    descricao = agrupamento_para_dict(origem)["descricao"]
    return {
        "codigo": componente.componente_codigo,
        "codigo_componente_territorio_saber": (
            componente.codigo_componente_territorio_saber
            or componente.componente_codigo
        ),
        "codigo_componente_curricular_pai": None,
        "descricao": descricao,
        "regencia": False,
        "planejamento_regencia": False,
        "territorio_saber": True,
        "turma_codigo": componente.turma_codigo,
        "exibir_componente_eol": False,
        "professor": atribuicao.professor,
        "codigos_territorios_agrupamento": [componente.componente_codigo],
    }


def _codigos_turmas_com_territorio(componentes: list[dict]) -> set[object]:
    """Retorna turmas com componentes de território."""
    return {
        item["turma_codigo"]
        for item in componentes
        if item.get("territorio_saber") and item.get("turma_codigo")
    }


def _buscar_agrupamentos_da_turma(
    using: str,
    turma_codigo: object,
    login: str,
) -> Iterable[AgrupamentoAtribuicaoTerritorioSaber]:
    """Busca agrupamentos de território da turma e professor."""
    return (
        AgrupamentoAtribuicaoTerritorioSaber.objects.using(using)
        .filter(cod_turma=turma_codigo, rf_professor=login)
        .order_by(
            F("dt_fim_atribuicao").asc(nulls_first=True),
            "-dt_inicio_atribuicao",
        )
    )


def _selecionar_agrupamentos(
    agrupamentos: Iterable[AgrupamentoAtribuicaoTerritorioSaber],
) -> AgrupamentosTerritorioSelecionados:
    """Seleciona agrupamentos válidos por conjunto de componentes."""
    selecionados = AgrupamentosTerritorioSelecionados()
    chaves_vistas: set[str | None] = set()

    for agrupamento in agrupamentos:
        codigos = parse_csv(agrupamento.cod_componentes_curriculares)
        if len(codigos) < 2:
            continue
        if agrupamento.cod_componentes_curriculares in chaves_vistas:
            continue
        chaves_vistas.add(agrupamento.cod_componentes_curriculares)
        selecionados.agrupamentos.append(agrupamento)
        selecionados.codigos_agrupados.update(codigos)
        selecionados.primeiros_codigos.add(codigos[0])
        selecionados.descricoes_primeiros_codigos[codigos[0]] = (
            agrupamento_para_dict(agrupamento)["descricao"]
        )
    return selecionados


def _deve_remover_componente_territorio(
    item: dict,
    turma_codigo: object,
    login: str,
    selecionados: AgrupamentosTerritorioSelecionados,
) -> bool:
    """Indica se um componente deve sair da lista final."""
    if not item.get("territorio_saber"):
        return False
    if item.get("turma_codigo") != turma_codigo:
        return False
    if item.get("professor") == login:
        return item.get("codigo") in selecionados.codigos_agrupados
    return item.get("codigo") not in selecionados.primeiros_codigos


def _remover_componentes_agrupados(
    componentes: list[dict],
    turma_codigo: object,
    login: str,
    selecionados: AgrupamentosTerritorioSelecionados,
) -> list[dict]:
    """Remove componentes substituídos por agrupamentos."""
    return [
        item
        for item in componentes
        if not _deve_remover_componente_territorio(
            item,
            turma_codigo,
            login,
            selecionados,
        )
    ]


def _adicionar_agrupamentos(
    componentes: list[dict],
    selecionados: AgrupamentosTerritorioSelecionados,
) -> list[dict]:
    """Adiciona agrupamentos ainda ausentes na lista."""
    codigos_existentes = {item["codigo"] for item in componentes}
    agrupamentos_para_adicionar = []
    for agrupamento in selecionados.agrupamentos:
        if agrupamento.cod_agrupamento in codigos_existentes:
            continue
        agrupamentos_para_adicionar.append(agrupamento_para_dict(agrupamento))
        codigos_existentes.add(agrupamento.cod_agrupamento)
    return agrupamentos_para_adicionar + componentes


def _atualizar_descricoes_outros_professores(
    componentes: list[dict],
    login: str,
    selecionados: AgrupamentosTerritorioSelecionados,
) -> None:
    """Atualiza descrições dos componentes de outros professores."""
    for item in componentes:
        codigo = item.get("codigo")
        descricao = (
            selecionados.descricoes_primeiros_codigos.get(codigo)
            if isinstance(codigo, int)
            else None
        )
        if item.get("professor") != login and descricao:
            item["descricao"] = descricao


def mesclar_agrupamentos_territorio(
    componentes: list[dict],
    using: str,
    login: str,
) -> list[dict]:
    """Substitui componentes de território agrupados pelo agrupamento.

    Args:
        componentes: Componentes já normalizados da turma/funcionário.
        using: Alias da conexão Django.
        login: RF do professor usado no filtro de atribuição.

    Returns:
        Lista de componentes com os agrupamentos de território aplicados.
    """
    turmas = _codigos_turmas_com_territorio(componentes)
    if not turmas:
        return componentes

    resultado = list(componentes)
    for turma_codigo in turmas:
        agrupamentos = _buscar_agrupamentos_da_turma(
            using,
            turma_codigo,
            login,
        )
        selecionados = _selecionar_agrupamentos(agrupamentos)
        if not selecionados.agrupamentos:
            continue

        resultado = _remover_componentes_agrupados(
            resultado,
            turma_codigo,
            login,
            selecionados,
        )
        resultado = _adicionar_agrupamentos(resultado, selecionados)
        _atualizar_descricoes_outros_professores(
            resultado,
            login,
            selecionados,
        )

    return resultado
