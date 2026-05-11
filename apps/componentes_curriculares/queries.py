"""Queries SQL do domínio Componentes Curriculares."""

COMPONENTE_TURMA_CAMPOS_RESPOSTA = """\
    ct.componente_codigo AS codigo,
    ct.codigo_componente_territorio_saber,
    cch.idcomponentecurricularpai AS codigo_componente_curricular_pai,
    cc.descricao,
    COALESCE(cc.regencia, false) AS regencia,
    false AS planejamento_regencia,
    (ct.codigo_componente_territorio_saber IS NOT NULL) AS territorio_saber,
    ct.turma_codigo,
    t.ano_letivo,
    t.duracao_turno AS turno_turma,
    t.ano AS ano_turma"""

SQL_COMPONENTES_TURMA_COM_ATRIBUICAO = f"""\
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
  JOIN turma t
    ON t.codigo::varchar = ct.turma_codigo
  JOIN atribuicao_componente ac
    ON ac.turma_codigo = ct.turma_codigo
   AND ac.componente_codigo = ct.componente_codigo"""

SQL_COMPONENTES_GRADE_POR_UE_MODALIDADE_ANO = """
    SELECT DISTINCT
        ct.componente_codigo AS codigo_componente_curricular,
        cc.descricao         AS descricao_componente_curricular
    FROM componente_turma ct
    INNER JOIN componente_curricular cc
            ON cc.codigo = ct.componente_codigo
    INNER JOIN turma t ON t.codigo::text = ct.turma_codigo
    WHERE t.ue_codigo = %s
      AND t.codigo_modalidade = %s
      AND t.ano_letivo = %s
"""

SQL_COMPONENTES_TURMA_PROGRAMA = """
    SELECT DISTINCT
        ct.componente_codigo AS codigo_componente_curricular,
        cc.descricao         AS descricao_componente_curricular
    FROM componente_turma ct
    INNER JOIN componente_curricular cc
            ON cc.codigo = ct.componente_codigo
    INNER JOIN turma t ON t.codigo::text = ct.turma_codigo
    WHERE t.ue_codigo = %s
      AND t.ano_letivo = %s
      AND t.codigo_tipo_programa IS NOT NULL
"""

SQL_COMPONENTES_SIMPLIFICADOS_POR_TURMAS = """\
SELECT DISTINCT
    ct.componente_codigo AS codigo,
    cc.descricao
  FROM componente_turma ct
  JOIN componente_curricular cc
    ON cc.codigo = ct.componente_codigo
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
 WHERE ct.turma_codigo IN ({{placeholders}})"""

SQL_COMPONENTES_TURMAS_BRUTOS = """\
SELECT DISTINCT
    ct.componente_codigo AS codigo,
    ct.codigo_componente_territorio_saber,
    cch.idcomponentecurricularpai AS codigo_componente_curricular_pai,
    cc.descricao,
    COALESCE(cc.regencia, false) AS regencia,
    false AS planejamento_regencia,
    (ct.codigo_componente_territorio_saber IS NOT NULL) AS territorio_saber,
    ct.turma_codigo,
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
 WHERE ct.turma_codigo IN ({placeholders})"""

SQL_VIGENCIA_COMPONENTES = """
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
WHERE t.ue_codigo = %s
  AND t.ano_letivo = %s
  AND ct.componente_codigo IN ({placeholders})
  AND t.tipo_turma != 3
  {semestre_clause}
"""

SQL_COMPONENTES_SEM_ATRIBUICAO = """\
SELECT cc.descricao
  FROM componente_turma ct
  JOIN componente_curricular cc
    ON cc.codigo = ct.componente_codigo
  JOIN turma t ON t.codigo::varchar = ct.turma_codigo AND t.extinta = false
  LEFT JOIN atribuicao_componente ac
         ON ac.turma_codigo = ct.turma_codigo
        AND ac.componente_codigo = ct.componente_codigo
 WHERE ct.turma_codigo = %s
   AND ac.turma_codigo IS NULL"""
