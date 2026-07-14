"""Constantes do domínio Turmas."""

MENSAGEM_COMPORTAMENTO_INESPERADO = (
    "Houve um comportamento inesperado do sistema. "
    "Por favor, contate a SME."
)

ETAPA_ENSINO_MAGISTERIO = 9
TIPO_GRADE_PROGRAMA_ITINERARIO = 23

# 1=AnualInício1ºSem, 2=AnualInício2ºSem, 3=SemestralInício1ºSem,
# 4=SemestralInício2ºSem. Semestre 1 => início no 1º semestre (1,3);
# semestre 2 => início no 2º semestre (2,4).
PERIODICIDADES_POR_SEMESTRE = {
    1: (1, 3),
    2: (2, 4),
}

TIPOS_ESCOLA_TURMAS_HISTORICAS_PROFESSOR = (1, 2, 3, 4, 16, 28, 31)
ETAPAS_ENSINO_TURMAS_HISTORICAS_PROFESSOR = (
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    10,
    11,
    12,
    13,
    14,
    17,
)

CODIGO_GRADE_PROGRAMA_LINGUAGENS = 5148
CODIGO_GRADE_PROGRAMA_HUMANAS_SOCIAIS = 5149
CODIGO_GRADE_PROGRAMA_CIENCIAS_MATEMATICA = 5150

DESCRICOES_GRADE_PROGRAMA_ITINERARIO = {
    CODIGO_GRADE_PROGRAMA_LINGUAGENS: "Linguagens",
    CODIGO_GRADE_PROGRAMA_HUMANAS_SOCIAIS: "Humanas e Sociais",
    CODIGO_GRADE_PROGRAMA_CIENCIAS_MATEMATICA: "Ciências e Matemática",
}
