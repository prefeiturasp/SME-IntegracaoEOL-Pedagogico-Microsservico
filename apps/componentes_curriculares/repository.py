"""Repository de Componentes Curriculares."""
from datetime import date

from django.db import connections
from django.db.models import F

from apps.componentes_curriculares.models import (
    AgrupamentoAtribuicaoTerritorioSaber,
    AtribuicaoComponente,
    ComponenteCurricular,
    ComponenteCurricularPAP,
    ComponenteTurma,
    GradeComponenteCurricular,
    RegenciaComponenteCurricular,
)

_CT_FIELDS = """\
    ct.componente_codigo AS codigo,
    ct.codigo_componente_territorio_saber,
    ct.codigo_componente_curricular_pai,
    ct.descricao, ct.regencia, ct.planejamento_regencia,
    ct.territorio_saber, ct.turma_codigo, ct.ano_letivo"""

_SQL_CT_JOIN_AC = f"""\
SELECT {_CT_FIELDS}, ac.professor
  FROM componente_turma ct
  JOIN atribuicao_componente ac
    ON ac.turma_codigo = ct.turma_codigo
   AND ac.componente_codigo = ct.componente_codigo"""

_SQL_CT_LEFT_JOIN_AC = f"""\
SELECT {_CT_FIELDS}, ac.professor
  FROM componente_turma ct
  LEFT JOIN atribuicao_componente ac
         ON ac.turma_codigo = ct.turma_codigo
        AND ac.componente_codigo = ct.componente_codigo"""


def _raw(sql: str, params: list, using: str = "default") -> list[dict]:
    with connections[using].cursor() as cursor:
        cursor.execute(sql, params)
        cols = [c[0] for c in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]


def _componente_para_dict(row: dict) -> dict:
    """Adiciona campos computados ausentes no ORM.

    ExibirComponenteEOL = !TemComponenteVigente.
    O ETL sincroniza apenas componentes ativos (dt_cancelamento IS NULL),
    portanto TemComponenteVigente = True para todos → exibir = False.
    Quando agrupamento=True o service também garante False.
    """
    return {
        **row,
        "codigo_componente_territorio_saber": row.get("codigo_componente_territorio_saber") or 0,
        "exibir_componente_eol": False,
        "codigosTerritoriosAgrupamento": [],
    }


def _grade_para_componente(row: dict) -> dict:
    """Converte linha de GradeComponenteCurricular para shape de ComponenteCurricular."""
    return {
        "codigo": row["codigo_componente_curricular"],
        "codigo_componente_territorio_saber": 0,
        "codigo_componente_curricular_pai": None,
        "descricao": row["descricao_componente_curricular"],
        "regencia": False,
        "planejamento_regencia": False,
        "territorio_saber": False,
        "turma_codigo": None,
        "exibir_componente_eol": True,
        "professor": None,
        "codigosTerritoriosAgrupamento": [],
    }


def _agrupamento_para_dict(
    agrupamento: AgrupamentoAtribuicaoTerritorioSaber,
) -> dict:
    """Formata AgrupamentoAtribuicaoTerritorioSaber para shape de resposta."""
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
        "codigosTerritoriosAgrupamento": codigos,
    }


def _parse_csv(csv_str: str | None) -> list[int]:
    """Converte CSV de códigos de componentes para lista de inteiros."""
    if not csv_str:
        return []
    return [
        int(c.strip())
        for c in csv_str.split(",")
        if c.strip().isdigit()
    ]


class ComponentesRepository:
    """Queries ORM para componentes curriculares."""

    _DB = "default"

    def listar_por_turma_funcionario(
        self,
        codigo_turma: str,
        login: str,
    ) -> list[dict]:
        """Lista componentes por turma e funcionário (EP-1 com codigoTurma)."""
        sql = (
            f"{_SQL_CT_JOIN_AC}"
            " WHERE ac.professor = %s AND ct.turma_codigo = %s"
        )
        rows = _raw(sql, [login, codigo_turma], self._DB)
        return [_componente_para_dict(r) for r in rows]

    def listar_por_funcionario(
        self,
        login: str,
    ) -> list[dict]:
        """Lista todos os componentes do funcionário sem filtro de turma (EP-1).

        Replica o legado: deduplica por codigo e, em seguida, por
        codigo_componente_curricular_pai (colapsando filhos sob o pai).
        turma_codigo é nulo porque não há filtro de turma.
        """
        sql = f"{_SQL_CT_JOIN_AC} WHERE ac.professor = %s"
        rows = _raw(sql, [login], self._DB)

        # 1ª passagem: dedup por codigo (mesmo componente em turmas diferentes)
        seen_codigo: set[int] = set()
        by_codigo: list[dict] = []
        for r in rows:
            if r["codigo"] not in seen_codigo:
                seen_codigo.add(r["codigo"])
                r["turma_codigo"] = None
                r["professor"] = None
                by_codigo.append(_componente_para_dict(r))

        # 2ª passagem: colapsa componentes filhos sob o pai
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
        """Lista componentes de planejamento de regência por turma (EP-1 planejamento)."""
        sql = (
            f"{_SQL_CT_JOIN_AC}"
            " WHERE ac.professor = %s AND ct.turma_codigo = %s"
            " AND ct.planejamento_regencia = %s"
        )
        rows = _raw(sql, [login, codigo_turma, True], self._DB)
        return [_componente_para_dict(r) for r in rows]

    def listar_regencia_por_ano_turma(
        self,
        ano_turma: int,
    ) -> list[dict]:
        """Lista componentes de regência por ano de turma (EP-2)."""
        if ano_turma <= 0:
            codigos = list(
                RegenciaComponenteCurricular.objects.using(self._DB)
                .filter(ano__isnull=True)
                .values_list("id_componente_curricular", flat=True)
            )
        else:
            codigos = list(
                RegenciaComponenteCurricular.objects.using(self._DB)
                .filter(ano=ano_turma)
                .values_list("id_componente_curricular", flat=True)
            )
        componentes = ComponenteCurricular.objects.using(self._DB).filter(
            codigo__in=codigos
        ).values("codigo", "descricao")
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
        """Verifica se a turma possui componente PAP para o funcionário (EP-3)."""
        codigos = list(
            AtribuicaoComponente.objects.using(self._DB)
            .filter(turma_codigo=codigo_turma, professor=login)
            .values_list("componente_codigo", flat=True)
        )
        return ComponenteCurricularPAP.objects.using(self._DB).filter(
            id_componente_curricular__in=codigos
        ).exists()

    def listar_por_ue_modalidade_ano_e_anos_escolares(
        self,
        ue_codigo: str,
        modalidade: int,
        ano_letivo: int,
        anos_escolares: list[str],
    ) -> list[dict]:
        """Lista componentes da grade por UE, modalidade, ano e séries (EP-4)."""
        sql = """
            SELECT DISTINCT
                ct.componente_codigo AS codigo_componente_curricular,
                ct.descricao         AS descricao_componente_curricular
            FROM componente_turma ct
            INNER JOIN turma t ON t.codigo::text = ct.turma_codigo
            WHERE t.ue_codigo = %s
              AND t.codigo_modalidade = %s
              AND ct.ano_letivo = %s
        """
        params: list = [ue_codigo, modalidade, ano_letivo]
        if anos_escolares:
            placeholders = ",".join(["%s"] * len(anos_escolares))
            sql += f" AND ct.ano_turma IN ({placeholders})"
            params.extend(anos_escolares)
        rows = _raw(sql, params, self._DB)
        return [_grade_para_componente(r) for r in rows]

    def listar_turma_programa_por_ue_modalidade_ano(
        self,
        ue_codigo: str,
        modalidade: int,
        ano_letivo: int,
    ) -> list[dict]:
        """Lista componentes de turmas programa por UE, modalidade e ano (EP-5)."""
        modalidades_validas = {1, 3, 4, 5, 6}
        if modalidade not in modalidades_validas:
            return []

        sql = """
            SELECT DISTINCT
                ct.componente_codigo AS codigo_componente_curricular,
                ct.descricao         AS descricao_componente_curricular
            FROM componente_turma ct
            INNER JOIN turma t ON t.codigo::text = ct.turma_codigo
            WHERE t.ue_codigo = %s
              AND ct.ano_letivo = %s
              AND t.codigo_tipo_programa IS NOT NULL
        """
        params: list = [ue_codigo, ano_letivo]

        if modalidade == 1:
            series = (23, 24, 25, 26, 116, 117, 118, 119, 225, 297)
            placeholders = ",".join(["%s"] * len(series))
            sql += f" AND ct.codigo_serie_ensino IN ({placeholders})"
            params.extend(series)

        rows = _raw(sql, params, self._DB)
        return [_grade_para_componente(r) for r in rows]

    def listar_por_ue_e_turmas(
        self,
        turmas: list[str],
    ) -> list[dict]:
        """Lista componentes simplificados por lista de turmas (EP-6)."""
        qs = ComponenteTurma.objects.using(self._DB).exclude(componente_codigo=0)
        if turmas:
            qs = qs.filter(turma_codigo__in=turmas)
        return list(
            qs.annotate(codigo=F("componente_codigo"))
            .values("codigo", "descricao")
            .distinct()
            .order_by("descricao")
        )

    def listar_por_lista_turmas(
        self,
        codigos_turmas: list[str],
    ) -> list[dict]:
        """Lista componentes de múltiplas turmas para planejamento (EP-7)."""
        if not codigos_turmas:
            return []
        placeholders = ",".join(["%s"] * len(codigos_turmas))
        sql = f"""\
SELECT {_CT_FIELDS}, ac.professor
  FROM componente_turma ct
  JOIN turma t ON t.codigo::varchar = ct.turma_codigo AND t.extinta = false
  LEFT JOIN atribuicao_componente ac
         ON ac.turma_codigo = ct.turma_codigo
        AND ac.componente_codigo = ct.componente_codigo
 WHERE ct.turma_codigo IN ({placeholders})"""
        rows = _raw(sql, list(codigos_turmas), self._DB)
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
        """Lista componentes sem pós-processamento (EP-8)."""
        if not codigos_turmas:
            return []
        placeholders = ",".join(["%s"] * len(codigos_turmas))
        sql = f"""\
SELECT DISTINCT
    ct.componente_codigo AS codigo,
    ct.codigo_componente_territorio_saber,
    ct.codigo_componente_curricular_pai,
    ct.descricao, ct.regencia, ct.planejamento_regencia,
    ct.territorio_saber, ct.turma_codigo, ct.ano_letivo
  FROM componente_turma ct
  JOIN turma t ON t.codigo::varchar = ct.turma_codigo AND t.extinta = false
 WHERE ct.turma_codigo IN ({placeholders})"""
        rows = _raw(sql, list(codigos_turmas), self._DB)
        for r in rows:
            r["professor"] = None
        return [_componente_para_dict(r) for r in rows]

    def listar_catalogo(self) -> list[dict]:
        """Lista o catálogo completo de componentes (EP-9)."""
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
        """Lista vigência de componentes por turma e UE (EP-10).

        JOIN entre componente_turma, turma e atribuicao_componente.
        Exclui turmas programa (tipo_turma=3) e atribuições externas.
        Filtra por semestre via turma.semestre quando informado.
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
        sql = f"""
SELECT DISTINCT
    ct.componente_codigo::varchar AS componente_codigo,
    ct.descricao                  AS componente_descricao,
    ct.turma_codigo,
    t.data_inicio_turma
FROM componente_turma ct
JOIN turma t
  ON t.codigo::varchar = ct.turma_codigo
JOIN atribuicao_componente ac
  ON ac.turma_codigo = ct.turma_codigo
 AND ac.componente_codigo = ct.componente_codigo
 AND ac.atribuicao_externa = false
WHERE t.ue_codigo = %s
  AND t.ano_letivo = %s
  AND ct.componente_codigo IN ({placeholders})
  AND t.tipo_turma != 3
  {semestre_clause}
"""
        return _raw(sql, params, self._DB)

    def listar_grade_curricular(
        self,
        ano_letivo: int,
    ) -> list[dict]:
        """Lista grade curricular completa por ano letivo (EP-11)."""
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
        """Lista componentes sem professor atribuído na turma (EP-12)."""
        sql = """\
SELECT ct.descricao
  FROM componente_turma ct
  JOIN turma t ON t.codigo::varchar = ct.turma_codigo AND t.extinta = false
  LEFT JOIN atribuicao_componente ac
         ON ac.turma_codigo = ct.turma_codigo
        AND ac.componente_codigo = ct.componente_codigo
 WHERE ct.turma_codigo = %s
   AND ac.turma_codigo IS NULL"""
        rows = _raw(sql, [codigo_turma], self._DB)
        return [r["descricao"] for r in rows]

    def listar_agrupamentos_correlacionados(
        self,
        codigo_componente: int,
        data_base: date | None,
    ) -> list[dict]:
        """Retorna agrupamentos correlacionados de território do saber (EP-13)."""
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
        """Retorna agrupamentos correlacionados em lote (EP-14)."""
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
        """Retorna agrupamentos de território do saber por IDs (EP-15)."""
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
