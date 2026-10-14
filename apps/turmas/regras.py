"""Regras do domínio Turmas."""

_MARCADOR_PRIMEIRO_CICLO = " I "
_MARCADOR_SEGUNDO_CICLO = " II"


def ciclo_eja(serie_ensino: str | None) -> int:
    """Retorna o ciclo EJA indicado na descrição da série de ensino.

    Args:
        serie_ensino: Descrição da série de ensino da turma.

    Returns:
        1 para o ciclo I, 2 para o ciclo II e 0 quando não identificável.
    """
    if not serie_ensino or len(serie_ensino) <= 2:
        return 0
    sufixo = serie_ensino[-2:].strip()
    tem_primeiro = _MARCADOR_PRIMEIRO_CICLO in serie_ensino
    tem_segundo = _MARCADOR_SEGUNDO_CICLO in serie_ensino
    if not tem_segundo and (tem_primeiro or sufixo == "I"):
        return 1
    if not tem_primeiro and (tem_segundo or sufixo == "II"):
        return 2
    return 0
