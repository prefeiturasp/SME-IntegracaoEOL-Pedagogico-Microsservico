"""Queries SQL do domínio Componentes Curriculares."""

from apps.componentes_curriculares.constants import (
    CODIGO_COMPONENTE_REGENCIA_CLASSE_INFANTIL,
    MOTIVO_DISPONIBILIZACAO_FIM_ANO_LETIVO,
    TIPO_TURMA_EVENTO_PARA_ATRIBUICAO,
    TIPO_TURMA_PROGRAMA,
)

MOTIVO_FIM_ANO = MOTIVO_DISPONIBILIZACAO_FIM_ANO_LETIVO
SQL_COMPONENTE_TERRITORIO_SABER = """\
(
        ct.codigo_componente_territorio_saber IS NOT NULL
        OR ct.componente_codigo BETWEEN 1214 AND 1225
        OR ct.componente_codigo BETWEEN 1519 AND 1522
    )"""

COMPONENTE_TURMA_CAMPOS_RESPOSTA = f"""\
    ct.componente_codigo AS codigo,
    ct.codigo_componente_territorio_saber,
    cch.idcomponentecurricularpai AS codigo_componente_curricular_pai,
    CASE
        WHEN ct.codigo_componente_territorio_saber IS NOT NULL
         AND ct.desc_territorio_saber IS NOT NULL
        THEN
            CASE
                WHEN ct.desc_experiencia_pedagogica IS NOT NULL
                THEN btrim(ct.desc_territorio_saber) || ' - ' ||
                     btrim(ct.desc_experiencia_pedagogica)
                ELSE btrim(ct.desc_territorio_saber)
            END
        ELSE cc.descricao
    END AS descricao,
    COALESCE(cc.regencia, false) AS regencia,
    false AS planejamento_regencia,
    {SQL_COMPONENTE_TERRITORIO_SABER} AS territorio_saber,
    ct.turma_codigo,
    ct.tipo_escola,
    t.ano_letivo,
    t.duracao_turno AS turno_turma,
    t.ano AS ano_turma"""

SQL_FILTRO_ATRIBUICAO_POR_TURMA = f"""\
 AND ac.dt_cancelamento IS NULL
 AND (
       ac.dt_disponibilizacao >= make_date(t.ano_letivo, 2, 5)
       OR ac.dt_disponibilizacao IS NULL
       OR ac.cd_motivo_disponibilizacao = {MOTIVO_FIM_ANO}
       OR COALESCE(cc.regencia, false)
       OR ct.componente_codigo = {CODIGO_COMPONENTE_REGENCIA_CLASSE_INFANTIL}
       OR cch.idcomponentecurricularpai =
          {CODIGO_COMPONENTE_REGENCIA_CLASSE_INFANTIL}
     )"""

SQL_FILTRO_ATRIBUICAO_VIGENTE = """\
 AND ac.dt_cancelamento IS NULL
 AND ac.dt_disponibilizacao IS NULL"""

SQL_COMPONENTE_NAO_VIGENTE = """\
NOT EXISTS (
    SELECT 1
      FROM componente_curricular_hierarquia h_vigente
     WHERE h_vigente.idcomponentecurricular = ct.componente_codigo
       AND (
             h_vigente.vigencia >=
                 CASE
                     WHEN COALESCE(
                              NULLIF(t.ano_letivo, 0),
                              EXTRACT(YEAR FROM CURRENT_DATE)::integer
                          ) = EXTRACT(YEAR FROM CURRENT_DATE)::integer
                     THEN CURRENT_DATE
                     ELSE make_date(t.ano_letivo, 12, 31)
                 END
             OR (
                  h_vigente.vigencia IS NULL
                  AND h_vigente.id > 0
                )
           )
)"""

SQL_COMPONENTES_TURMA_COM_ATRIBUICAO = f"""\
SELECT {COMPONENTE_TURMA_CAMPOS_RESPOSTA},
       {SQL_COMPONENTE_NAO_VIGENTE} AS exibir_componente_eol,
       ac.professor
  FROM componente_turma ct
  LEFT JOIN componente_curricular cc
    ON cc.codigo = ct.componente_codigo
  LEFT JOIN LATERAL (
    SELECT h.idcomponentecurricularpai
      FROM componente_curricular_hierarquia h
     WHERE h.idcomponentecurricular = ct.componente_codigo
     ORDER BY h.vigencia DESC NULLS LAST
     LIMIT 1
  ) cch ON true
  JOIN turma t
    ON t.codigo::varchar = ct.turma_codigo
  JOIN atribuicao_componente ac
    ON ac.turma_codigo = ct.turma_codigo
   AND ac.componente_codigo = ct.componente_codigo"""

# Componentes com hierarquia são apresentados pelo componente pai; o DISTINCT
# remove filhos duplicados após a normalização.
SQL_COMPONENTES_GRADE_POR_UE_MODALIDADE_ANO = """
    SELECT DISTINCT
        COALESCE(
            ccp.codigo,
            ct.componente_codigo
        ) AS codigo_componente_curricular,
        cch.idcomponentecurricularpai AS codigo_componente_curricular_pai,
        COALESCE(
            ccp.descricao,
            cc.descricao
        ) AS descricao_componente_curricular,
        COALESCE(
            ccp.regencia,
            cc.regencia,
            false
        ) AS regencia
    FROM componente_turma ct
    INNER JOIN componente_curricular cc
            ON cc.codigo = ct.componente_codigo
    LEFT JOIN LATERAL (
        SELECT h.idcomponentecurricularpai
          FROM componente_curricular_hierarquia h
         WHERE h.idcomponentecurricular = ct.componente_codigo
         ORDER BY h.vigencia DESC NULLS LAST
         LIMIT 1
    ) cch ON true
    LEFT JOIN componente_curricular ccp
           ON ccp.codigo = cch.idcomponentecurricularpai
    INNER JOIN turma t ON t.codigo::text = ct.turma_codigo
    WHERE t.ue_codigo = %s
      AND t.codigo_modalidade_etapa = %s
      AND t.ano_letivo = %s
"""

# Turmas programa seguem a mesma normalização de componente pai da grade.
SQL_COMPONENTES_TURMA_PROGRAMA = f"""
    SELECT DISTINCT
        COALESCE(
            ccp.codigo,
            ct.componente_codigo
        ) AS codigo_componente_curricular,
        cch.idcomponentecurricularpai AS codigo_componente_curricular_pai,
        COALESCE(
            ccp.descricao,
            cc.descricao
        ) AS descricao_componente_curricular,
        COALESCE(
            ccp.regencia,
            cc.regencia,
            false
        ) AS regencia
    FROM componente_turma ct
    INNER JOIN componente_curricular cc
            ON cc.codigo = ct.componente_codigo
    LEFT JOIN LATERAL (
        SELECT h.idcomponentecurricularpai
          FROM componente_curricular_hierarquia h
         WHERE h.idcomponentecurricular = ct.componente_codigo
         ORDER BY h.vigencia DESC NULLS LAST
         LIMIT 1
    ) cch ON true
    LEFT JOIN componente_curricular ccp
           ON ccp.codigo = cch.idcomponentecurricularpai
    INNER JOIN turma t ON t.codigo::text = ct.turma_codigo
    WHERE t.ue_codigo = %s
      AND t.ano_letivo = %s
      AND t.codigo_tipo_programa IS NOT NULL
      AND t.tipo_turma != {TIPO_TURMA_EVENTO_PARA_ATRIBUICAO}
"""

SQL_COMPONENTES_SIMPLIFICADOS_POR_TURMAS = """\
SELECT DISTINCT
    ct.componente_codigo AS codigo,
    cc.descricao
  FROM componente_turma ct
  JOIN componente_curricular cc
    ON cc.codigo = ct.componente_codigo
  JOIN turma t
    ON t.codigo::varchar = ct.turma_codigo
 WHERE ct.componente_codigo <> 0"""

SQL_COMPONENTES_POR_LISTA_TURMAS = f"""\
SELECT {COMPONENTE_TURMA_CAMPOS_RESPOSTA}, ac.professor
  FROM componente_turma ct
  LEFT JOIN componente_curricular cc
    ON cc.codigo = ct.componente_codigo
  LEFT JOIN LATERAL (
    SELECT h.idcomponentecurricularpai
      FROM componente_curricular_hierarquia h
     WHERE h.idcomponentecurricular = ct.componente_codigo
     ORDER BY h.vigencia DESC NULLS LAST
     LIMIT 1
  ) cch ON true
  JOIN turma t ON t.codigo::varchar = ct.turma_codigo AND t.extinta = false
  LEFT JOIN atribuicao_componente ac
         ON ac.turma_codigo = ct.turma_codigo
        AND ac.componente_codigo = ct.componente_codigo
        AND ac.dt_cancelamento IS NULL
        AND (
              ac.dt_disponibilizacao >= make_date(t.ano_letivo, 2, 5)
              OR ac.dt_disponibilizacao IS NULL
              OR ac.cd_motivo_disponibilizacao = {MOTIVO_FIM_ANO}
            )
 WHERE ct.turma_codigo IN ({{placeholders}})"""

# Variante que NÃO exclui turmas extintas — usada na consulta de disciplinas
# por turma, para manter paridade com o legado (que retorna disciplinas mesmo
# de turmas extintas). Derivada da query base para evitar duplicação.
SQL_COMPONENTES_POR_LISTA_TURMAS_INCLUI_EXTINTAS = (
    SQL_COMPONENTES_POR_LISTA_TURMAS.replace(" AND t.extinta = false", "")
)

SQL_COMPONENTES_TURMAS_BRUTOS = f"""\
SELECT DISTINCT
    ct.componente_codigo AS codigo,
    ct.codigo_componente_territorio_saber,
    cch.idcomponentecurricularpai AS codigo_componente_curricular_pai,
    cc.descricao,
    COALESCE(cc.regencia, false) AS regencia,
    false AS planejamento_regencia,
    {SQL_COMPONENTE_TERRITORIO_SABER} AS territorio_saber,
    ct.turma_codigo,
    ct.tipo_escola,
    t.ano_letivo,
    t.duracao_turno AS turno_turma,
    t.ano AS ano_turma
  FROM componente_turma ct
  LEFT JOIN componente_curricular cc
    ON cc.codigo = ct.componente_codigo
  LEFT JOIN LATERAL (
    SELECT h.idcomponentecurricularpai
      FROM componente_curricular_hierarquia h
     WHERE h.idcomponentecurricular = ct.componente_codigo
     ORDER BY h.vigencia DESC NULLS LAST
     LIMIT 1
  ) cch ON true
  JOIN turma t ON t.codigo::varchar = ct.turma_codigo AND t.extinta = false
 WHERE ct.turma_codigo IN ({{placeholders}})"""

SQL_VIGENCIA_COMPONENTES = f"""
SELECT DISTINCT
    ct.componente_codigo::varchar AS componente_codigo,
    cc.descricao                  AS componente_descricao,
    ct.turma_codigo,
    t.data_inicio_turma
FROM componente_turma ct
JOIN componente_curricular cc
  ON cc.codigo = ct.componente_codigo
JOIN turma t
  ON t.codigo::varchar = ct.turma_codigo
JOIN atribuicao_componente ac
  ON ac.turma_codigo = ct.turma_codigo
 AND ac.componente_codigo = ct.componente_codigo
 AND ac.atribuicao_externa = false
 AND ac.dt_cancelamento IS NULL
 AND (
       ac.dt_disponibilizacao >= make_date(t.ano_letivo, 2, 5)
       OR ac.dt_disponibilizacao IS NULL
       OR ac.cd_motivo_disponibilizacao = {MOTIVO_FIM_ANO}
     )
WHERE t.ue_codigo = %s
  AND t.ano_letivo = %s
  AND ct.componente_codigo IN ({{placeholders}})
  AND t.tipo_turma != {TIPO_TURMA_PROGRAMA}
  {{semestre_clause}}
"""

SQL_COMPONENTES_SEM_ATRIBUICAO = """\
SELECT DISTINCT ct.componente_codigo AS codigo
  FROM componente_turma ct
  JOIN turma t ON t.codigo::varchar = ct.turma_codigo AND t.extinta = false
  LEFT JOIN atribuicao_componente ac
         ON ac.turma_codigo = ct.turma_codigo
        AND ac.componente_codigo = ct.componente_codigo
        AND ac.dt_cancelamento IS NULL
        AND %s BETWEEN ac.dt_atribuicao::date
                   AND COALESCE(ac.dt_disponibilizacao::date, %s)
 WHERE ct.turma_codigo = %s
   AND ac.turma_codigo IS NULL
 ORDER BY ct.componente_codigo"""
