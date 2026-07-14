"""Repositório de componentes curriculares."""

from collections.abc import Iterable
from datetime import date, datetime

from django.db import connections
from django.db.models import F, Q, QuerySet

from apps.componentes_curriculares.constants import (
    CODIGO_COMPONENTE_REGENCIA_CLASSE_INFANTIL,
    DESCRICAO_COMPONENTE_REGENCIA_CLASSE_INFANTIL,
    MODALIDADE_EJA,
    MOTIVO_DISPONIBILIZACAO_FIM_ANO_LETIVO,
)
from apps.componentes_curriculares.models import (
    AgrupamentoAtribuicaoTerritorioSaber,
    AtribuicaoTerritorioSaber,
    ComponenteCurricular,
    ComponenteCurricularPlanejamentoRegencia,
    ComponenteTurma,
    GradeComponenteCurricular,
)
from apps.componentes_curriculares.queries import (
    SQL_COMPONENTES_GRADE_POR_UE_MODALIDADE_ANO,
    SQL_COMPONENTES_POR_LISTA_TURMAS,
    SQL_COMPONENTES_POR_LISTA_TURMAS_INCLUI_EXTINTAS,
    SQL_COMPONENTES_SEM_ATRIBUICAO,
    SQL_COMPONENTES_SIMPLIFICADOS_POR_TURMAS,
    SQL_COMPONENTES_TURMA_COM_ATRIBUICAO,
    SQL_COMPONENTES_TURMA_PROGRAMA,
    SQL_COMPONENTES_TURMAS_BRUTOS,
    SQL_FILTRO_ATRIBUICAO_POR_TURMA,
    SQL_FILTRO_ATRIBUICAO_VIGENTE,
    SQL_LISTAGEM_HISTORICO_HISTORICA,
    SQL_LISTAGEM_HISTORICO_VIGENTE,
    SQL_LISTAGEM_JOIN_PROFESSOR,
    SQL_LISTAGEM_TURMAS_COMPONENTES,
    SQL_VIGENCIA_COMPONENTES,
)
from apps.componentes_curriculares.services.territorio_saber import (
    agrupamento_para_dict,
    agrupamento_vigente_na_data,
    atribuicao_nao_agrupada_para_dict,
    componente_sintetico_agrupado_para_dict,
    componentes_agrupados_sao_subconjunto,
    mesclar_agrupamentos_territorio,
    parse_csv,
)


def _raw(sql: str, params: list, using: str = "default") -> list[dict]:
    """Executa SQL bruto e retorna linhas como dicionários.

    Args:
        sql: Consulta SQL a executar.
        params: Parâmetros da consulta.
        using: Alias da conexão Django.

    Returns:
        Lista de linhas com nomes de colunas como chaves.
    """
    with connections[using].cursor() as cursor:
        cursor.execute(sql, params)
        cols = [c[0] for c in cursor.description]
        return [
            dict(zip(cols, row, strict=False)) for row in cursor.fetchall()
        ]


def _componente_para_dict(row: dict) -> dict:
    """Normaliza campos computados de componente curricular.

    Args:
        row: Linha retornada pela consulta.

    Returns:
        Componente curricular no formato interno de resposta.
    """
    return {
        **row,
        "codigo_componente_territorio_saber": (
            row.get("codigo_componente_territorio_saber") or 0
        ),
        "exibir_componente_eol": row.get("exibir_componente_eol", False),
        "codigos_territorios_agrupamento": [],
    }


def _grade_para_componente(row: dict) -> dict:
    """Retorna componente curricular a partir de linha de grade.

    Args:
        row: Linha de grade curricular.

    Returns:
        Componente curricular no formato interno de resposta.
    """
    item = {
        "codigo": row["codigo_componente_curricular"],
        "codigo_componente_territorio_saber": 0,
        "codigo_componente_curricular_pai": row.get(
            "codigo_componente_curricular_pai"
        ),
        "descricao": row["descricao_componente_curricular"],
        "regencia": row.get("regencia", False),
        "planejamento_regencia": False,
        "territorio_saber": False,
        "turma_codigo": None,
        "exibir_componente_eol": False,
        "professor": None,
        "codigos_territorios_agrupamento": [],
    }
    return _aplicar_regra_regencia_classe_infantil(item)


def _aplicar_regra_regencia_classe_infantil(item: dict) -> dict:
    """Normaliza a regência de classe infantil.

    Args:
        item: Componente curricular a normalizar.

    Returns:
        Componente curricular normalizado.
    """
    if item["codigo"] == CODIGO_COMPONENTE_REGENCIA_CLASSE_INFANTIL:
        # Compatibiliza o componente infantil com o retorno esperado pelo
        # domínio pedagógico.
        item["codigo_componente_curricular_pai"] = (
            CODIGO_COMPONENTE_REGENCIA_CLASSE_INFANTIL
        )
        item["descricao"] = DESCRICAO_COMPONENTE_REGENCIA_CLASSE_INFANTIL
        item["regencia"] = True
    return item


def _item_listagem_para_dict(componente: dict, info: dict) -> dict:
    """Monta um item da listagem turma×componente para resposta.

    Args:
        componente: Componente já processado pelo Território do Saber.
        info: Dados da turma associados ao componente.

    Returns:
        Item da listagem no formato de resposta (snake_case).
    """
    turno = info.get("turno")
    return {
        "id": None,
        "turma_codigo": componente.get("turma_codigo"),
        "modalidade": info.get("modalidade"),
        "nome_turma": info.get("nome_turma"),
        "ano": info.get("ano"),
        "complemento_turma_eja": info.get("complemento_turma_eja") or "",
        "nome_componente_curricular": componente.get("descricao"),
        "componente_curricular_codigo": componente.get("codigo"),
        "turno": str(turno) if turno is not None else None,
        "territorio_saber": componente.get("territorio_saber", False),
        "componente_curricular_territorio_saber_codigo": (
            componente.get("codigo_componente_territorio_saber") or 0
        ),
        # Atributos cadastrais da turma (mesma turma repetida por componente).
        "ano_letivo": info.get("ano_letivo"),
        "tipo_turma": info.get("tipo_turma"),
        "tipo_escola": info.get("tipo_escola"),
        "situacao_turma_escola": info.get("situacao"),
        "data_status_turma_escola": info.get("data_status_turma_escola"),
        "codigo_escola": info.get("ue_codigo"),
        "etapa_ensino": info.get("etapa_ensino"),
        "ciclo_ensino": info.get("ciclo_ensino"),
        "serie_ensino": info.get("serie_ensino"),
        "tipo_grade_programa": info.get("tipo_grade_programa"),
        "codigo_grade_programa": info.get("codigo_grade_programa"),
        "descricao_grade_programa": info.get("descricao_grade_programa"),
        "data_inicio_turma": info.get("data_inicio_turma"),
        "data_fim_turma": info.get("data_fim"),
        "data_atualizacao": info.get("data_atualizacao"),
        "duracao_turno": info.get("duracao_turno"),
        "ensino_especial": info.get("ensino_especial"),
        "semestre": info.get("semestre"),
        "extinta": info.get("extinta"),
    }


def _normalizar_componente_turma(row: dict) -> dict:
    """Normaliza um componente vinculado a uma turma.

    Args:
        row: Linha retornada pelas consultas de turma.

    Returns:
        Componente no formato de resposta, com regência infantil consolidada.
    """
    item = _componente_para_dict(row)
    if (
        item.get("codigo_componente_curricular_pai")
        == CODIGO_COMPONENTE_REGENCIA_CLASSE_INFANTIL
    ):
        item["codigo"] = CODIGO_COMPONENTE_REGENCIA_CLASSE_INFANTIL
    return _aplicar_regra_regencia_classe_infantil(item)


def _normalizar_componente_atribuido(row: dict) -> dict:
    """Normaliza um componente atribuído a funcionário.

    Args:
        row: Linha retornada pela consulta.

    Returns:
        Componente preservando o código retornado pela atribuição.
    """
    item = _componente_para_dict(row)
    if (
        item.get("codigo_componente_curricular_pai")
        == CODIGO_COMPONENTE_REGENCIA_CLASSE_INFANTIL
    ):
        item["regencia"] = True
    return item


def _int_or_none(value: object) -> int | None:
    """Converta valor para inteiro quando possível.

    Args:
        value: Valor de entrada.

    Returns:
        Inteiro convertido ou None.
    """
    if value is None:
        return None
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


def _componentes_planejamento_regencia(
    row: dict,
    using: str,
) -> list[ComponenteCurricular]:
    """Busca componentes de planejamento de regência aplicáveis.

    Args:
        row: Linha com dados de turma e regência.
        using: Alias da conexão Django.

    Returns:
        Componentes curriculares de planejamento na ordem configurada.
    """
    turno = _int_or_none(row.get("turno_turma"))
    ano = _int_or_none(row.get("ano_turma"))

    qs = ComponenteCurricularPlanejamentoRegencia.objects.using(using)
    regras = list(qs.filter(turno=turno, ano=ano))
    if not regras:
        # Usa a regra genérica quando não há configuração específica.
        regras = list(qs.filter(turno__isnull=True, ano__isnull=True))

    codigos = [r.id_componente_curricular for r in regras]
    if not codigos:
        return []

    componentes = (
        ComponenteCurricular.objects.using(using)
        .filter(codigo__in=codigos)
        .in_bulk(field_name="codigo")
    )
    return [componentes[codigo] for codigo in codigos if codigo in componentes]


def _expandir_planejamento_regencia(
    rows: list[dict],
    using: str,
) -> list[dict]:
    """Retorna componentes de regência expandidos para planejamento.

    Args:
        rows: Linhas de componentes da turma.
        using: Alias da conexão Django.

    Returns:
        Lista de componentes com regência substituída por planejamento.
    """
    resultado: list[dict] = []
    vistos: set[tuple[object, object]] = set()

    for row in rows:
        item_normalizado = _normalizar_componente_turma(row)
        if not item_normalizado.get("regencia"):
            item_normalizado["professor"] = None
            key = (
                item_normalizado.get("turma_codigo"),
                item_normalizado.get("codigo"),
            )
            if key not in vistos:
                vistos.add(key)
                resultado.append(item_normalizado)
            continue

        for componente in _componentes_planejamento_regencia(
            item_normalizado,
            using,
        ):
            item = _componente_para_dict(
                {
                    "codigo": componente.codigo,
                    "codigo_componente_territorio_saber": 0,
                    "codigo_componente_curricular_pai": None,
                    "descricao": componente.descricao,
                    "regencia": False,
                    "planejamento_regencia": True,
                    "territorio_saber": False,
                    "turma_codigo": row.get("turma_codigo"),
                    "tipo_escola": row.get("tipo_escola"),
                    "ano_letivo": row.get("ano_letivo"),
                    "turno_turma": row.get("turno_turma"),
                    "ano_turma": row.get("ano_turma"),
                    "professor": None,
                }
            )
            key = (
                item.get("turma_codigo"),
                item.get("codigo"),
            )
            if key not in vistos:
                vistos.add(key)
                resultado.append(item)

    return resultado


class ComponentesRepository:
    """Executa consultas ORM para componentes curriculares."""

    _DB = "default"

    @staticmethod
    def _ordenar_agrupamentos_legado(
        queryset: QuerySet[AgrupamentoAtribuicaoTerritorioSaber],
    ) -> QuerySet[AgrupamentoAtribuicaoTerritorioSaber]:
        """Ordena agrupamentos para seleção determinística.

        Args:
            queryset: QuerySet de agrupamentos.

        Returns:
            QuerySet ordenado.
        """
        return queryset.order_by(
            "-dt_inicio_atribuicao",
            F("dt_fim_atribuicao").desc(nulls_first=True),
            "-id",
        )

    @staticmethod
    def _tem_empate_perfeito_agrupamento(
        candidatos: list[AgrupamentoAtribuicaoTerritorioSaber],
    ) -> bool:
        """Indica se os candidatos diferem apenas pelo professor.

        Args:
            candidatos: Agrupamentos candidatos ao mesmo código.

        Returns:
            True quando todos compartilham os mesmos metadados de vigência e
            agrupamento.
        """
        if len(candidatos) < 2:
            return False
        referencia = candidatos[0]
        return all(
            candidato.cod_turma == referencia.cod_turma
            and candidato.cod_territorio_saber
            == referencia.cod_territorio_saber
            and candidato.cod_experiencia_pedagogica
            == referencia.cod_experiencia_pedagogica
            and candidato.cod_componentes_curriculares
            == referencia.cod_componentes_curriculares
            and candidato.dt_inicio_atribuicao
            == referencia.dt_inicio_atribuicao
            and candidato.dt_fim_atribuicao == referencia.dt_fim_atribuicao
            and candidato.cod_motivo_disponibilizacao
            == referencia.cod_motivo_disponibilizacao
            for candidato in candidatos[1:]
        )

    def _professores_atribuicoes_agrupamento(
        self,
        agrupamento: AgrupamentoAtribuicaoTerritorioSaber,
        atribuicoes_por_chave: (
            dict[tuple[str, int], AtribuicaoTerritorioSaber] | None
        ) = None,
    ) -> set[str]:
        """Retorna professores com atribuição individual no agrupamento.

        Args:
            agrupamento: Agrupamento avaliado.
            atribuicoes_por_chave: Atribuições pré-carregadas por turma e
                componente.

        Returns:
            RFs de professores encontrados nas atribuições individuais.
        """
        if not agrupamento.cod_turma:
            return set()

        componentes = parse_csv(agrupamento.cod_componentes_curriculares)
        if not componentes:
            return set()

        if atribuicoes_por_chave is not None:
            return {
                atribuicao.professor
                for codigo in componentes
                if (
                    atribuicao := atribuicoes_por_chave.get(
                        (agrupamento.cod_turma, codigo)
                    )
                )
                and atribuicao.professor
            }

        professores = (
            AtribuicaoTerritorioSaber.objects.using(self._DB)
            .filter(
                turma_codigo=agrupamento.cod_turma,
                componente_codigo__in=componentes,
            )
            .exclude(professor__isnull=True)
            .values_list("professor", flat=True)
        )
        return {professor for professor in professores if professor}

    def _selecionar_agrupamento_resposta(
        self,
        candidatos: list[AgrupamentoAtribuicaoTerritorioSaber],
        atribuicoes_por_chave: (
            dict[tuple[str, int], AtribuicaoTerritorioSaber] | None
        ) = None,
    ) -> AgrupamentoAtribuicaoTerritorioSaber | None:
        """Seleciona a linha que representa o agrupamento na resposta.

        Args:
            candidatos: Linhas candidatas do mesmo `cod_agrupamento`.
            atribuicoes_por_chave: Atribuições individuais pré-carregadas.

        Returns:
            Agrupamento selecionado ou None.
        """
        if not candidatos:
            return None

        if self._tem_empate_perfeito_agrupamento(candidatos):
            professores_atribuicoes = (
                self._professores_atribuicoes_agrupamento(
                    candidatos[0],
                    atribuicoes_por_chave,
                )
            )
            if professores_atribuicoes:
                for candidato in candidatos:
                    if candidato.rf_professor not in professores_atribuicoes:
                        return candidato

        return candidatos[0]

    def listar_por_turma_funcionario(
        self,
        codigo_turma: str,
        login: str,
        incluir_territorios_outros_professores: bool = False,
    ) -> list[dict]:
        """Lista componentes por turma e funcionário.

        Args:
            codigo_turma: Código da turma.
            login: Login (RF) do funcionário.
            incluir_territorios_outros_professores: Inclui componentes de
                Território do Saber atribuídos a outros professores da turma.

        Returns:
            Lista de componentes da turma para o funcionário.
        """
        filtro_professor = "ac.professor = %s"
        params: list = [login, codigo_turma]
        if incluir_territorios_outros_professores:
            filtro_professor = (
                "(ac.professor = %s OR "
                "(ct.codigo_componente_territorio_saber IS NOT NULL "
                "AND ac.professor <> %s))"
            )
            params = [login, login, codigo_turma]
        sql = (
            f"{SQL_COMPONENTES_TURMA_COM_ATRIBUICAO}"
            f" WHERE {filtro_professor} AND ct.turma_codigo = %s"
            f"{SQL_FILTRO_ATRIBUICAO_POR_TURMA}"
        )
        rows = _raw(sql, params, self._DB)
        resultado: list[dict] = []
        vistos: set[tuple[object, object, object]] = set()
        for row in rows:
            item = _normalizar_componente_atribuido(row)
            key = (
                item.get("turma_codigo"),
                item.get("codigo"),
                item.get("professor"),
            )
            if key not in vistos:
                vistos.add(key)
                resultado.append(item)
        return mesclar_agrupamentos_territorio(resultado, self._DB, login)

    def listar_por_funcionario(
        self,
        login: str,
    ) -> list[dict]:
        """Lista os componentes do funcionário no ano letivo corrente.

        Args:
            login: Login (RF) do funcionário.

        Returns:
            Lista deduplicada de componentes do funcionário.
        """
        sql = (
            f"{SQL_COMPONENTES_TURMA_COM_ATRIBUICAO}"
            " WHERE ac.professor = %s AND ac.ano_letivo = %s"
            f"{SQL_FILTRO_ATRIBUICAO_VIGENTE}"
        )
        rows = _raw(sql, [login, date.today().year], self._DB)

        # Resolve componentes pais para substituir o código do filho.
        codigos_pai = {
            r["codigo_componente_curricular_pai"]
            for r in rows
            if r.get("codigo_componente_curricular_pai")
        }
        componentes_pai = (
            ComponenteCurricular.objects.using(self._DB)
            .filter(codigo__in=codigos_pai)
            .in_bulk(field_name="codigo")
            if codigos_pai
            else {}
        )

        componentes: list[dict] = []
        for r in rows:
            r["exibir_componente_eol"] = False
            item = _componente_para_dict(r)
            pai = item.get("codigo_componente_curricular_pai")
            componente_pai = componentes_pai.get(pai)
            if componente_pai:
                item["codigo"] = componente_pai.codigo
                item["descricao"] = componente_pai.descricao

            item = _aplicar_regra_regencia_classe_infantil(item)
            componentes.append(item)

        seen: set[object] = set()
        result: list[dict] = []
        for item in componentes:
            key = (
                item.get("codigo_componente_curricular_pai") or item["codigo"]
            )

            if key not in seen:
                seen.add(key)
                item["professor"] = None
                result.append(item)

        return result

    def listar_planejamento_por_turma_funcionario(
        self,
        codigo_turma: str,
        login: str,
    ) -> list[dict]:
        """Lista componentes da turma aplicando planejamento de regência.

        Args:
            codigo_turma: Código da turma.
            login: Login (RF) do funcionário.

        Returns:
            Lista de componentes com regência expandida para planejamento.
        """
        sql = (
            f"{SQL_COMPONENTES_TURMA_COM_ATRIBUICAO}"
            " WHERE ac.professor = %s AND ct.turma_codigo = %s"
            f"{SQL_FILTRO_ATRIBUICAO_POR_TURMA}"
        )
        rows = _raw(sql, [login, codigo_turma], self._DB)
        for row in rows:
            row["exibir_componente_eol"] = False
        componentes = _expandir_planejamento_regencia(rows, self._DB)
        return mesclar_agrupamentos_territorio(componentes, self._DB, login)

    def listar_regencia_por_ano_turma(
        self,
        ano_turma: int,
    ) -> list[dict]:
        """Lista componentes de regência por ano de turma.

        Args:
            ano_turma: Ano escolar da turma.

        Returns:
            Lista de componentes de regência no formato de resposta.
        """
        filtro: dict[str, object] = (
            {"ano__isnull": True} if ano_turma <= 0 else {"ano": ano_turma}
        )
        codigos = list(
            ComponenteCurricularPlanejamentoRegencia.objects.using(self._DB)
            .filter(**filtro)
            .order_by("id_componente_curricular")
            .values_list("id_componente_curricular", flat=True)
        )
        componentes = (
            ComponenteCurricular.objects.using(self._DB)
            .filter(codigo__in=codigos)
            .in_bulk(field_name="codigo")
        )
        componentes_ordenados = [
            componentes[codigo] for codigo in codigos if codigo in componentes
        ]

        return [
            {
                "ano_turma": None,
                "ano_letivo": 0,
                "codigo": c.codigo,
                "codigo_componente_territorio_saber": 0,
                "descricao": c.descricao,
                "territorio_saber": False,
                "tipo_escola": None,
                "turno_turma": 0,
                "componente_planejamento_regencia": False,
                "turma_codigo": None,
                "professor": None,
                "inicio_atribuicao": None,
                "fim_atribuicao": None,
            }
            for c in componentes_ordenados
        ]

    def turma_possui_componente_pap(
        self,
        codigo_turma: str,
        login: str,
    ) -> bool:
        """Verifica se a turma possui componente PAP para o funcionário.

        Args:
            codigo_turma: Código da turma.
            login: Login (RF) do funcionário.

        Returns:
            True quando há componente PAP atribuído ao funcionário na turma.
        """
        rows = _raw(
            """
            SELECT EXISTS (
                SELECT 1
                  FROM atribuicao_componente ac
                  JOIN turma t
                    ON t.codigo::varchar = ac.turma_codigo
                  JOIN componente_curricular_pap pap
                    ON pap.id_componente_curricular = ac.componente_codigo
                 WHERE ac.turma_codigo = %s
                   AND ac.professor = %s
                   AND ac.dt_cancelamento IS NULL
                   AND (
                         ac.dt_disponibilizacao >= make_date(
                             t.ano_letivo,
                             2,
                             5
                         )
                         OR ac.dt_disponibilizacao IS NULL
                         OR ac.cd_motivo_disponibilizacao = %s
                       )
                 LIMIT 1
            ) AS possui
            """,
            [
                codigo_turma,
                login,
                MOTIVO_DISPONIBILIZACAO_FIM_ANO_LETIVO,
            ],
            self._DB,
        )
        return bool(rows and rows[0]["possui"])

    def listar_por_ue_modalidade_ano_e_anos_escolares(
        self,
        ue_codigo: str,
        modalidade: int,
        ano_letivo: int,
        anos_escolares: list[str],
    ) -> list[dict]:
        """Lista componentes da grade por UE, modalidade, ano e séries.

        Args:
            ue_codigo: Código da unidade educacional.
            modalidade: Código da modalidade de ensino.
            ano_letivo: Ano letivo consultado.
            anos_escolares: Séries a serem filtradas.

        Returns:
            Lista de componentes da grade curricular.
        """
        sql = SQL_COMPONENTES_GRADE_POR_UE_MODALIDADE_ANO
        params: list = [ue_codigo, modalidade, ano_letivo]
        if anos_escolares:
            placeholders = ",".join(["%s"] * len(anos_escolares))
            sql += f" AND t.ano IN ({placeholders})"
            params.extend(anos_escolares)
        rows = _raw(sql, params, self._DB)
        componentes = [_grade_para_componente(r) for r in rows]
        return sorted(componentes, key=lambda c: c["codigo"])

    def listar_turma_programa_por_ue_modalidade_ano(
        self,
        ue_codigo: str,
        modalidade: int,
        ano_letivo: int,
    ) -> list[dict]:
        """Lista componentes de turmas programa por UE, modalidade e ano.

        Args:
            ue_codigo: Código da unidade educacional.
            modalidade: Código da modalidade de ensino.
            ano_letivo: Ano letivo consultado.

        Returns:
            Lista de componentes de turmas programa.
        """
        modalidades_validas = {1, 3, 4, 5, 6}
        if modalidade not in modalidades_validas:
            return []

        sql = SQL_COMPONENTES_TURMA_PROGRAMA
        params: list = [ue_codigo, ano_letivo]

        if modalidade == 1:
            series = (23, 24, 25, 26, 116, 117, 118, 119, 225, 297)
            placeholders = ",".join(["%s"] * len(series))
            sql += f" AND t.codigo_serie_ensino IN ({placeholders})"
            params.extend(series)

        rows = _raw(sql, params, self._DB)
        componentes = [_grade_para_componente(r) for r in rows]
        return sorted(componentes, key=lambda c: c["codigo"])

    def listar_por_ue_e_turmas(
        self,
        ue_id: str,
        turmas: list[str],
    ) -> list[dict]:
        """Lista componentes simplificados por lista de turmas.

        Args:
            ue_id: Código da unidade educacional.
            turmas: Códigos das turmas a consultar.

        Returns:
            Lista de componentes simplificados das turmas.
        """
        sql = SQL_COMPONENTES_SIMPLIFICADOS_POR_TURMAS
        params: list = []
        if ue_id and ue_id != "-99":
            sql += " AND t.ue_codigo = %s"
            params.append(ue_id)
        if turmas:
            placeholders = ",".join(["%s"] * len(turmas))
            sql += f" AND ct.turma_codigo IN ({placeholders})"
            params.extend(turmas)
        sql += " ORDER BY cc.descricao"
        return _raw(sql, params, self._DB)

    @staticmethod
    def _info_turma_listagem(row: dict) -> dict:
        """Extrai dados de turma que acompanham cada componente na listagem.

        Args:
            row: Linha bruta da consulta de listagem turma×componente.

        Returns:
            Dados de turma usados para recompor o retorno após o território.
        """
        modalidade = row.get("modalidade")
        complemento = row.get("descricao_grade_programa") or ""
        return {
            "modalidade": modalidade,
            "nome_turma": row.get("nome_turma"),
            "ano": row.get("ano_turma"),
            "turno": row.get("tipo_turno"),
            "complemento_turma_eja": (
                complemento if modalidade == MODALIDADE_EJA else ""
            ),
            "ano_letivo": row.get("ano_letivo"),
            "tipo_turma": row.get("tipo_turma"),
            "tipo_escola": row.get("tipo_escola"),
            "situacao": row.get("situacao"),
            "data_status_turma_escola": row.get("data_status_turma_escola"),
            "ue_codigo": row.get("ue_codigo"),
            "etapa_ensino": row.get("codigo_etapa_ensino"),
            "ciclo_ensino": row.get("codigo_ciclo_ensino"),
            "serie_ensino": row.get("serie_ensino"),
            "tipo_grade_programa": row.get("tipo_grade_programa"),
            "codigo_grade_programa": row.get("codigo_grade_programa"),
            "descricao_grade_programa": row.get("descricao_grade_programa"),
            "data_inicio_turma": row.get("data_inicio_turma"),
            "data_fim": row.get("data_fim"),
            "data_atualizacao": row.get("data_atualizacao"),
            "duracao_turno": row.get("turno_turma"),
            "ensino_especial": row.get("ensino_especial"),
            "semestre": row.get("semestre"),
            "extinta": row.get("extinta"),
        }

    def _agrupar_componentes_listagem(
        self,
        rows: list[dict],
    ) -> tuple[list[dict], dict[object, dict]]:
        """Deduplica componentes e coleta os dados de turma da listagem.

        Args:
            rows: Linhas brutas da consulta de listagem turma×componente.

        Returns:
            Par com os componentes deduplicados e os dados por turma.
        """
        turma_info: dict[object, dict] = {}
        componentes: list[dict] = []
        vistos: set[tuple[object, object, object]] = set()
        for row in rows:
            turma_info.setdefault(
                row["turma_codigo"],
                self._info_turma_listagem(row),
            )
            item = _normalizar_componente_turma(row)
            chave = (
                item.get("turma_codigo"),
                item.get("codigo"),
                item.get("professor"),
            )
            if chave not in vistos:
                vistos.add(chave)
                componentes.append(item)
        return componentes, turma_info

    @staticmethod
    def _montar_itens_listagem(
        componentes: list[dict],
        turma_info: dict[object, dict],
        anos_infantil_desconsiderar: list[str] | None,
    ) -> list[dict]:
        """Monta os itens finais da listagem turma×componente.

        Args:
            componentes: Componentes já com Território do Saber aplicado.
            turma_info: Dados de turma indexados pelo código da turma.
            anos_infantil_desconsiderar: Anos de turma removidos do retorno.

        Returns:
            Itens de listagem deduplicados, no formato de resposta.
        """
        anos_ignorar = set(anos_infantil_desconsiderar or [])
        itens: list[dict] = []
        chaves_vistas: set[tuple] = set()
        for componente in componentes:
            info = turma_info.get(componente.get("turma_codigo"), {})
            if anos_ignorar and info.get("ano") in anos_ignorar:
                continue
            item = _item_listagem_para_dict(componente, info)
            chave = (
                item["turma_codigo"],
                item["modalidade"],
                item["nome_turma"],
                item["nome_componente_curricular"],
                item["ano"],
                item["complemento_turma_eja"],
                item["turno"],
                item["componente_curricular_codigo"],
            )
            if chave in chaves_vistas:
                continue
            chaves_vistas.add(chave)
            itens.append(item)
        return itens

    def listar_turmas_componentes_por_ue_modalidade_ano(
        self,
        ue_codigo: str,
        modalidade: int,
        ano_letivo: int,
        codigo_turma: int | None = None,
        eh_professor: bool = False,
        codigo_rf: str | None = None,
        considera_historico: bool = False,
        periodo_escolar_inicio: datetime | None = None,
        anos_infantil_desconsiderar: list[str] | None = None,
    ) -> list[dict]:
        """Lista componentes por turma para UE, modalidade e ano letivo.

        Aplica a substituição de Território do Saber. Quando `eh_professor`
        é falso, o território roda no modo gestor (sem RF), agregando os
        agrupamentos de todos os professores da turma.

        Args:
            ue_codigo: Código da unidade educacional.
            modalidade: Código da modalidade de ensino.
            ano_letivo: Ano letivo consultado.
            codigo_turma: Filtra por uma turma específica quando informado.
            eh_professor: Restringe os componentes ao RF informado.
            codigo_rf: RF do professor usado no filtro e no território.
            considera_historico: Inclui turmas históricas (situação C/E).
            periodo_escolar_inicio: Início do período escolar para turmas
                extintas quando `considera_historico` é verdadeiro.
            anos_infantil_desconsiderar: Anos de turma removidos do retorno.

        Returns:
            Itens de listagem turma×componente com território aplicado.
        """
        professor_select = "ac.professor" if eh_professor else "NULL"
        professor_join = SQL_LISTAGEM_JOIN_PROFESSOR if eh_professor else ""
        params: list = [ue_codigo, ano_letivo, modalidade]
        if eh_professor:
            params.append(codigo_rf)

        codigo_turma_clause = ""
        if codigo_turma:
            codigo_turma_clause = "AND t.codigo = %s"
            params.append(codigo_turma)

        if considera_historico:
            historico_clause = SQL_LISTAGEM_HISTORICO_HISTORICA
            params.append(periodo_escolar_inicio)
        else:
            historico_clause = SQL_LISTAGEM_HISTORICO_VIGENTE

        sql = SQL_LISTAGEM_TURMAS_COMPONENTES.format(
            professor_select=professor_select,
            professor_join=professor_join,
            codigo_turma_clause=codigo_turma_clause,
            historico_clause=historico_clause,
        )
        rows = _raw(sql, params, self._DB)
        componentes, turma_info = self._agrupar_componentes_listagem(rows)

        login = codigo_rf if eh_professor else None
        componentes = mesclar_agrupamentos_territorio(
            componentes,
            self._DB,
            login,
        )

        return self._montar_itens_listagem(
            componentes,
            turma_info,
            anos_infantil_desconsiderar,
        )

    def listar_por_lista_turmas(
        self,
        codigos_turmas: list[str],
        adicionar_componentes_planejamento: bool = True,
    ) -> list[dict]:
        """Lista componentes de múltiplas turmas para planejamento.

        Args:
            codigos_turmas: Códigos das turmas consultadas.
            adicionar_componentes_planejamento: Quando True, expande
                regência com os componentes de planejamento.

        Returns:
            Lista de componentes das turmas informadas.
        """
        return self._listar_por_lista_turmas(
            SQL_COMPONENTES_POR_LISTA_TURMAS,
            codigos_turmas,
            adicionar_componentes_planejamento,
        )

    def listar_por_lista_turmas_incluindo_extintas(
        self,
        codigos_turmas: list[str],
        adicionar_componentes_planejamento: bool = True,
    ) -> list[dict]:
        """Lista componentes de múltiplas turmas, incluindo turmas extintas.

        Igual a ``listar_por_lista_turmas``, mas não exclui turmas extintas —
        usada pela consulta de disciplinas por turma para manter paridade com
        o legado.

        Args:
            codigos_turmas: Códigos das turmas consultadas.
            adicionar_componentes_planejamento: Quando True, expande
                regência com os componentes de planejamento.

        Returns:
            Lista de componentes das turmas informadas.
        """
        return self._listar_por_lista_turmas(
            SQL_COMPONENTES_POR_LISTA_TURMAS_INCLUI_EXTINTAS,
            codigos_turmas,
            adicionar_componentes_planejamento,
        )

    def _listar_por_lista_turmas(
        self,
        sql_base: str,
        codigos_turmas: list[str],
        adicionar_componentes_planejamento: bool,
    ) -> list[dict]:
        if not codigos_turmas:
            return []
        placeholders = ",".join(["%s"] * len(codigos_turmas))
        sql = sql_base.format(placeholders=placeholders)
        rows = _raw(sql, list(codigos_turmas), self._DB)
        if adicionar_componentes_planejamento:
            return _expandir_planejamento_regencia(rows, self._DB)

        seen: set[tuple] = set()
        result: list[dict] = []
        for r in rows:
            item = _normalizar_componente_turma(r)
            key = (item["turma_codigo"], item["codigo"])
            if key not in seen:
                seen.add(key)
                item["professor"] = None
                result.append(item)
        return result

    def listar_turmas_brutos(
        self,
        codigos_turmas: list[str],
    ) -> list[dict]:
        """Lista componentes sem pós-processamento.

        Args:
            codigos_turmas: Códigos das turmas a consultar.

        Returns:
            Lista de componentes sem normalização de dados.
        """
        if not codigos_turmas:
            return []
        placeholders = ",".join(["%s"] * len(codigos_turmas))
        sql = SQL_COMPONENTES_TURMAS_BRUTOS.format(placeholders=placeholders)
        rows = _raw(sql, list(codigos_turmas), self._DB)
        resultado: list[dict] = []
        vistos: set[object] = set()
        for row in rows:
            row["professor"] = None
            item = _normalizar_componente_turma(row)
            key = item.get("codigo_componente_curricular_pai") or item.get(
                "codigo"
            )
            if key not in vistos:
                vistos.add(key)
                resultado.append(item)
        return resultado

    def listar_catalogo(self) -> list[dict]:
        """Lista o catálogo completo de componentes.

        Returns:
            Lista completa de componentes curriculares.
        """
        return [
            {"codigo": codigo, "descricao": descricao}
            for codigo, descricao in (
                ComponenteCurricular.objects.using(self._DB)
                .values_list("codigo", "descricao")
                .order_by("codigo")
            )
        ]

    def listar_vigencia_componentes(
        self,
        ue_codigo: str,
        ano_letivo: int,
        componentes_curriculares: list[str],
        semestre: int | None,
    ) -> list[dict]:
        """Lista vigência de componentes por turma e UE.

        Args:
            ue_codigo: Código da unidade educacional.
            ano_letivo: Ano letivo consultado.
            componentes_curriculares: Códigos dos componentes a consultar.
            semestre: Semestre letivo; None para todos os semestres.

        Returns:
            Lista de vigências de componentes por turma.
        """
        if not componentes_curriculares:
            return []
        placeholders = ",".join(["%s"] * len(componentes_curriculares))
        params: list = [ue_codigo, ano_letivo] + [
            int(c) for c in componentes_curriculares
        ]
        semestre_clause = ""
        if semestre is not None:
            semestre_clause = "AND t.semestre = %s"
            params.append(semestre)
        sql = SQL_VIGENCIA_COMPONENTES.format(
            placeholders=placeholders,
            semestre_clause=semestre_clause,
        )
        return _raw(sql, params, self._DB)

    def listar_grade_curricular(
        self,
        ano_letivo: int,
    ) -> list[dict]:
        """Lista grade curricular completa por ano letivo.

        Args:
            ano_letivo: Ano letivo consultado.

        Returns:
            Linhas da grade curricular do ano letivo.
        """
        rows = (
            GradeComponenteCurricular.objects.using(self._DB)
            .filter(ano_letivo=ano_letivo)
            .values_list(
                "codigo_componente_curricular",
                "descricao_componente_curricular",
                "codigo_ano_turma",
                "descricao_serie_ensino",
                "codigo_serie_ensino",
                "modalidade",
            )
            .distinct()
        )
        return [
            {
                "codigo_componente_curricular": codigo,
                "descricao_componente_curricular": descricao,
                "codigo_ano_turma": codigo_ano_turma,
                "descricao_serie_ensino": descricao_serie_ensino,
                "codigo_serie_ensino": codigo_serie_ensino,
                "modalidade": modalidade,
            }
            for (
                codigo,
                descricao,
                codigo_ano_turma,
                descricao_serie_ensino,
                codigo_serie_ensino,
                modalidade,
            ) in rows
        ]

    def listar_componentes_sem_atribuicao(
        self,
        codigo_turma: str,
        data_base: date,
    ) -> list[str]:
        """Lista códigos de componentes sem atribuição na data informada.

        Args:
            codigo_turma: Código da turma.
            data_base: Data usada para verificar a vigência da atribuição.

        Returns:
            Códigos dos componentes sem professor atribuído.
        """
        rows = _raw(
            SQL_COMPONENTES_SEM_ATRIBUICAO,
            [data_base, data_base, codigo_turma],
            self._DB,
        )
        return [str(r["codigo"]) for r in rows]

    def listar_agrupamentos_correlacionados(
        self,
        codigo_componente: int,
        data_base: date | None,
    ) -> list[dict]:
        """Retorna agrupamentos correlacionados de território do saber.

        Args:
            codigo_componente: `cod_agrupamento` de origem da consulta.
            data_base: Data de referência; None para sem filtro de data.

        Returns:
            Lista de agrupamentos e componentes correlacionados à origem.
        """
        origem = self._ordenar_agrupamentos_legado(
            AgrupamentoAtribuicaoTerritorioSaber.objects.using(
                self._DB
            ).filter(cod_agrupamento=codigo_componente)
        ).first()
        if origem is None:
            return []
        if not agrupamento_vigente_na_data(origem, data_base):
            return []

        resultado, vistos = self._agrupamentos_correlacionados_da_origem(
            origem,
            data_base,
        )
        resultado.extend(
            self._componentes_individuais_correlacionados(
                origem,
                vistos,
                data_base,
            )
        )
        return resultado

    def _agrupamentos_correlacionados_da_origem(
        self,
        origem: AgrupamentoAtribuicaoTerritorioSaber,
        data_base: date | None,
    ) -> tuple[list[dict], set[int]]:
        """Lista agrupamentos correlacionados de uma origem.

        Args:
            origem: Agrupamento de origem da consulta.
            data_base: Data de referência; None para sem filtro de data.

        Returns:
            Lista de agrupamentos formatados e códigos já incluídos.
        """
        qs = self._ordenar_agrupamentos_legado(
            AgrupamentoAtribuicaoTerritorioSaber.objects.using(
                self._DB
            ).filter(
                cod_turma=origem.cod_turma,
                cod_territorio_saber=origem.cod_territorio_saber,
                cod_experiencia_pedagogica=origem.cod_experiencia_pedagogica,
            )
        )

        grupos: dict[int, list[AgrupamentoAtribuicaoTerritorioSaber]] = {}
        for ag in qs:
            if not agrupamento_vigente_na_data(ag, data_base):
                continue
            if not componentes_agrupados_sao_subconjunto(ag, origem):
                continue
            grupos.setdefault(ag.cod_agrupamento, []).append(ag)

        resultado: list[dict] = []
        vistos: set[int] = set()
        for cod_agrupamento, candidatos in grupos.items():
            escolhido = self._selecionar_agrupamento_resposta(candidatos)
            if escolhido is None:
                continue
            vistos.add(cod_agrupamento)
            resultado.append(agrupamento_para_dict(escolhido))
        return resultado, vistos

    def _componentes_individuais_correlacionados(
        self,
        origem: AgrupamentoAtribuicaoTerritorioSaber,
        vistos: set[int],
        data_base: date | None,
    ) -> list[dict]:
        """Lista componentes individuais correlacionados de uma origem.

        Args:
            origem: Agrupamento de origem da consulta.
            vistos: Códigos já incluídos no resultado.
            data_base: Data de referência; None para sem filtro de data.

        Returns:
            Lista de componentes individuais formatados.
        """
        resultado: list[dict] = []
        atribuicoes_origem = list(self._atribuicoes_da_origem(origem))
        professor_sintetico = self._professor_filho_sintetico(
            origem,
            atribuicoes_origem,
            data_base,
        )
        for codigo in parse_csv(origem.cod_componentes_curriculares):
            if codigo in vistos:
                continue
            atribuicao = self._atribuicao_do_componente(
                origem,
                codigo,
                data_base,
            )
            componente = self._componente_territorio_da_turma(origem, codigo)
            if atribuicao is not None and componente is not None:
                item = atribuicao_nao_agrupada_para_dict(
                    componente,
                    atribuicao,
                )
            else:
                item = componente_sintetico_agrupado_para_dict(
                    origem,
                    codigo,
                    componente,
                    atribuicao,
                    professor_sintetico,
                )
            resultado.append(item)
            vistos.add(codigo)
        return resultado

    def _atribuicoes_da_origem(
        self,
        origem: AgrupamentoAtribuicaoTerritorioSaber,
    ) -> QuerySet[AtribuicaoTerritorioSaber]:
        """Busca atribuições individuais relacionadas à origem.

        Args:
            origem: Agrupamento de origem da consulta.

        Returns:
            QuerySet com atribuições individuais da mesma correlação.
        """
        componentes = parse_csv(origem.cod_componentes_curriculares)
        if not origem.cod_turma or not componentes:
            return AtribuicaoTerritorioSaber.objects.using(self._DB).none()

        return AtribuicaoTerritorioSaber.objects.using(self._DB).filter(
            turma_codigo=origem.cod_turma,
            codigo_territorio_saber=origem.cod_territorio_saber,
            codigo_experiencia_pedagogica=origem.cod_experiencia_pedagogica,
            componente_codigo__in=componentes,
        )

    def _atribuicao_do_componente(
        self,
        origem: AgrupamentoAtribuicaoTerritorioSaber,
        codigo: int,
        data_base: date | None,
    ) -> AtribuicaoTerritorioSaber | None:
        """Busca atribuição individual do componente na turma.

        Args:
            origem: Agrupamento de origem da consulta.
            codigo: Código do componente curricular.
            data_base: Data de referência; None para sem filtro de data.

        Returns:
            Atribuição selecionada, ou None.
        """
        if not origem.cod_turma:
            return None

        atribuicoes = AtribuicaoTerritorioSaber.objects.using(self._DB).filter(
            turma_codigo=origem.cod_turma,
            componente_codigo=codigo,
        )
        return self._selecionar_atribuicao_nao_agrupada(
            atribuicoes,
            codigo,
            data_base,
        )

    @staticmethod
    def _chave_atribuicao_nao_agrupada(
        atribuicao: AtribuicaoTerritorioSaber,
    ) -> tuple[
        str,
        int,
        int | None,
        str | None,
        datetime | None,
        date | None,
    ]:
        """Retorna a chave de agrupamento da atribuição individual.

        Args:
            atribuicao: Atribuição individual de Território do Saber.

        Returns:
            Chave usada para identificar atribuições duplicadas.
        """
        return (
            atribuicao.turma_codigo,
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

    @classmethod
    def _selecionar_atribuicao_nao_agrupada(
        cls,
        atribuicoes: Iterable[AtribuicaoTerritorioSaber],
        codigo: int,
        data_base: date | None,
    ) -> AtribuicaoTerritorioSaber | None:
        """Seleciona a atribuição individual aplicável ao componente.

        Args:
            atribuicoes: Atribuições candidatas da mesma correlação.
            codigo: Código do componente curricular solicitado.
            data_base: Data de referência; None para sem filtro de data.

        Returns:
            Atribuição selecionada, ou None.
        """
        grupos: dict[
            tuple[
                str,
                int,
                int | None,
                str | None,
                datetime | None,
                date | None,
            ],
            list[AtribuicaoTerritorioSaber],
        ] = {}
        for atribuicao in atribuicoes:
            chave = cls._chave_atribuicao_nao_agrupada(atribuicao)
            grupos.setdefault(chave, []).append(atribuicao)

        candidatos: list[AtribuicaoTerritorioSaber] = []
        for grupo in grupos.values():
            if len(grupo) == 1:
                candidatos.extend(grupo)
                continue

            candidatos.append(
                next(
                    (
                        atribuicao
                        for atribuicao in grupo
                        if atribuicao.componente_codigo == codigo
                    ),
                    grupo[0],
                )
            )

        candidatos.sort(
            key=lambda atribuicao: (
                atribuicao.dt_atribuicao is not None,
                atribuicao.dt_atribuicao,
                atribuicao.dt_disponibilizacao is None,
            ),
            reverse=True,
        )
        for atribuicao in candidatos:
            if atribuicao.componente_codigo != codigo:
                continue
            if (
                data_base
                and atribuicao.dt_atribuicao
                and atribuicao.dt_atribuicao.date() > data_base
            ):
                continue
            return atribuicao
        return None

    def _professor_filho_sintetico(
        self,
        origem: AgrupamentoAtribuicaoTerritorioSaber,
        atribuicoes: Iterable[AtribuicaoTerritorioSaber],
        data_base: date | None,
    ) -> str | None:
        """Retorna professor para filho sem atribuição individual.

        Args:
            origem: Agrupamento usado como origem da consulta.
            atribuicoes: Atribuições individuais da mesma correlação.
            data_base: Data de referência; None para sem filtro de data.

        Returns:
            RF do professor selecionado.
        """
        professor_atribuicao = self._professor_atribuicao_sintetica(
            atribuicoes,
            data_base,
        )
        if professor_atribuicao:
            return professor_atribuicao

        candidatos = list(
            AgrupamentoAtribuicaoTerritorioSaber.objects.using(self._DB)
            .filter(
                cod_agrupamento=origem.cod_agrupamento,
                cod_turma=origem.cod_turma,
                cod_componentes_curriculares=origem.cod_componentes_curriculares,
            )
            .order_by("-dt_inicio_atribuicao", "-id")
        )
        return self._selecionar_professor_filho_sintetico(
            candidatos,
            origem.rf_professor,
        )

    @staticmethod
    def _professor_atribuicao_sintetica(
        atribuicoes: Iterable[AtribuicaoTerritorioSaber],
        data_base: date | None,
    ) -> str | None:
        """Seleciona professor a partir de atribuições individuais.

        Args:
            atribuicoes: Atribuições individuais candidatas.
            data_base: Data de referência; None para sem filtro de data.

        Returns:
            RF do professor mais recente, ou None.
        """
        candidatos = [
            atribuicao
            for atribuicao in atribuicoes
            if atribuicao.professor
            and (
                data_base is None
                or not atribuicao.dt_atribuicao
                or atribuicao.dt_atribuicao.date() <= data_base
            )
        ]
        if not candidatos:
            return None

        escolhido = max(
            candidatos,
            key=lambda atribuicao: (
                atribuicao.dt_atribuicao is not None,
                atribuicao.dt_atribuicao,
                atribuicao.dt_disponibilizacao is None,
            ),
        )
        return escolhido.professor

    @classmethod
    def _selecionar_professor_filho_sintetico(
        cls,
        candidatos: list[AgrupamentoAtribuicaoTerritorioSaber],
        padrao: str | None,
    ) -> str | None:
        """Seleciona professor para filho sintético.

        Args:
            candidatos: Agrupamentos candidatos.
            padrao: Professor usado quando não há candidato específico.

        Returns:
            RF do professor selecionado.
        """
        abertos = [
            candidato
            for candidato in candidatos
            if candidato.dt_fim_atribuicao is None
        ]
        encerrados = [
            candidato
            for candidato in candidatos
            if candidato.dt_fim_atribuicao is not None
            and candidato.dt_inicio_atribuicao == candidato.dt_fim_atribuicao
        ]
        encerrados_reais = [
            candidato
            for candidato in candidatos
            if candidato.dt_fim_atribuicao is not None
            and candidato.dt_inicio_atribuicao != candidato.dt_fim_atribuicao
        ]

        aberto_recente = max(
            abertos,
            key=lambda candidato: (
                candidato.dt_inicio_atribuicao,
                candidato.id,
            ),
            default=None,
        )
        encerrado_real_recente = max(
            encerrados_reais,
            key=lambda candidato: (
                candidato.dt_fim_atribuicao,
                candidato.dt_inicio_atribuicao,
                candidato.id,
            ),
            default=None,
        )
        if (
            aberto_recente
            and encerrado_real_recente
            and aberto_recente.dt_inicio_atribuicao
            == encerrado_real_recente.dt_fim_atribuicao
        ):
            return aberto_recente.rf_professor

        if encerrado_real_recente:
            return encerrado_real_recente.rf_professor

        if encerrados:
            escolhido = max(
                encerrados,
                key=lambda candidato: (
                    candidato.dt_inicio_atribuicao,
                    candidato.id,
                ),
            )
            return escolhido.rf_professor
        return padrao

    def _componente_territorio_da_turma(
        self,
        origem: AgrupamentoAtribuicaoTerritorioSaber,
        codigo: int,
    ) -> ComponenteTurma | None:
        """Busca componente de território da turma da origem.

        Args:
            origem: Agrupamento de origem da consulta.
            codigo: Código do componente curricular.

        Returns:
            Componente da turma encontrado, ou None.
        """
        return (
            ComponenteTurma.objects.using(self._DB)
            .filter(
                turma_codigo=origem.cod_turma,
                componente_codigo=codigo,
                codigo_componente_territorio_saber__isnull=False,
            )
            .first()
        )

    def listar_agrupamentos_correlacionados_lote(
        self,
        codigos_agrupamentos: list[int],
        data_base: date | None,
    ) -> list[dict]:
        """Retorna agrupamentos correlacionados em lote.

        Args:
            codigos_agrupamentos: `cod_agrupamento` das origens consultadas.
            data_base: Data de referência; None para sem filtro de data.

        Returns:
            Lista de agrupamentos correlacionados sem duplicatas.
        """
        if not codigos_agrupamentos:
            return []

        origens = self._origens_agrupamentos_lote(codigos_agrupamentos)
        correlacionados_por_chave = self._correlacionados_por_chave_lote(
            origens.values()
        )
        componentes_por_chave = self._componentes_territorio_lote(
            origens.values()
        )
        (
            atribuicoes_por_chave,
            atribuicoes_por_componente,
            atribuicoes_por_correlacao,
        ) = self._atribuicoes_territorio_lote(origens.values())

        resultado: list[dict] = []
        vistos: set[object] = set()
        for cod in codigos_agrupamentos:
            origem = origens.get(cod)
            if origem is None or not agrupamento_vigente_na_data(
                origem,
                data_base,
            ):
                continue

            itens, vistos_origem = self._agrupamentos_correlacionados_lote(
                origem,
                data_base,
                correlacionados_por_chave,
                atribuicoes_por_chave,
            )
            itens.extend(
                self._componentes_individuais_lote(
                    origem,
                    vistos_origem,
                    data_base,
                    correlacionados_por_chave,
                    componentes_por_chave,
                    atribuicoes_por_componente,
                    atribuicoes_por_correlacao,
                )
            )

            for item in itens:
                chave = item["codigo"]
                if chave in vistos:
                    continue
                vistos.add(chave)
                resultado.append(item)
        return resultado

    def _origens_agrupamentos_lote(
        self,
        codigos_agrupamentos: list[int],
    ) -> dict[int, AgrupamentoAtribuicaoTerritorioSaber]:
        """Busca as origens de agrupamentos do lote.

        Args:
            codigos_agrupamentos: `cod_agrupamento` das origens consultadas.

        Returns:
            Agrupamentos de origem indexados por código.
        """
        origens: dict[int, AgrupamentoAtribuicaoTerritorioSaber] = {}
        agrupamentos = self._ordenar_agrupamentos_legado(
            AgrupamentoAtribuicaoTerritorioSaber.objects.using(
                self._DB
            ).filter(cod_agrupamento__in=codigos_agrupamentos)
        )
        for agrupamento in agrupamentos:
            origens.setdefault(agrupamento.cod_agrupamento, agrupamento)
        return origens

    @staticmethod
    def _chave_correlacionados(
        agrupamento: AgrupamentoAtribuicaoTerritorioSaber,
    ) -> tuple[str | None, int, int | None]:
        """Retorna a chave de correlação de agrupamentos.

        Args:
            agrupamento: Agrupamento de Território do Saber.

        Returns:
            Chave composta por turma, território e experiência pedagógica.
        """
        return (
            agrupamento.cod_turma,
            agrupamento.cod_territorio_saber,
            agrupamento.cod_experiencia_pedagogica,
        )

    def _correlacionados_por_chave_lote(
        self,
        origens: Iterable[AgrupamentoAtribuicaoTerritorioSaber],
    ) -> dict[
        tuple[str | None, int, int | None],
        list[AgrupamentoAtribuicaoTerritorioSaber],
    ]:
        """Busca agrupamentos correlacionados das origens em bloco.

        Args:
            origens: Agrupamentos de origem do lote.

        Returns:
            Agrupamentos correlacionados indexados pela chave de correlação.
        """
        chaves = {self._chave_correlacionados(origem) for origem in origens}
        if not chaves:
            return {}

        filtros = Q()
        for turma, territorio, experiencia in chaves:
            filtros |= Q(
                cod_turma=turma,
                cod_territorio_saber=territorio,
                cod_experiencia_pedagogica=experiencia,
            )

        resultado: dict[
            tuple[str | None, int, int | None],
            list[AgrupamentoAtribuicaoTerritorioSaber],
        ] = {chave: [] for chave in chaves}
        agrupamentos = self._ordenar_agrupamentos_legado(
            AgrupamentoAtribuicaoTerritorioSaber.objects.using(
                self._DB
            ).filter(filtros)
        )
        for agrupamento in agrupamentos:
            chave = self._chave_correlacionados(agrupamento)
            resultado.setdefault(chave, []).append(agrupamento)
        return resultado

    @staticmethod
    def _codigos_componentes_origens(
        origens: Iterable[AgrupamentoAtribuicaoTerritorioSaber],
    ) -> tuple[set[str], set[int]]:
        """Retorna turmas e componentes presentes nas origens.

        Args:
            origens: Agrupamentos de origem do lote.

        Returns:
            Tupla com turmas e componentes curriculares das origens.
        """
        turmas: set[str] = set()
        componentes: set[int] = set()
        for origem in origens:
            if origem.cod_turma:
                turmas.add(origem.cod_turma)
            componentes.update(parse_csv(origem.cod_componentes_curriculares))
        return turmas, componentes

    def _componentes_territorio_lote(
        self,
        origens: Iterable[AgrupamentoAtribuicaoTerritorioSaber],
    ) -> dict[tuple[str, int], ComponenteTurma]:
        """Busca componentes de território das origens em bloco.

        Args:
            origens: Agrupamentos de origem do lote.

        Returns:
            Componentes indexados por turma e código.
        """
        turmas, componentes = self._codigos_componentes_origens(origens)
        if not turmas or not componentes:
            return {}

        resultado: dict[tuple[str, int], ComponenteTurma] = {}
        queryset = (
            ComponenteTurma.objects.using(self._DB)
            .filter(
                turma_codigo__in=turmas,
                componente_codigo__in=componentes,
                codigo_componente_territorio_saber__isnull=False,
            )
            .order_by("turma_codigo", "componente_codigo")
        )
        for componente in queryset:
            chave = (componente.turma_codigo, componente.componente_codigo)
            resultado.setdefault(chave, componente)
        return resultado

    def _atribuicoes_territorio_lote(
        self,
        origens: Iterable[AgrupamentoAtribuicaoTerritorioSaber],
    ) -> tuple[
        dict[tuple[str, int], AtribuicaoTerritorioSaber],
        dict[tuple[str, int], list[AtribuicaoTerritorioSaber]],
        dict[
            tuple[str | None, int, int | None],
            list[AtribuicaoTerritorioSaber],
        ],
    ]:
        """Busca atribuições de território das origens em bloco.

        Args:
            origens: Agrupamentos de origem do lote.

        Returns:
            Atribuições indexadas por turma/componente e por correlação.
        """
        turmas, componentes = self._codigos_componentes_origens(origens)
        if not turmas or not componentes:
            return {}, {}, {}

        por_componente: dict[tuple[str, int], AtribuicaoTerritorioSaber] = {}
        lista_por_componente: dict[
            tuple[str, int], list[AtribuicaoTerritorioSaber]
        ] = {}
        por_correlacao: dict[
            tuple[str | None, int, int | None],
            list[AtribuicaoTerritorioSaber],
        ] = {}
        atribuicoes = (
            AtribuicaoTerritorioSaber.objects.using(self._DB)
            .filter(
                turma_codigo__in=turmas,
                componente_codigo__in=componentes,
            )
            .order_by(
                "turma_codigo",
                "componente_codigo",
                "-dt_atribuicao",
                "id",
            )
        )
        for atribuicao in atribuicoes:
            chave_componente = (
                atribuicao.turma_codigo,
                atribuicao.componente_codigo,
            )
            por_componente.setdefault(chave_componente, atribuicao)
            lista_por_componente.setdefault(chave_componente, []).append(
                atribuicao
            )

            chave_correlacao = (
                atribuicao.turma_codigo,
                atribuicao.codigo_territorio_saber,
                atribuicao.codigo_experiencia_pedagogica,
            )
            por_correlacao.setdefault(chave_correlacao, []).append(atribuicao)
        return por_componente, lista_por_componente, por_correlacao

    def _agrupamentos_correlacionados_lote(
        self,
        origem: AgrupamentoAtribuicaoTerritorioSaber,
        data_base: date | None,
        correlacionados_por_chave: dict[
            tuple[str | None, int, int | None],
            list[AgrupamentoAtribuicaoTerritorioSaber],
        ],
        atribuicoes_por_chave: dict[
            tuple[str, int], AtribuicaoTerritorioSaber
        ],
    ) -> tuple[list[dict], set[int]]:
        """Lista agrupamentos correlacionados usando dados pré-carregados.

        Args:
            origem: Agrupamento de origem da consulta.
            data_base: Data de referência; None para sem filtro de data.
            correlacionados_por_chave: Agrupamentos agrupados por chave.
            atribuicoes_por_chave: Atribuições indexadas por turma e código.

        Returns:
            Lista de agrupamentos formatados e códigos incluídos.
        """
        grupos: dict[int, list[AgrupamentoAtribuicaoTerritorioSaber]] = {}
        chave = self._chave_correlacionados(origem)
        for ag in correlacionados_por_chave.get(chave, []):
            if not agrupamento_vigente_na_data(ag, data_base):
                continue
            if not componentes_agrupados_sao_subconjunto(ag, origem):
                continue
            grupos.setdefault(ag.cod_agrupamento, []).append(ag)

        resultado: list[dict] = []
        vistos: set[int] = set()
        for cod_agrupamento, candidatos in grupos.items():
            escolhido = self._selecionar_agrupamento_resposta(
                candidatos,
                atribuicoes_por_chave,
            )
            if escolhido is None:
                continue
            vistos.add(cod_agrupamento)
            resultado.append(agrupamento_para_dict(escolhido))
        return resultado, vistos

    def _componentes_individuais_lote(
        self,
        origem: AgrupamentoAtribuicaoTerritorioSaber,
        vistos: set[int],
        data_base: date | None,
        correlacionados_por_chave: dict[
            tuple[str | None, int, int | None],
            list[AgrupamentoAtribuicaoTerritorioSaber],
        ],
        componentes_por_chave: dict[tuple[str, int], ComponenteTurma],
        atribuicoes_por_componente: dict[
            tuple[str, int],
            list[AtribuicaoTerritorioSaber],
        ],
        atribuicoes_por_correlacao: dict[
            tuple[str | None, int, int | None],
            list[AtribuicaoTerritorioSaber],
        ],
    ) -> list[dict]:
        """Lista componentes individuais usando dados pré-carregados.

        Args:
            origem: Agrupamento de origem da consulta.
            vistos: Códigos já incluídos no resultado.
            data_base: Data de referência; None para sem filtro de data.
            correlacionados_por_chave: Agrupamentos agrupados por chave.
            componentes_por_chave: Componentes indexados por turma e código.
            atribuicoes_por_componente: Atribuições indexadas por componente.
            atribuicoes_por_correlacao: Atribuições indexadas por correlação.

        Returns:
            Lista de componentes individuais formatados.
        """
        resultado: list[dict] = []
        if origem.cod_turma is None:
            return resultado

        atribuicoes_origem = atribuicoes_por_correlacao.get(
            self._chave_correlacionados(origem),
            [],
        )
        professor_atribuicao = self._professor_atribuicao_sintetica(
            atribuicoes_origem,
            data_base,
        )
        professor_sintetico = self._selecionar_professor_filho_sintetico(
            [
                agrupamento
                for agrupamento in correlacionados_por_chave.get(
                    self._chave_correlacionados(origem),
                    [],
                )
                if agrupamento.cod_agrupamento == origem.cod_agrupamento
                and agrupamento.cod_turma == origem.cod_turma
                and agrupamento.cod_componentes_curriculares
                == origem.cod_componentes_curriculares
            ],
            origem.rf_professor,
        )
        professor_sintetico = professor_atribuicao or professor_sintetico

        for codigo in parse_csv(origem.cod_componentes_curriculares):
            if codigo in vistos:
                continue

            chave = (origem.cod_turma, codigo)
            atribuicao = self._selecionar_atribuicao_nao_agrupada(
                atribuicoes_por_componente.get(chave, []),
                codigo,
                data_base,
            )
            componente = componentes_por_chave.get(chave)
            if atribuicao is not None and componente is not None:
                item = atribuicao_nao_agrupada_para_dict(
                    componente,
                    atribuicao,
                )
            else:
                item = componente_sintetico_agrupado_para_dict(
                    origem,
                    codigo,
                    componente,
                    atribuicao,
                    professor_sintetico,
                )
            resultado.append(item)
            vistos.add(codigo)
        return resultado

    def listar_agrupamentos_territorio(
        self,
        codigos_agrupamentos: list[int],
    ) -> list[dict]:
        """Retorna agrupamentos de território do saber por IDs.

        Args:
            codigos_agrupamentos: IDs dos agrupamentos a consultar.

        Returns:
            Lista de agrupamentos de Território do Saber.
        """
        agrupamentos = self._ordenar_agrupamentos_legado(
            AgrupamentoAtribuicaoTerritorioSaber.objects.using(
                self._DB
            ).filter(cod_agrupamento__in=codigos_agrupamentos)
        )
        grupos: dict[int, list[AgrupamentoAtribuicaoTerritorioSaber]] = {}
        for ag in agrupamentos:
            grupos.setdefault(ag.cod_agrupamento, []).append(ag)

        resultado: list[dict] = []
        for candidatos in grupos.values():
            escolhido = self._selecionar_agrupamento_resposta(candidatos)
            if escolhido is None:
                continue
            resultado.append(agrupamento_para_dict(escolhido))
        return resultado
