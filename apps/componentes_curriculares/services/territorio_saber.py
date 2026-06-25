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
    AtribuicaoTerritorioSaber,
    ComponenteTurma,
)


@dataclass
class AgrupamentosTerritorioSelecionados:
    """Armazena agrupamentos selecionados para recompor uma resposta.

    Attributes:
        agrupamentos: Agrupamentos que devem entrar no retorno.
        codigos_agrupados: Componentes contemplados pelos agrupamentos.
        primeiros_codigos: Primeiro componente de cada agrupamento.
        descricoes_primeiros_codigos: Descrição por primeiro componente.
    """

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
    ts = (agrupamento.desc_territorio_saber or "").strip()
    ep = (agrupamento.desc_experiencia_pedagogica or "").strip()
    descricao = f"{ts} - {ep}" if ep else ts
    if not descricao:
        descricao = " - "
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
    """Verifica se o agrupamento iniciou até a data informada.

    Args:
        agrupamento: Agrupamento de Território do Saber avaliado.
        data_base: Data de referência; None ignora o filtro de data.

    Returns:
        True quando o agrupamento pode ser considerado na data.
    """
    if data_base is None:
        return True
    return agrupamento.dt_inicio_atribuicao.date() <= data_base


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
    atribuicao: AtribuicaoTerritorioSaber,
) -> dict:
    """Formata atribuição única de território como componente.

    Args:
        componente: Vínculo turma-componente de Território do Saber.
        atribuicao: Atribuição do professor ao componente.

    Returns:
        Componente individual no formato interno de resposta.
    """
    descricao = _descricao_componente_territorio(componente)
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


def componente_sintetico_agrupado_para_dict(
    origem: AgrupamentoAtribuicaoTerritorioSaber,
    codigo_componente: int,
    componente: ComponenteTurma | None = None,
    atribuicao: AtribuicaoTerritorioSaber | None = None,
    professor: str | None = None,
) -> dict:
    """Formata componente filho criado a partir de um agrupamento.

    Args:
        origem: Agrupamento usado como origem da consulta.
        codigo_componente: Código do componente filho.
        componente: Vínculo turma-componente, quando disponível.
        atribuicao: Atribuição individual do componente, quando disponível.
        professor: Professor usado quando não há atribuição individual.

    Returns:
        Componente individual no formato interno de resposta.
    """
    descricao = (
        _descricao_componente_territorio(componente) if componente else " - "
    )
    professor_resposta = (
        atribuicao.professor
        if atribuicao
        else professor or origem.rf_professor
    )
    return {
        "codigo": codigo_componente,
        "codigo_componente_territorio_saber": codigo_componente,
        "codigo_componente_curricular_pai": None,
        "descricao": descricao,
        "regencia": False,
        "planejamento_regencia": False,
        "territorio_saber": True,
        "turma_codigo": origem.cod_turma,
        "exibir_componente_eol": False,
        "professor": professor_resposta,
        "codigos_territorios_agrupamento": [codigo_componente],
    }


def _descricao_componente_territorio(componente: ComponenteTurma) -> str:
    """Monta descrição contextual de um componente de território.

    Args:
        componente: Vínculo turma-componente de Território do Saber.

    Returns:
        Descrição contextual do componente na turma.
    """
    ts = componente.desc_territorio_saber or ""
    ep = componente.desc_experiencia_pedagogica or ""
    # Espelha o legado (DescricaoAgrupamentoTerritorioSaber): sempre
    # "{territorio} - {experiencia}", inclusive " - " quando ambos vazios.
    return f"{ts} - {ep}"


def _componente_nao_agrupado_para_dict(
    componente: ComponenteTurma,
    atribuicao: AtribuicaoTerritorioSaber,
) -> dict:
    """Formata atribuição única de território para resposta da turma.

    Args:
        componente: Vínculo turma-componente de Território do Saber.
        atribuicao: Atribuição do professor ao componente.

    Returns:
        Componente individual no formato interno de resposta.
    """
    return {
        "codigo": componente.componente_codigo,
        "codigo_componente_territorio_saber": (
            componente.codigo_componente_territorio_saber
            or componente.componente_codigo
        ),
        "codigo_componente_curricular_pai": None,
        "descricao": _descricao_componente_territorio(componente),
        "regencia": False,
        "planejamento_regencia": False,
        "territorio_saber": True,
        "turma_codigo": componente.turma_codigo,
        "exibir_componente_eol": False,
        "professor": atribuicao.professor,
        "codigos_territorios_agrupamento": [],
    }


def _codigos_turmas_com_territorio(componentes: list[dict]) -> set[object]:
    """Retorna turmas presentes em componentes de Território do Saber.

    Args:
        componentes: Componentes normalizados para resposta.

    Returns:
        Códigos de turma encontrados nos componentes de território.
    """
    return {
        item["turma_codigo"]
        for item in componentes
        if item.get("territorio_saber") and item.get("turma_codigo")
    }


def _codigos_territorio_do_login(
    componentes: list[dict],
    turma_codigo: object,
    login: str,
) -> set[object]:
    """Retorna códigos de território atribuídos a um login.

    Args:
        componentes: Componentes normalizados para resposta.
        turma_codigo: Código da turma usada como filtro.
        login: RF do professor usado como filtro.

    Returns:
        Códigos dos componentes de território do professor na turma.
    """
    # Território não informado ou não utilizável permanece como componente
    # comum e não entra no merge.
    return {
        item["codigo"]
        for item in componentes
        if item.get("territorio_saber")
        and item.get("codigo_componente_territorio_saber")
        and item.get("turma_codigo") == turma_codigo
        and item.get("professor") == login
    }


def _buscar_agrupamentos_da_turma(
    using: str,
    turma_codigo: object,
    login: str,
) -> Iterable[AgrupamentoAtribuicaoTerritorioSaber]:
    """Busca agrupamentos de território de uma turma e professor.

    Args:
        using: Alias da conexão Django.
        turma_codigo: Código da turma usada como filtro.
        login: RF do professor usado como filtro.

    Returns:
        Agrupamentos ordenados para seleção.
    """
    return (
        AgrupamentoAtribuicaoTerritorioSaber.objects.using(using)
        .filter(cod_turma=turma_codigo, rf_professor=login)
        .order_by(
            F("dt_fim_atribuicao").asc(nulls_first=True),
            "-dt_inicio_atribuicao",
        )
    )


def _buscar_componentes_agrupados_encerrados_por_professor(
    using: str,
    turma_codigo: object,
) -> dict[object, set[int]]:
    """Busca componentes cobertos por agrupamentos encerrados na turma.

    Args:
        using: Alias da conexão Django.
        turma_codigo: Código da turma usada como filtro.

    Returns:
        Mapa de professor para códigos cobertos por agrupamentos encerrados.
    """
    agrupamentos = (
        AgrupamentoAtribuicaoTerritorioSaber.objects.using(using)
        .filter(cod_turma=turma_codigo)
        .exclude(
            cod_motivo_disponibilizacao=MOTIVO_DISPONIBILIZACAO_FIM_ANO_LETIVO
        )
        .values_list("rf_professor", "cod_componentes_curriculares")
    )
    codigos_por_professor: dict[object, set[int]] = {}
    for professor, componentes_csv in agrupamentos:
        codigos = parse_csv(componentes_csv)
        if len(codigos) < 2:
            continue
        codigos_por_professor.setdefault(professor, set()).update(codigos)
    return codigos_por_professor


def _selecionar_agrupamentos(
    agrupamentos: Iterable[AgrupamentoAtribuicaoTerritorioSaber],
    codigos_territorio_login: set[object] | None = None,
) -> AgrupamentosTerritorioSelecionados:
    """Seleciona agrupamentos e consolida seus metadados.

    Args:
        agrupamentos: Agrupamentos candidatos a entrar no retorno.
        codigos_territorio_login: Componentes de território presentes na
            listagem do professor. Quando informado, apenas agrupamentos com
            ao menos um componente presente são selecionados.

    Returns:
        Agrupamentos selecionados e índices auxiliares.
    """
    selecionados = AgrupamentosTerritorioSelecionados()
    chaves_vistas: set[str | None] = set()

    for agrupamento in agrupamentos:
        codigos = parse_csv(agrupamento.cod_componentes_curriculares)
        if len(codigos) < 2:
            continue
        if (
            codigos_territorio_login is not None
            and not set(codigos) & codigos_territorio_login
        ):
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
    codigos_territorio_login: set[object],
    primeiros_codigos_outros_professores: set[tuple[object, int]],
    codigos_agrupados_encerrados_por_professor: dict[object, set[int]],
) -> bool:
    """Indica se um componente deve ser removido da resposta.

    Args:
        item: Componente normalizado avaliado.
        turma_codigo: Código da turma em processamento.
        login: RF do professor usado como filtro.
        selecionados: Agrupamentos selecionados para a turma.
        codigos_territorio_login: Componentes de território do professor.
        primeiros_codigos_outros_professores: Primeiro componente por
            professor.
        codigos_agrupados_encerrados_por_professor: Componentes cobertos por
            agrupamentos encerrados por professor.

    Returns:
        True quando o componente deve ser removido.
    """
    if not item.get("territorio_saber"):
        return False
    if item.get("turma_codigo") != turma_codigo:
        return False
    if item.get("professor") == login:
        return item.get("codigo") in codigos_territorio_login
    if item.get("codigo") in codigos_agrupados_encerrados_por_professor.get(
        item.get("professor"),
        set(),
    ):
        return True
    if item.get("codigo") not in codigos_territorio_login:
        return True
    if (
        item.get("professor") != login
        and (item.get("professor"), item.get("codigo"))
        not in primeiros_codigos_outros_professores
    ):
        return True
    if item.get("codigo") in selecionados.codigos_agrupados:
        return item.get("codigo") not in selecionados.primeiros_codigos
    return False


def _primeiros_codigos_outros_professores(
    componentes: list[dict],
    turma_codigo: object,
    login: str,
    codigos_territorio_login: set[object],
) -> set[tuple[object, int]]:
    """Retorna o primeiro componente de território por outro professor.

    Args:
        componentes: Componentes normalizados para resposta.
        turma_codigo: Código da turma em processamento.
        login: RF do professor usado como filtro.
        codigos_territorio_login: Componentes de território do professor.

    Returns:
        Pares de professor e primeiro código correlato.
    """
    codigos_por_professor: dict[object, list[int]] = {}
    for item in componentes:
        professor = item.get("professor")
        codigo = item.get("codigo")
        if (
            item.get("territorio_saber")
            and item.get("turma_codigo") == turma_codigo
            and professor != login
            and isinstance(codigo, int)
            and codigo in codigos_territorio_login
        ):
            codigos_por_professor.setdefault(professor, []).append(codigo)
    return {
        (professor, min(codigos))
        for professor, codigos in codigos_por_professor.items()
        if codigos
    }


def _remover_componentes_agrupados(
    componentes: list[dict],
    turma_codigo: object,
    login: str,
    selecionados: AgrupamentosTerritorioSelecionados,
    codigos_territorio_login: set[object],
    primeiros_codigos_outros_professores: set[tuple[object, int]],
    codigos_agrupados_encerrados_por_professor: dict[object, set[int]],
) -> list[dict]:
    """Remove componentes que não devem permanecer na resposta.

    Args:
        componentes: Componentes normalizados para resposta.
        turma_codigo: Código da turma em processamento.
        login: RF do professor usado como filtro.
        selecionados: Agrupamentos selecionados para a turma.
        codigos_territorio_login: Componentes de território do professor.
        primeiros_codigos_outros_professores: Primeiro componente por
            professor.
        codigos_agrupados_encerrados_por_professor: Componentes cobertos por
            agrupamentos encerrados por professor.

    Returns:
        Componentes restantes após a remoção.
    """
    return [
        item
        for item in componentes
        if not _deve_remover_componente_territorio(
            item,
            turma_codigo,
            login,
            selecionados,
            codigos_territorio_login,
            primeiros_codigos_outros_professores,
            codigos_agrupados_encerrados_por_professor,
        )
    ]


def _adicionar_agrupamentos(
    componentes: list[dict],
    selecionados: AgrupamentosTerritorioSelecionados,
) -> list[dict]:
    """Adiciona agrupamentos que ainda não estão na lista.

    Args:
        componentes: Componentes normalizados para resposta.
        selecionados: Agrupamentos selecionados para a turma.

    Returns:
        Componentes com agrupamentos adicionados no início da lista.
    """
    codigos_existentes = {item["codigo"] for item in componentes}
    agrupamentos_para_adicionar = []
    for agrupamento in selecionados.agrupamentos:
        if agrupamento.cod_agrupamento in codigos_existentes:
            continue
        agrupamentos_para_adicionar.append(agrupamento_para_dict(agrupamento))
        codigos_existentes.add(agrupamento.cod_agrupamento)
    return agrupamentos_para_adicionar + componentes


def _chave_agrupamento_atribuicao(
    componente: ComponenteTurma,
    atribuicao: AtribuicaoTerritorioSaber,
) -> tuple[object, ...]:
    """Retorna chave usada para identificar atribuição única.

    Args:
        componente: Vínculo turma-componente de Território do Saber.
        atribuicao: Atribuição do professor ao componente.

    Returns:
        Chave de agrupamento de atribuições de território.
    """
    return (
        componente.turma_codigo,
        atribuicao.codigo_territorio_saber,
        atribuicao.codigo_experiencia_pedagogica,
        atribuicao.professor,
        atribuicao.dt_atribuicao,
        (
            atribuicao.dt_disponibilizacao.date()
            if atribuicao.dt_disponibilizacao
            else None
        ),
    )


def _buscar_atribuicao_nao_agrupada(
    using: str,
    turma_codigo: object,
    codigo_componente: int,
) -> tuple[ComponenteTurma, AtribuicaoTerritorioSaber] | None:
    """Busca atribuição única de território para um componente.

    Args:
        using: Alias da conexão Django.
        turma_codigo: Código da turma usada como filtro.
        codigo_componente: Código do componente de território.

    Returns:
        Par componente/atribuição quando há atribuição única.
    """
    componentes = {
        componente.componente_codigo: componente
        for componente in ComponenteTurma.objects.using(using).filter(
            turma_codigo=turma_codigo,
            desc_territorio_saber__isnull=False,
        )
    }
    componente_alvo = componentes.get(codigo_componente)
    if not componente_alvo:
        return None

    atribuicoes = (
        AtribuicaoTerritorioSaber.objects.using(using)
        .filter(
            turma_codigo=turma_codigo,
            componente_codigo__in=componentes,
        )
        .order_by(
            "-dt_atribuicao",
            F("dt_disponibilizacao").desc(nulls_first=True),
        )
    )

    pares: list[tuple[ComponenteTurma, AtribuicaoTerritorioSaber]] = []
    contagem: dict[tuple[object, ...], int] = {}
    for atribuicao in atribuicoes:
        componente = componentes.get(atribuicao.componente_codigo)
        if componente is None:
            continue
        chave = _chave_agrupamento_atribuicao(componente, atribuicao)
        contagem[chave] = contagem.get(chave, 0) + 1
        pares.append((componente, atribuicao))

    duplicados: dict[
        tuple[object, ...],
        tuple[ComponenteTurma, AtribuicaoTerritorioSaber],
    ] = {}
    for componente, atribuicao in pares:
        if componente.componente_codigo != codigo_componente:
            continue
        chave = _chave_agrupamento_atribuicao(componente, atribuicao)
        if contagem[chave] == 1:
            return componente, atribuicao
        duplicados.setdefault(chave, (componente, atribuicao))

    return next(iter(duplicados.values()), None)


def _adicionar_atribuicoes_nao_agrupadas(
    componentes: list[dict],
    using: str,
    turma_codigo: object,
    codigos_componentes: set[object],
) -> list[dict]:
    """Adiciona atribuições únicas de território removidas da resposta.

    Args:
        componentes: Componentes normalizados para resposta.
        using: Alias da conexão Django.
        turma_codigo: Código da turma usada como filtro.
        codigos_componentes: Códigos removidos para tentar recompor.

    Returns:
        Componentes com atribuições únicas de território preservadas.
    """
    existentes = {
        (item.get("turma_codigo"), item.get("codigo"), item.get("professor"))
        for item in componentes
    }
    descricoes_existentes = {
        (
            item.get("turma_codigo"),
            item.get("professor"),
            item.get("descricao"),
        )
        for item in componentes
        if item.get("territorio_saber")
    }
    adicionados: list[dict] = []
    codigos = sorted(
        codigo for codigo in codigos_componentes if isinstance(codigo, int)
    )
    for codigo in codigos:
        atribuicao = _buscar_atribuicao_nao_agrupada(
            using,
            turma_codigo,
            codigo,
        )
        if atribuicao is None:
            continue
        item = _componente_nao_agrupado_para_dict(*atribuicao)
        chave = (item["turma_codigo"], item["codigo"], item["professor"])
        chave_descricao = (
            item["turma_codigo"],
            item["professor"],
            item["descricao"],
        )
        if chave in existentes or chave_descricao in descricoes_existentes:
            continue
        existentes.add(chave)
        descricoes_existentes.add(chave_descricao)
        adicionados.append(item)
    return componentes + adicionados


def _atualizar_descricoes_outros_professores(
    componentes: list[dict],
    login: str,
    selecionados: AgrupamentosTerritorioSelecionados,
) -> None:
    """Atualiza descrições dos componentes preservados na resposta.

    Args:
        componentes: Componentes normalizados para resposta.
        login: RF do professor usado como filtro.
        selecionados: Agrupamentos selecionados para a turma.
    """
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
        codigos_territorio_login = _codigos_territorio_do_login(
            resultado,
            turma_codigo,
            login,
        )
        agrupamentos = _buscar_agrupamentos_da_turma(
            using,
            turma_codigo,
            login,
        )
        selecionados = _selecionar_agrupamentos(
            agrupamentos,
            codigos_territorio_login,
        )
        if not selecionados.agrupamentos:
            continue

        primeiros_codigos_outros_professores = (
            _primeiros_codigos_outros_professores(
                resultado,
                turma_codigo,
                login,
                codigos_territorio_login,
            )
        )
        codigos_agrupados_encerrados_por_professor = (
            _buscar_componentes_agrupados_encerrados_por_professor(
                using,
                turma_codigo,
            )
        )
        resultado = _remover_componentes_agrupados(
            resultado,
            turma_codigo,
            login,
            selecionados,
            codigos_territorio_login,
            primeiros_codigos_outros_professores,
            codigos_agrupados_encerrados_por_professor,
        )
        resultado = _adicionar_agrupamentos(resultado, selecionados)
        resultado = _adicionar_atribuicoes_nao_agrupadas(
            resultado,
            using,
            turma_codigo,
            codigos_territorio_login,
        )
        _atualizar_descricoes_outros_professores(
            resultado,
            login,
            selecionados,
        )

    return resultado
