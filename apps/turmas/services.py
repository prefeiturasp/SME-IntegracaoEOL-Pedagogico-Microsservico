"""Services do domínio Turmas.

Orquestra o fluxo de negócio de cada endpoint. Não monta SQL — apenas
decide qual método do repository chamar e aplica decisões de contrato.
"""

from apps.turmas.repository import TurmasRepository


class TurmasService:
    """Orquestra as operações do domínio Turmas."""

    def __init__(self) -> None:
        self._repo = TurmasRepository()

    def turmas_regulares(self, codigos: list[int]) -> list[dict]:
        """Retorna turmas regulares (tipo_turma=1) da lista de códigos."""
        return self._repo.turmas_regulares(codigos)

    def turmas_programa(self, codigos: list[int]) -> list[dict]:
        """Retorna turmas programa (tipo_turma=3) da lista de códigos."""
        return self._repo.turmas_programa(codigos)

    def listar_turmas(self, codigos: list[int]) -> list[dict]:
        """Retorna turmas pelos códigos fornecidos, sem filtro de tipo."""
        return self._repo.listar_turmas(codigos)

    def dados_turma(self, codigo: int) -> dict | None:
        """Retorna dados canônicos de uma turma. None se não existir."""
        return self._repo.dados_turma(codigo)

    def sincronizacoes_institucionais(
        self,
        ue_codigo: str,
        turma_codigo: int,
    ) -> dict | None:
        """Retorna dados de sincronização institucional da turma por UE."""
        return self._repo.sincronizacoes_institucionais(ue_codigo, turma_codigo)

    def anos_letivos_por_ue(self, ue_codigo: str) -> list[int]:
        """Retorna anos letivos distintos com turmas na UE (exclui tipo_turma=4)."""
        return self._repo.anos_letivos_por_ue(ue_codigo)

    def turmas_historicas_professor(
        self,
        ano_letivo: int,
        professor_rf: str,
    ) -> list[dict]:
        """Retorna turmas históricas do professor via AtribuicaoComponente."""
        return self._repo.turmas_historicas_professor(ano_letivo, professor_rf)

    def itinerarios_ensino_medio(self) -> list[dict]:
        """Retorna itinerários do Ensino Médio ordenados por nome."""
        return self._repo.itinerarios_ensino_medio()
