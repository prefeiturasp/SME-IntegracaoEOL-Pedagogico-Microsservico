"""Serviços de Território do Saber."""

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
    turmas = {
        item["turma_codigo"]
        for item in componentes
        if item.get("territorio_saber") and item.get("turma_codigo")
    }
    if not turmas:
        return componentes

    resultado = list(componentes)
    for turma_codigo in turmas:
        agrupamentos = (
            AgrupamentoAtribuicaoTerritorioSaber.objects.using(using)
            .filter(cod_turma=turma_codigo, rf_professor=login)
            .order_by(
                F("dt_fim_atribuicao").asc(nulls_first=True),
                "-dt_inicio_atribuicao",
            )
        )

        # Mantém o agrupamento mais recente por conjunto de componentes e
        # ignora atribuições de componente único.
        selecionados: list[AgrupamentoAtribuicaoTerritorioSaber] = []
        chaves_vistas: set[str | None] = set()
        codigos_agrupados: set[int] = set()
        primeiros_codigos_agrupados: set[int] = set()
        descricoes_primeiros_codigos: dict[int, str] = {}
        for agrupamento in agrupamentos:
            codigos = parse_csv(agrupamento.cod_componentes_curriculares)
            if len(codigos) < 2:
                continue
            if agrupamento.cod_componentes_curriculares in chaves_vistas:
                continue
            chaves_vistas.add(agrupamento.cod_componentes_curriculares)
            selecionados.append(agrupamento)
            codigos_agrupados.update(codigos)
            primeiros_codigos_agrupados.add(codigos[0])
            descricoes_primeiros_codigos[codigos[0]] = agrupamento_para_dict(
                agrupamento
            )["descricao"]

        if not selecionados:
            continue

        resultado = [
            item
            for item in resultado
            if not (
                item.get("territorio_saber")
                and item.get("turma_codigo") == turma_codigo
                and (
                    (
                        item.get("professor") == login
                        and item.get("codigo") in codigos_agrupados
                    )
                    or (
                        item.get("professor") != login
                        and item.get("codigo")
                        not in primeiros_codigos_agrupados
                    )
                )
            )
        ]

        codigos_existentes = {item["codigo"] for item in resultado}
        agrupamentos_para_adicionar = []
        for agrupamento in selecionados:
            if agrupamento.cod_agrupamento not in codigos_existentes:
                agrupamentos_para_adicionar.append(
                    agrupamento_para_dict(agrupamento)
                )
                codigos_existentes.add(agrupamento.cod_agrupamento)
        resultado = agrupamentos_para_adicionar + resultado
        for item in resultado:
            codigo = item.get("codigo")
            descricao = (
                descricoes_primeiros_codigos.get(codigo)
                if isinstance(codigo, int)
                else None
            )
            if item.get("professor") != login and descricao:
                item["descricao"] = descricao

    return resultado
