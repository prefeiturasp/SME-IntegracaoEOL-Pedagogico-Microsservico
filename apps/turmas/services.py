"""Serviços do domínio Turmas."""

from collections.abc import Iterable, Mapping
from types import MappingProxyType
from typing import Any

from apps.componentes_curriculares.constants import MODALIDADE_EJA
from apps.turmas.regras import ciclo_eja
from apps.turmas.repository import TurmasRepository

_TURMA_NAO_CADASTRADA: Mapping[str, Any] = MappingProxyType(
    {
        "tipo_turma": 0,
        "data_inicio": None,
        "data_fim": None,
        "extinta": False,
        "ensino_especial": False,
        "serie_ensino": None,
    }
)


def _turma_abrangencia(linha: Mapping[str, Any]) -> dict[str, Any]:
    turma = linha["turma"] or _TURMA_NAO_CADASTRADA
    codigo_modalidade = linha["codigo_modalidade"] or 0
    etapa_eja = (
        ciclo_eja(turma["serie_ensino"])
        if codigo_modalidade == MODALIDADE_EJA
        else 0
    )
    return {
        "ano": linha["ano"],
        "ano_letivo": linha["ano_letivo"],
        "codigo": linha["codigo_turma"],
        "tipo_turma": turma["tipo_turma"],
        "modalidade": linha["modalidade"],
        "codigo_modalidade": codigo_modalidade,
        "nome_turma": linha["nome_turma"],
        "semestre": linha["semestre"],
        "duracao_turno": linha["duracao_turno"],
        "tipo_turno": linha["tipo_turno"],
        "data_fim": turma["data_fim"],
        "eh_historico": False,
        "ensino_especial": turma["ensino_especial"],
        "etapa_eja": etapa_eja,
        "serie_ensino": None,
        "data_inicio_turma": turma["data_inicio"],
        "extinta": turma["extinta"],
        "situacao": None,
        "ue_codigo": None,
    }


def _agrupar_por_dre_ue(
    linhas: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    dres: dict[str, dict[str, Any]] = {}
    ues: dict[str, dict[str, Any]] = {}
    for linha in linhas:
        dre = dres.get(linha["codigo_dre"])
        if dre is None:
            dre = dres[linha["codigo_dre"]] = {
                "codigo": linha["codigo_dre"],
                "nome": linha["dre"],
                "abreviacao": linha["dre_abreviacao"],
                "ues": [],
            }
        ue = ues.get(linha["codigo_escola"])
        if ue is None:
            ue = ues[linha["codigo_escola"]] = {
                "codigo": linha["codigo_escola"],
                "nome": linha["ue"],
                "codigo_tipo_escola": linha["codigo_tipo_escola"],
                "turmas": [],
            }
            dre["ues"].append(ue)
        ue["turmas"].append(_turma_abrangencia(linha))
    return {"dres": list(dres.values())}


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

    def estrutura_abrangencia(
        self, codigo_dre: str | None = None
    ) -> dict[str, Any]:
        """Retorna a estrutura institucional vigente da SME ou de uma DRE.

        Args:
            codigo_dre: Código da DRE; toda a SME quando ausente.

        Returns:
            Turmas agrupadas por DRE e UE.
        """
        linhas = self._repo.linhas_abrangencia_estrutura_vigente(
            codigo_dre=codigo_dre
        )
        return _agrupar_por_dre_ue(linhas)

    def estrutura_abrangencia_por_turmas(
        self, codigos_turma: list[int]
    ) -> dict[str, Any]:
        """Retorna a estrutura institucional vigente das turmas informadas.

        Args:
            codigos_turma: Códigos das turmas a consultar.

        Returns:
            Turmas agrupadas por DRE e UE; vazia quando nenhuma turma é
            informada.
        """
        if not codigos_turma:
            return _agrupar_por_dre_ue([])
        linhas = self._repo.linhas_abrangencia_estrutura_vigente(
            codigos_turma=codigos_turma
        )
        return _agrupar_por_dre_ue(linhas)

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
