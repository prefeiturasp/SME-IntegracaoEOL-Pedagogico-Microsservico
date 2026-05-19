"""Serviços do domínio Turmas."""

from apps.turmas.repository import TurmasRepository


class TurmasService:
    """Orquestra as operações do domínio Turmas."""

    def __init__(self) -> None:
        self._repo = TurmasRepository()

    def turmas_regulares(self, codigos: list[int]) -> list[dict]:
        """Retorna turmas regulares da lista de códigos."""
        return self._repo.turmas_regulares(codigos)

    def turmas_programa(self, codigos: list[int]) -> list[dict]:
        """Retorna turmas programa da lista de códigos."""
        return self._repo.turmas_programa(codigos)

    def listar_turmas(self, codigos: list[int]) -> list[dict]:
        """Retorna turmas da lista de códigos."""
        return self._repo.listar_turmas(codigos)

    def dados_turma(self, codigo: int) -> dict | None:
        """Retorna dados canônicos de uma turma."""
        return self._repo.dados_turma(codigo)

    def sincronizacoes_institucionais(
        self,
        ue_codigo: str,
        turma_codigo: int,
    ) -> dict | None:
        """Retorna dados de sincronização institucional da turma por UE."""
        return self._repo.sincronizacoes_institucionais(
            ue_codigo, turma_codigo
        )

    def anos_letivos_por_ue(self, ue_codigo: str) -> list[int]:
        """Retorna anos letivos com turmas na UE."""
        return self._repo.anos_letivos_por_ue(ue_codigo)

    def turmas_historicas_professor(
        self,
        ano_letivo: int,
        professor_rf: str,
    ) -> list[dict]:
        """Retorna turmas históricas do professor."""
        return self._repo.turmas_historicas_professor(ano_letivo, professor_rf)

    def itinerarios_ensino_medio(self) -> list[dict]:
        """Retorna itinerários do Ensino Médio ordenados por nome."""
        return self._repo.itinerarios_ensino_medio()
