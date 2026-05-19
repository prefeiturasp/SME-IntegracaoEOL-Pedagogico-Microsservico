"""Repositório de componentes curriculares."""

from datetime import date

from django.db import connections
from django.db.models import F

from apps.componentes_curriculares.constants import (
    CODIGO_COMPONENTE_REGENCIA_CLASSE_INFANTIL,
    DESCRICAO_COMPONENTE_REGENCIA_CLASSE_INFANTIL,
)
from apps.componentes_curriculares.models import (
    AgrupamentoAtribuicaoTerritorioSaber,
    AtribuicaoComponente,
    ComponenteCurricular,
    ComponenteCurricularPAP,
    ComponenteCurricularPlanejamentoRegencia,
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
    SQL_VIGENCIA_COMPONENTES,
)


def _raw(sql: str, params: list, using: str = "default") -> list[dict]:
    with connections[using].cursor() as cursor:
        cursor.execute(sql, params)
        cols = [c[0] for c in cursor.description]
        return [
            dict(zip(cols, row, strict=False)) for row in cursor.fetchall()
        ]


def _componente_para_dict(row: dict) -> dict:
    """Normaliza campos computados de componente curricular."""
    return {
        **row,
        "codigo_componente_territorio_saber": (
            row.get("codigo_componente_territorio_saber") or 0
        ),
        "exibir_componente_eol": False,
        "codigos_territorios_agrupamento": [],
    }


def _grade_para_componente(row: dict) -> dict:
    """Retorna componente curricular a partir de linha de grade."""
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
    """Normaliza a regência de classe infantil."""
    if item["codigo"] == CODIGO_COMPONENTE_REGENCIA_CLASSE_INFANTIL:
        # Compatibiliza o componente infantil com o retorno esperado pelo
        # domínio pedagógico
        item["codigo_componente_curricular_pai"] = (
            CODIGO_COMPONENTE_REGENCIA_CLASSE_INFANTIL
        )
        item["descricao"] = DESCRICAO_COMPONENTE_REGENCIA_CLASSE_INFANTIL
        item["regencia"] = True
    return item


def _agrupamento_para_dict(
    agrupamento: AgrupamentoAtribuicaoTerritorioSaber,
) -> dict:
    """Formata agrupamento de território para resposta."""
    codigos = _parse_csv(agrupamento.cod_componentes_curriculares)
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
        "exibir_componente_eol": True,
        "professor": agrupamento.rf_professor,
        "codigos_territorios_agrupamento": codigos,
    }


def _parse_csv(csv_str: str | None) -> list[int]:
    """Retorna códigos de componentes extraídos de CSV."""
    if not csv_str:
        return []
    return [int(c.strip()) for c in csv_str.split(",") if c.strip().isdigit()]


def _int_or_none(value: object) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _componentes_planejamento_regencia(
    row: dict,
    using: str,
) -> list[ComponenteCurricular]:
    turno = _int_or_none(row.get("turno_turma"))
    ano = _int_or_none(row.get("ano_turma"))

    qs = ComponenteCurricularPlanejamentoRegencia.objects.using(using)
    regras = list(qs.filter(turno=turno, ano=ano))
    if not regras:
        # Usa a regra genérica quando não há configuração específica
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
    """Retorna componentes de regência expandidos para planejamento."""
    resultado: list[dict] = []
    vistos: set[tuple] = set()

    for row in rows:
        if not row.get("regencia"):
            item = _componente_para_dict(row)
            key = (
                item.get("turma_codigo"),
                item.get("codigo"),
                item.get("professor"),
            )
            if key not in vistos:
                vistos.add(key)
                resultado.append(item)
            continue

        for componente in _componentes_planejamento_regencia(row, using):
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
                    "professor": row.get("professor"),
                }
            )
            key = (
                item.get("turma_codigo"),
                item.get("codigo"),
                item.get("professor"),
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
    ) -> list[dict]:
        """Lista componentes por turma e funcionário."""
        sql = (
            f"{SQL_COMPONENTES_TURMA_COM_ATRIBUICAO}"
            " WHERE ac.professor = %s AND ct.turma_codigo = %s"
        )
        rows = _raw(sql, [login, codigo_turma], self._DB)
        return [_componente_para_dict(r) for r in rows]

    def listar_por_funcionario(
        self,
        login: str,
    ) -> list[dict]:
        """Lista todos os componentes do funcionário."""
        sql = f"{SQL_COMPONENTES_TURMA_COM_ATRIBUICAO} WHERE ac.professor = %s"
        rows = _raw(sql, [login], self._DB)

        # Remove repetições do mesmo componente em turmas diferentes
        seen_codigo: set[int] = set()
        by_codigo: list[dict] = []
        for r in rows:
            if r["codigo"] not in seen_codigo:
                seen_codigo.add(r["codigo"])
                r["turma_codigo"] = None
                r["professor"] = None
                by_codigo.append(_componente_para_dict(r))

        # Agrupa componentes filhos sob o respectivo componente pai
        seen_pai: set[int] = set()
        result: list[dict] = []
        for item in by_codigo:
            pai = item.get("codigo_componente_curricular_pai") or 0
            key = pai if pai > 0 else item["codigo"]
            if key not in seen_pai:
                seen_pai.add(key)
                result.append(item)

        return result

    def listar_planejamento_por_turma_funcionario(
        self,
        codigo_turma: str,
        login: str,
    ) -> list[dict]:
        """Lista componentes da turma aplicando planejamento de regência."""
        sql = (
            f"{SQL_COMPONENTES_TURMA_COM_ATRIBUICAO}"
            " WHERE ac.professor = %s AND ct.turma_codigo = %s"
        )
        rows = _raw(sql, [login, codigo_turma], self._DB)
        return _expandir_planejamento_regencia(rows, self._DB)

    def listar_regencia_por_ano_turma(
        self,
        ano_turma: int,
    ) -> list[dict]:
        """Lista componentes de regência por ano de turma."""
        if ano_turma <= 0:
            codigos = list(
                ComponenteCurricularPlanejamentoRegencia.objects.using(
                    self._DB
                )
                .filter(ano__isnull=True)
                .values_list("id_componente_curricular", flat=True)
            )
        else:
            codigos = list(
                ComponenteCurricularPlanejamentoRegencia.objects.using(
                    self._DB
                )
                .filter(ano=ano_turma)
                .values_list("id_componente_curricular", flat=True)
            )
        componentes = (
            ComponenteCurricular.objects.using(self._DB)
            .filter(codigo__in=codigos)
            .values("codigo", "descricao")
        )
        return [
            {
                "ano_turma": None,
                "ano_letivo": 0,
                "codigo": c["codigo"],
                "codigo_componente_territorio_saber": 0,
                "descricao": c["descricao"],
                "territorio_saber": False,
                "tipo_escola": None,
                "turno_turma": 0,
                "componente_planejamento_regencia": False,
                "turma_codigo": None,
                "professor": None,
                "inicio_atribuicao": None,
                "fim_atribuicao": None,
            }
            for c in componentes
        ]

    def turma_possui_componente_pap(
        self,
        codigo_turma: str,
        login: str,
    ) -> bool:
        """Verifica se a turma possui componente PAP para o funcionário."""
        codigos = list(
            AtribuicaoComponente.objects.using(self._DB)
            .filter(turma_codigo=codigo_turma, professor=login)
            .values_list("componente_codigo", flat=True)
        )
        return (
            ComponenteCurricularPAP.objects.using(self._DB)
            .filter(id_componente_curricular__in=codigos)
            .exists()
        )

    def listar_por_ue_modalidade_ano_e_anos_escolares(
        self,
        ue_codigo: str,
        modalidade: int,
        ano_letivo: int,
        anos_escolares: list[str],
    ) -> list[dict]:
        """Lista componentes da grade por UE, modalidade, ano e séries."""
        sql = SQL_COMPONENTES_GRADE_POR_UE_MODALIDADE_ANO
        params: list = [ue_codigo, modalidade, ano_letivo]
        if anos_escolares:
            placeholders = ",".join(["%s"] * len(anos_escolares))
            sql += f" AND t.ano IN ({placeholders})"
            params.extend(anos_escolares)
        rows = _raw(sql, params, self._DB)
        return [_grade_para_componente(r) for r in rows]

    def listar_turma_programa_por_ue_modalidade_ano(
        self,
        ue_codigo: str,
        modalidade: int,
        ano_letivo: int,
    ) -> list[dict]:
        """Lista componentes de turmas programa por UE, modalidade e ano."""
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
        return [_grade_para_componente(r) for r in rows]

    def listar_por_ue_e_turmas(
        self,
        ue_id: str,
        turmas: list[str],
    ) -> list[dict]:
        """Lista componentes simplificados por lista de turmas."""
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
        """Lista componentes de múltiplas turmas para planejamento."""
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
            key = (r["turma_codigo"], r["codigo"])
            if key not in seen:
                seen.add(key)
                result.append(_componente_para_dict(r))
        return result

    def listar_turmas_brutos(
        self,
        codigos_turmas: list[str],
    ) -> list[dict]:
        """Lista componentes sem pós-processamento."""
        if not codigos_turmas:
            return []
        placeholders = ",".join(["%s"] * len(codigos_turmas))
        sql = SQL_COMPONENTES_TURMAS_BRUTOS.format(placeholders=placeholders)
        rows = _raw(sql, list(codigos_turmas), self._DB)
        for r in rows:
            r["professor"] = None
        return [_componente_para_dict(r) for r in rows]

    def listar_catalogo(self) -> list[dict]:
        """Lista o catálogo completo de componentes."""
        return list(
            ComponenteCurricular.objects.using(self._DB)
            .values("codigo", "descricao")
            .order_by("codigo")
        )

    def listar_vigencia_componentes(
        self,
        ue_codigo: str,
        ano_letivo: int,
        componentes_curriculares: list[str],
        semestre: int | None,
    ) -> list[dict]:
        """Lista vigência de componentes por turma e UE."""
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
        """Lista grade curricular completa por ano letivo."""
        return list(
            GradeComponenteCurricular.objects.using(self._DB)
            .filter(ano_letivo=ano_letivo)
            .values(
                "codigo_componente_curricular",
                "descricao_componente_curricular",
                "codigo_ano_turma",
                "descricao_serie_ensino",
                "codigo_serie_ensino",
                "modalidade",
            )
            .distinct()
        )

    def listar_componentes_sem_atribuicao(
        self,
        codigo_turma: str,
    ) -> list[str]:
        """Lista componentes sem professor atribuído na turma."""
        rows = _raw(SQL_COMPONENTES_SEM_ATRIBUICAO, [codigo_turma], self._DB)
        return [r["descricao"] for r in rows]

    def listar_agrupamentos_correlacionados(
        self,
        codigo_componente: int,
        data_base: date | None,
    ) -> list[dict]:
        """Retorna agrupamentos correlacionados de território do saber."""
        origem = (
            AgrupamentoAtribuicaoTerritorioSaber.objects.using(self._DB)
            .filter(cod_agrupamento=codigo_componente)
            .order_by(
                F("dt_fim_atribuicao").asc(nulls_first=True),
                "-dt_inicio_atribuicao",
            )
            .first()
        )
        if origem is None:
            return []

        qs = AgrupamentoAtribuicaoTerritorioSaber.objects.using(
            self._DB
        ).filter(
            cod_turma=origem.cod_turma,
            cod_territorio_saber=origem.cod_territorio_saber,
        )
        if data_base is not None:
            qs = qs.filter(dt_inicio_atribuicao__date__lte=data_base)

        codigos_origem = set(_parse_csv(origem.cod_componentes_curriculares))
        resultado: list[dict] = []
        for ag in qs:
            codigos_ag = set(_parse_csv(ag.cod_componentes_curriculares))
            if codigos_ag and codigos_ag.issubset(codigos_origem):
                resultado.append(_agrupamento_para_dict(ag))
        return resultado

    def listar_agrupamentos_correlacionados_lote(
        self,
        codigos_agrupamentos: list[int],
        data_base: date | None,
    ) -> list[dict]:
        """Retorna agrupamentos correlacionados em lote."""
        resultado: list[dict] = []
        vistos: set[int] = set()
        for cod in codigos_agrupamentos:
            for item in self.listar_agrupamentos_correlacionados(
                cod, data_base
            ):
                ag_cod = item["codigo"]
                if ag_cod not in vistos:
                    vistos.add(ag_cod)
                    resultado.append(item)
        return resultado

    def listar_agrupamentos_territorio(
        self,
        codigos_agrupamentos: list[int],
    ) -> list[dict]:
        """Retorna agrupamentos de território do saber por IDs."""
        agrupamentos = (
            AgrupamentoAtribuicaoTerritorioSaber.objects.using(self._DB)
            .filter(cod_agrupamento__in=codigos_agrupamentos)
            .order_by(
                F("dt_fim_atribuicao").asc(nulls_first=True),
                "-dt_inicio_atribuicao",
            )
        )
        vistos: set[int] = set()
        resultado: list[dict] = []
        for ag in agrupamentos:
            if ag.cod_agrupamento not in vistos:
                vistos.add(ag.cod_agrupamento)
                resultado.append(_agrupamento_para_dict(ag))
        return resultado
