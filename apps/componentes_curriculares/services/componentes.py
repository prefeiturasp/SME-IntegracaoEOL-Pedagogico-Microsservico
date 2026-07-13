"""Serviços do domínio Componentes Curriculares."""

import math
from datetime import date, datetime

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
        agrupamento: bool = False,
    ) -> list[dict]:
        """Retorna componentes do funcionário.

        Args:
            login: Login (RF) do funcionário.
            codigo_turma: Filtra pelos componentes da turma quando
                informado.
            planejamento: Quando True, substitui regência pelos filhos
                de planejamento.
            agrupamento: Quando True, aplica agrupamentos de território no
                repositório.

        Returns:
            Lista de componentes curriculares do funcionário.
        """
        if codigo_turma is None:
            dados = self._repo.listar_por_funcionario(login)
        elif planejamento:
            dados = self._repo.listar_planejamento_por_turma_funcionario(
                codigo_turma, login
            )
        else:
            dados = self._repo.listar_por_turma_funcionario(
                codigo_turma,
                login,
                incluir_territorios_outros_professores=False,
            )

        if agrupamento:
            for item in dados:
                item["exibir_componente_eol"] = False
        return dados

    def listar_regencia_por_ano_turma(
        self,
        ano_turma: int,
    ) -> list[dict]:
        """Retorna componentes de regência por ano de turma.

        Args:
            ano_turma: Ano de turma para filtro.

        Returns:
            Lista de componentes de regência.
        """
        return self._repo.listar_regencia_por_ano_turma(ano_turma)

    def turma_possui_componente_pap(
        self,
        codigo_turma: str,
        login: str,
    ) -> bool:
        """Verifica presença de componente PAP na turma.

        Args:
            codigo_turma: Código da turma.
            login: Login (RF) do funcionário.

        Returns:
            True se a turma possui componente PAP para o funcionário.
        """
        return self._repo.turma_possui_componente_pap(codigo_turma, login)

    def listar_por_ue_modalidade_ano_e_anos_escolares(
        self,
        ue_codigo: str,
        modalidade: int,
        ano_letivo: int,
        anos_escolares: list[str],
    ) -> list[dict]:
        """Retorna componentes da grade por UE, modalidade e séries.

        Args:
            ue_codigo: Código da unidade educacional.
            modalidade: Código da modalidade de ensino.
            ano_letivo: Ano letivo consultado.
            anos_escolares: Séries a serem filtradas.

        Returns:
            Lista de componentes da grade curricular.
        """
        return self._repo.listar_por_ue_modalidade_ano_e_anos_escolares(
            ue_codigo, modalidade, ano_letivo, anos_escolares
        )

    def listar_turma_programa_por_ue_modalidade_ano(
        self,
        ue_codigo: str,
        modalidade: int,
        ano_letivo: int,
    ) -> list[dict]:
        """Retorna componentes de turmas programa.

        Args:
            ue_codigo: Código da unidade educacional.
            modalidade: Código da modalidade de ensino.
            ano_letivo: Ano letivo consultado.

        Returns:
            Lista de componentes de turmas programa.
        """
        return self._repo.listar_turma_programa_por_ue_modalidade_ano(
            ue_codigo, modalidade, ano_letivo
        )

    def listar_turmas_componentes_por_ue_modalidade_ano(
        self,
        ue_codigo: str,
        modalidade: int,
        ano_letivo: int,
        codigo_turma: int | None = None,
        qtde_registros: int = 0,
        eh_professor: bool = False,
        codigo_rf: str | None = None,
        considera_historico: bool = False,
        periodo_escolar_inicio: datetime | None = None,
        anos_infantil_desconsiderar: list[str] | None = None,
    ) -> dict:
        """Retorna listagem paginada de componentes por turma.

        Args:
            ue_codigo: Código da unidade educacional.
            modalidade: Código da modalidade de ensino.
            ano_letivo: Ano letivo consultado.
            codigo_turma: Filtra por uma turma específica quando informado.
            qtde_registros: Tamanho da página usado no total de páginas.
            eh_professor: Restringe os componentes ao RF informado.
            codigo_rf: RF do professor usado no filtro e no território.
            considera_historico: Inclui turmas históricas (situação C/E).
            periodo_escolar_inicio: Início do período escolar para turmas
                extintas quando `considera_historico` é verdadeiro.
            anos_infantil_desconsiderar: Anos de turma removidos do retorno.

        Returns:
            Envelope com `items`, `total_registros` e `total_paginas`.
        """
        itens = self._repo.listar_turmas_componentes_por_ue_modalidade_ano(
            ue_codigo,
            modalidade,
            ano_letivo,
            codigo_turma=codigo_turma,
            eh_professor=eh_professor,
            codigo_rf=codigo_rf,
            considera_historico=considera_historico,
            periodo_escolar_inicio=periodo_escolar_inicio,
            anos_infantil_desconsiderar=anos_infantil_desconsiderar,
        )
        total_registros = len(itens)
        # A paginação só informa o total de páginas calculado a partir de `qtde_registros`.
        total_paginas = (
            math.ceil(total_registros / qtde_registros)
            if qtde_registros > 0
            else 0
        )
        return {
            "items": itens,
            "total_registros": total_registros,
            "total_paginas": total_paginas,
        }

    def listar_por_ue_e_turmas(
        self,
        ue_id: str,
        turmas: list[str],
    ) -> list[dict]:
        """Retorna componentes simplificados por lista de turmas.

        Args:
            ue_id: Código da unidade educacional.
            turmas: Códigos das turmas a consultar.

        Returns:
            Lista de componentes simplificados das turmas.
        """
        return self._repo.listar_por_ue_e_turmas(ue_id, turmas)

    def listar_por_lista_turmas(
        self,
        codigos_turmas: list[str],
        adicionar_componentes_planejamento: bool = True,
    ) -> list[dict]:
        """Retorna componentes de múltiplas turmas para planejamento.

        Args:
            codigos_turmas: Códigos das turmas consultadas.
            adicionar_componentes_planejamento: Quando True, expande
                regência com os componentes de planejamento.

        Returns:
            Lista de componentes das turmas informadas.
        """
        return self._repo.listar_por_lista_turmas(
            codigos_turmas,
            adicionar_componentes_planejamento=adicionar_componentes_planejamento,
        )

    def listar_turmas_brutos(
        self,
        codigos_turmas: list[str],
    ) -> list[dict]:
        """Retorna componentes sem pós-processamento.

        Args:
            codigos_turmas: Códigos das turmas a consultar.

        Returns:
            Lista de componentes sem normalização de dados.
        """
        return self._repo.listar_turmas_brutos(codigos_turmas)

    def listar_catalogo(self) -> list[dict]:
        """Retorna catálogo completo de componentes.

        Returns:
            Lista completa de componentes curriculares.
        """
        return self._repo.listar_catalogo()

    def listar_vigencia_componentes(
        self,
        ue_codigo: str,
        ano_letivo: int,
        componentes_curriculares: list[str],
        semestre: int | None,
    ) -> list[dict]:
        """Retorna vigência de componentes por turma e UE.

        Args:
            ue_codigo: Código da unidade educacional.
            ano_letivo: Ano letivo consultado.
            componentes_curriculares: Códigos dos componentes a consultar.
            semestre: Semestre letivo; None para todos os semestres.

        Returns:
            Lista de vigências de componentes por turma.
        """
        return self._repo.listar_vigencia_componentes(
            ue_codigo, ano_letivo, componentes_curriculares, semestre
        )

    def listar_grade_curricular(
        self,
        ano_letivo: int,
    ) -> list[dict]:
        """Retorna grade curricular completa por ano letivo.

        Args:
            ano_letivo: Ano letivo consultado.

        Returns:
            Linhas da grade curricular do ano letivo.
        """
        return self._repo.listar_grade_curricular(ano_letivo)

    def listar_componentes_sem_atribuicao(
        self,
        codigo_turma: str,
        data_base: date,
    ) -> list[str]:
        """Retorna códigos de componentes sem professor atribuído.

        Args:
            codigo_turma: Código da turma.
            data_base: Data usada para verificar a vigência da atribuição.

        Returns:
            Códigos dos componentes sem professor atribuído.
        """
        return self._repo.listar_componentes_sem_atribuicao(
            codigo_turma,
            data_base,
        )

    def listar_agrupamentos_correlacionados(
        self,
        codigo_componente: int,
        data_base: date | None,
    ) -> list[dict]:
        """Retorna agrupamentos correlacionados de território do saber.

        Args:
            codigo_componente: `cod_agrupamento` de origem da consulta.
            data_base: Data de referência; None para sem filtro de data.

        Returns:
            Lista de agrupamentos e componentes correlacionados à origem.
        """
        return self._repo.listar_agrupamentos_correlacionados(
            codigo_componente, data_base
        )

    def listar_agrupamentos_correlacionados_lote(
        self,
        codigos: list[int],
        data_base: date | None,
    ) -> list[dict]:
        """Retorna agrupamentos correlacionados em lote.

        Args:
            codigos: `cod_agrupamento` das origens consultadas.
            data_base: Data de referência; None para sem filtro de data.

        Returns:
            Lista de agrupamentos correlacionados sem duplicatas.
        """
        return self._repo.listar_agrupamentos_correlacionados_lote(
            codigos, data_base
        )

    def listar_agrupamentos_territorio(
        self,
        ids: list[int],
    ) -> list[dict]:
        """Retorna agrupamentos de Território do Saber por IDs.

        Args:
            ids: IDs dos agrupamentos a consultar.

        Returns:
            Lista de agrupamentos de Território do Saber.
        """
        return self._repo.listar_agrupamentos_territorio(ids)
