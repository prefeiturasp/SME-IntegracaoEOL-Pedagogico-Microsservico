"""Serviços do domínio Turmas."""

from apps.turmas.repository import TurmasRepository


class TurmasService:
    """Orquestra as operações do domínio Turmas."""

    def __init__(self) -> None:
        self._repo = TurmasRepository()

    def turmas_regulares(self, codigos: list[int]) -> list[dict]:
        """Retorna turmas regulares da lista de códigos.

        Args:
            codigos: Códigos das turmas a consultar.

        Returns:
            Lista de turmas regulares encontradas.
        """
        return self._repo.turmas_regulares(codigos)

    def turmas_programa(self, codigos: list[int]) -> list[dict]:
        """Retorna turmas programa da lista de códigos.

        Args:
            codigos: Códigos das turmas a consultar.

        Returns:
            Lista de turmas programa encontradas.
        """
        return self._repo.turmas_programa(codigos)

    def listar_turmas(self, codigos: list[int]) -> list[dict]:
        """Retorna turmas da lista de códigos.

        Args:
            codigos: Códigos das turmas a consultar.

        Returns:
            Lista de turmas encontradas.
        """
        return self._repo.listar_turmas(codigos)

    def dados_turma(self, codigo: int) -> dict | None:
        """Retorna dados canônicos de uma turma.

        Args:
            codigo: Código da turma.

        Returns:
            Dados da turma, ou None se não encontrada.
        """
        return self._repo.dados_turma(codigo)

    def sincronizacoes_institucionais(
        self,
        ue_codigo: str,
        turma_codigo: int,
    ) -> dict | None:
        """Retorna dados de sincronização institucional da turma.

        Args:
            ue_codigo: Código da unidade educacional, obrigatório no
                contrato mas não usado na consulta.
            turma_codigo: Código da turma.

        Returns:
            Dados de sincronização, ou None se não encontrada.
        """
        return self._repo.sincronizacoes_institucionais(
            ue_codigo, turma_codigo
        )

    def codigos_turmas_por_ue(
        self,
        ue_codigo: str,
        anos_letivos: list[int] | None,
    ) -> list[int]:
        """Retorna códigos de turma da UE.

        Args:
            ue_codigo: Código da unidade educacional.
            anos_letivos: Anos letivos a filtrar; quando vazio, lista todos.

        Returns:
            Códigos de turma da UE, em ordem crescente.
        """
        return self._repo.codigos_turmas_por_ue(ue_codigo, anos_letivos)

    def turmas_historicas_professor(
        self,
        ano_letivo: int,
        professor_rf: str,
    ) -> list[dict]:
        """Retorna turmas históricas do professor.

        Args:
            ano_letivo: Ano letivo consultado.
            professor_rf: Registro funcional do professor.

        Returns:
            Lista de turmas históricas do professor no ano letivo.
        """
        return self._repo.turmas_historicas_professor(ano_letivo, professor_rf)

    def itinerarios_ensino_medio(self) -> list[dict]:
        """Retorna itinerários do Ensino Médio ordenados por id.

        Returns:
            Lista de itinerários do Ensino Médio.
        """
        return self._repo.itinerarios_ensino_medio()
