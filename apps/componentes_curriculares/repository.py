"""Repositório de componentes curriculares."""

from datetime import date

from django.db import connections
from django.db.models import F

from apps.componentes_curriculares.constants import (
    CODIGO_COMPONENTE_REGENCIA_CLASSE_INFANTIL,
    DESCRICAO_COMPONENTE_REGENCIA_CLASSE_INFANTIL,
    MOTIVO_DISPONIBILIZACAO_FIM_ANO_LETIVO,
)
from apps.componentes_curriculares.models import (
    AgrupamentoAtribuicaoTerritorioSaber,
    AtribuicaoComponente,
    ComponenteCurricular,
    ComponenteCurricularPlanejamentoRegencia,
    ComponenteTurma,
    GradeComponenteCurricular,
)
from apps.componentes_curriculares.queries import (
    SQL_COMPONENTES_GRADE_POR_UE_MODALIDADE_ANO,
    SQL_COMPONENTES_POR_LISTA_TURMAS,
    SQL_COMPONENTES_SEM_ATRIBUICAO,
    SQL_COMPONENTES_SIMPLIFICADOS_POR_TURMAS,
    SQL_COMPONENTES_TURMA_COM_ATRIBUICAO,
    SQL_COMPONENTES_TURMA_PROGRAMA,
    SQL_COMPONENTES_TURMAS_BRUTOS,
    SQL_FILTRO_ATRIBUICAO_POR_TURMA,
    SQL_FILTRO_ATRIBUICAO_VIGENTE,
    SQL_VIGENCIA_COMPONENTES,
)
from apps.componentes_curriculares.services.territorio_saber import (
    agrupamento_para_dict,
    agrupamento_vigente_na_data,
    atribuicao_nao_agrupada_para_dict,
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
            item = _normalizar_componente_turma(row)
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
        if not codigos_turmas:
            return []
        placeholders = ",".join(["%s"] * len(codigos_turmas))
        sql = SQL_COMPONENTES_POR_LISTA_TURMAS.format(
            placeholders=placeholders
        )
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
        origem = (
            AgrupamentoAtribuicaoTerritorioSaber.objects.using(self._DB)
            .filter(cod_agrupamento=codigo_componente)
            .order_by(
                "-dt_inicio_atribuicao",
                F("dt_fim_atribuicao").desc(nulls_first=True),
            )
            .first()
        )
        if origem is None:
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
        qs = (
            AgrupamentoAtribuicaoTerritorioSaber.objects.using(self._DB)
            .filter(
                cod_turma=origem.cod_turma,
                cod_territorio_saber=origem.cod_territorio_saber,
                cod_experiencia_pedagogica=origem.cod_experiencia_pedagogica,
            )
            .order_by(
                "-dt_inicio_atribuicao",
                F("dt_fim_atribuicao").desc(nulls_first=True),
            )
        )

        resultado: list[dict] = []
        vistos: set[int] = set()
        for ag in qs:
            if not agrupamento_vigente_na_data(ag, data_base):
                continue
            if not componentes_agrupados_sao_subconjunto(ag, origem):
                continue
            if ag.cod_agrupamento in vistos:
                continue
            vistos.add(ag.cod_agrupamento)
            resultado.append(agrupamento_para_dict(ag))
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
        for codigo in parse_csv(origem.cod_componentes_curriculares):
            if codigo in vistos:
                continue
            atribuicao = self._atribuicao_do_componente(origem, codigo)
            componente = self._componente_territorio_da_turma(origem, codigo)
            if atribuicao is None or componente is None:
                continue
            if (
                data_base
                and atribuicao.dt_atribuicao
                and atribuicao.dt_atribuicao.date() > data_base
            ):
                continue
            resultado.append(
                atribuicao_nao_agrupada_para_dict(
                    componente,
                    atribuicao,
                    origem,
                )
            )
            vistos.add(codigo)
        return resultado

    def _atribuicao_do_componente(
        self,
        origem: AgrupamentoAtribuicaoTerritorioSaber,
        codigo: int,
    ) -> AtribuicaoComponente | None:
        """Busca atribuição ativa de um componente da origem.

        Args:
            origem: Agrupamento de origem da consulta.
            codigo: Código do componente curricular.

        Returns:
            Atribuição encontrada, ou None.
        """
        return (
            AtribuicaoComponente.objects.using(self._DB)
            .filter(
                turma_codigo=origem.cod_turma,
                componente_codigo=codigo,
                dt_cancelamento__isnull=True,
            )
            .order_by("-dt_atribuicao")
            .first()
        )

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
        resultado: list[dict] = []
        vistos: set[tuple[object, object]] = set()
        for cod in codigos_agrupamentos:
            for item in self.listar_agrupamentos_correlacionados(
                cod, data_base
            ):
                chave = (item["codigo"], item.get("professor"))
                if chave not in vistos:
                    vistos.add(chave)
                    resultado.append(item)
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
        agrupamentos = (
            AgrupamentoAtribuicaoTerritorioSaber.objects.using(self._DB)
            .filter(cod_agrupamento__in=codigos_agrupamentos)
            .order_by(
                "-dt_inicio_atribuicao",
                F("dt_fim_atribuicao").desc(nulls_first=True),
            )
        )
        vistos: set[int] = set()
        resultado: list[dict] = []
        for ag in agrupamentos:
            if ag.cod_agrupamento not in vistos:
                vistos.add(ag.cod_agrupamento)
                resultado.append(agrupamento_para_dict(ag))
        return resultado
