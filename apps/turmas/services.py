"""Serviços do domínio Turmas."""

from typing import Any

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

    def turmas_atribuidas_dre_ue(self, codigos_ue: list[str]) -> list[dict]:
        """Retorna turmas atribuídas das unidades.

        Args:
            codigos_ue: Códigos das unidades educacionais.

        Returns:
            Lista de turmas atribuídas encontradas.
        """
        return self._repo.turmas_atribuidas_dre_ue(codigos_ue)

    def todas_turmas_atribuidas_dre_ue(self) -> dict[str, Any]:
        """Retorna turmas atribuídas."""
        return self._repo.todas_turmas_atribuidas_dre_ue()

    def turmas_atribuidas_dre_ue_por_dre(
        self, codigo_dre: str
    ) -> dict[str, Any]:
        """Retorna a abrangência de uma DRE.

        Args:
            codigo_dre: Código EOL da DRE.

        Returns:
            Estrutura agrupada por DRE/UE/turma.
        """
        return self._repo.turmas_atribuidas_dre_ue_por_dre(codigo_dre)

    def turmas_atribuidas_dre_ue_por_turmas(
        self, codigos_turma: list[int]
    ) -> dict[str, Any]:
        """Retorna a abrangência de uma lista de turmas.

        Args:
            codigos_turma: Códigos das turmas a consultar.

        Returns:
            Estrutura agrupada por DRE/UE/turma.
        """
        return self._repo.turmas_atribuidas_dre_ue_por_turmas(codigos_turma)

    def turmas_elegiveis(
        self,
        codigo_rf: str,
        codigo_turma: int,
        componente_curricular: int,
    ) -> list[dict]:
        """Retorna turmas elegíveis por atribuição.

        Args:
            codigo_rf: RF usado na consulta.
            codigo_turma: Turma base da consulta.
            componente_curricular: Componente usado no filtro.

        Returns:
            Lista de turmas elegíveis encontradas.
        """
        return self._repo.turmas_elegiveis(
            codigo_rf,
            codigo_turma,
            componente_curricular,
        )

    def turmas_recorte_fund_medio_eja(self, codigos: list[int]) -> list[dict]:
        """Retorna turmas no recorte de etapa (Fund/Médio/EJA).

        Args:
            codigos: Códigos das turmas a consultar.

        Returns:
            Lista de turmas no recorte de etapa encontradas.
        """
        return self._repo.turmas_recorte_fund_medio_eja(codigos)

    def codigos_turmas_por_ano_modalidade_dre(
        self,
        ues_codigos: list[str],
        ano_turma: str | None = None,
        codigo_modalidade: int | None = None,
        ano_letivo: int | None = None,
    ) -> list[int]:
        """Lista códigos de turmas vigentes para a contagem de alunos.

        Args:
            ues_codigos: Códigos EOL das UEs consideradas.
            ano_turma: Primeiro caractere da nomenclatura da turma.
            codigo_modalidade: Modalidade materializada.
            ano_letivo: Ano letivo da chamada.

        Returns:
            Códigos distintos das turmas que atendem ao recorte.
        """
        return self._repo.codigos_turmas_por_ano_modalidade_dre(
            ues_codigos, ano_turma, codigo_modalidade, ano_letivo
        )

    def turmas_recorte_por_tipo(
        self,
        codigos: list[int],
        tipos_turma: list[int] | None = None,
        ue_codigo: str | None = None,
        semestre: int | None = None,
    ) -> list[int]:
        """Filtra códigos de turma por tipo de turma, UE e semestre.

        Args:
            codigos: Códigos de turma candidatos.
            tipos_turma: Tipos de turma aceitos; sem filtro quando vazio.
            ue_codigo: Código da UE; sem filtro quando ausente.
            semestre: Semestre da turma; sem filtro quando ausente.

        Returns:
            Subconjunto dos códigos que atende ao recorte.
        """
        return self._repo.turmas_recorte_por_tipo(
            codigos, tipos_turma, ue_codigo, semestre
        )

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

    def modalidades_ensino(self) -> list[str]:
        """Retorna as descrições do catálogo de etapas de ensino.

        Returns:
            Descrições das etapas de ensino.
        """
        return self._repo.modalidades_ensino()

    def turmas_por_tipo_sala(
        self,
        ue_codigo: str,
        tipo_sala: str,
        ano_letivo: str,
    ) -> list[dict]:
        """Retorna turmas de uma UE/ano letivo por tipo de sala.

        Args:
            ue_codigo: Código da unidade educacional.
            tipo_sala: Tipo de sala informado na rota (texto).
            ano_letivo: Ano letivo informado na rota (texto).

        Returns:
            Turmas encontradas no recorte; lista vazia se ``tipo_sala`` ou
            ``ano_letivo`` não forem numéricos (não filtram nada, mesma
            convenção para os dois parâmetros).
        """
        tipo_turma = int(tipo_sala) if tipo_sala.strip().isdigit() else 0
        if not ano_letivo.strip().isdigit():
            return []
        return self._repo.turmas_por_tipo_sala(
            ue_codigo, tipo_turma, int(ano_letivo)
        )

    def turmas_por_escola(
        self,
        ue_codigo: str,
        ano_letivo: str,
    ) -> list[dict]:
        """Retorna turmas de uma UE/ano letivo cujo nome começa com dígito.

        Args:
            ue_codigo: Código da unidade educacional.
            ano_letivo: Ano letivo informado na rota (texto).

        Returns:
            Turmas encontradas, ordenadas por nome; lista vazia se
            ``ano_letivo`` não for numérico.
        """
        if not ano_letivo.strip().isdigit():
            return []
        return self._repo.turmas_por_escola(ue_codigo, int(ano_letivo))

    def turmas_sondagem(
        self,
        ue_codigo: str,
        ano_letivo: str,
    ) -> list[dict]:
        """Retorna turmas regulares de 5º ano do Fundamental para Sondagem.

        Args:
            ue_codigo: Código da unidade educacional.
            ano_letivo: Ano letivo informado na rota (texto).

        Returns:
            Turmas encontradas, ordenadas por nome; lista vazia se
            ``ano_letivo`` não for numérico.
        """
        if not ano_letivo.strip().isdigit():
            return []
        return self._repo.turmas_sondagem(ue_codigo, int(ano_letivo))
