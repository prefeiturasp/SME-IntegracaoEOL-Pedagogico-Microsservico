"""Serviços do domínio Componentes Curriculares."""
from datetime import date

from apps.componentes_curriculares.repository import ComponentesRepository


class ComponentesService:
    """Orquestra as operações de Componentes Curriculares."""

    def __init__(self) -> None:
        self._repo = ComponentesRepository()

    def listar_componentes_por_funcionario(
        self,
        login: str,
        codigo_turma: str | None = None,
        planejamento: bool = False,
    ) -> list[dict]:
        """Retorna componentes do funcionário com roteamento por params (EP-1).

        - sem codigoTurma: todos os componentes do funcionário
        - com codigoTurma + planejamento=True: filtra planejamento de regência
        - com codigoTurma + planejamento=False: componentes da turma
        """
        if codigo_turma is None:
            return self._repo.listar_por_funcionario(login)
        if planejamento:
            return self._repo.listar_planejamento_por_turma_funcionario(
                codigo_turma, login
            )
        return self._repo.listar_por_turma_funcionario(
            codigo_turma,
            login,
        )

    def listar_regencia_por_ano_turma(
        self,
        ano_turma: int,
    ) -> list[dict]:
        """Retorna componentes de regência por ano de turma (EP-2)."""
        return self._repo.listar_regencia_por_ano_turma(ano_turma)

    def turma_possui_componente_pap(
        self,
        codigo_turma: str,
        login: str,
    ) -> bool:
        """Verifica presença de componente PAP na turma (EP-3)."""
        return self._repo.turma_possui_componente_pap(codigo_turma, login)

    def listar_por_ue_modalidade_ano_e_anos_escolares(
        self,
        modalidade: int,
        ano_letivo: int,
        anos_escolares: list[str],
    ) -> list[dict]:
        """Retorna componentes da grade por UE, modalidade e séries (EP-4)."""
        return self._repo.listar_por_ue_modalidade_ano_e_anos_escolares(
            modalidade, ano_letivo, anos_escolares
        )

    def listar_turma_programa_por_ue_modalidade_ano(
        self,
        modalidade: int,
        ano_letivo: int,
    ) -> list[dict]:
        """Retorna componentes de turmas programa (EP-5)."""
        return self._repo.listar_turma_programa_por_ue_modalidade_ano(
            modalidade, ano_letivo
        )

    def listar_por_ue_e_turmas(
        self,
        turmas: list[str],
    ) -> list[dict]:
        """Retorna componentes simplificados por lista de turmas (EP-6)."""
        return self._repo.listar_por_ue_e_turmas(turmas)

    def listar_por_lista_turmas(
        self,
        codigos_turmas: list[str],
    ) -> list[dict]:
        """Retorna componentes de múltiplas turmas para planejamento (EP-7)."""
        return self._repo.listar_por_lista_turmas(
            codigos_turmas
        )

    def listar_turmas_brutos(
        self,
        codigos_turmas: list[str],
    ) -> list[dict]:
        """Retorna componentes sem pós-processamento (EP-8)."""
        return self._repo.listar_turmas_brutos(codigos_turmas)

    def listar_catalogo(self) -> list[dict]:
        """Retorna catálogo completo de componentes (EP-9)."""
        return self._repo.listar_catalogo()

    def listar_vigencia_componentes(
        self,
        ue_codigo: str,
        ano_letivo: int,
        componentes_curriculares: list[str],
        semestre: int | None,
    ) -> list[dict]:
        """Retorna vigência de componentes por turma e UE (EP-10)."""
        return self._repo.listar_vigencia_componentes(
            ue_codigo, ano_letivo, componentes_curriculares, semestre
        )

    def listar_grade_curricular(
        self,
        ano_letivo: int,
    ) -> list[dict]:
        """Retorna grade curricular completa por ano letivo (EP-11)."""
        return self._repo.listar_grade_curricular(ano_letivo)

    def listar_componentes_sem_atribuicao(
        self,
        codigo_turma: str,
    ) -> list[str]:
        """Retorna componentes sem professor atribuído (EP-12)."""
        return self._repo.listar_componentes_sem_atribuicao(
            codigo_turma
        )

    def listar_agrupamentos_correlacionados(
        self,
        codigo_componente: int,
        data_base: date | None,
    ) -> list[dict]:
        """Retorna agrupamentos correlacionados de território do saber (EP-13)."""
        return self._repo.listar_agrupamentos_correlacionados(
            codigo_componente, data_base
        )

    def listar_agrupamentos_correlacionados_lote(
        self,
        codigos: list[int],
        data_base: date | None,
    ) -> list[dict]:
        """Retorna agrupamentos correlacionados em lote (EP-14)."""
        return self._repo.listar_agrupamentos_correlacionados_lote(
            codigos, data_base
        )

    def listar_agrupamentos_territorio(
        self,
        ids: list[int],
    ) -> list[dict]:
        """Retorna agrupamentos de Território do Saber por IDs (EP-15)."""
        return self._repo.listar_agrupamentos_territorio(ids)
