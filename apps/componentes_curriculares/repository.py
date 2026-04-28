"""Repository de Componentes Curriculares."""
from datetime import date

from django.db.models import F

from apps.componentes_curriculares.models import (
    AgrupamentoAtribuicaoTerritorioSaber,
    ComponenteCurricular,
    ComponenteCurricularPAP,
    ComponenteCurricularPorTurma,
    ComponenteInicioTurma,
    GradeCurricularSerie,
    RegenciaComponenteCurricular,
)

_CAMPOS_COMPONENTE = (
    "codigo",
    "codigo_componente_territorio_saber",
    "codigo_componente_curricular_pai",
    "descricao",
    "regencia",
    "planejamento_regencia",
    "territorio_saber",
    "turma_codigo",
    "exibir_componente_eol",
    "professor",
)


def _componente_para_dict(row: dict) -> dict:
    """Adiciona campo codigosTerritoriosAgrupamento ausente no ORM."""
    return {**row, "codigosTerritoriosAgrupamento": []}


def _grade_para_componente(row: dict) -> dict:
    """Converte linha de GradeCurricularSerie para shape de ComponenteCurricular."""
    return {
        "codigo": row["codigo_componente_curricular"],
        "codigo_componente_territorio_saber": 0,
        "codigo_componente_curricular_pai": None,
        "descricao": row["descricao_componente_curricular"],
        "regencia": False,
        "planejamento_regencia": False,
        "territorio_saber": False,
        "turma_codigo": None,
        "exibir_componente_eol": True,
        "professor": None,
        "codigosTerritoriosAgrupamento": [],
    }


def _agrupamento_para_dict(
    agrupamento: AgrupamentoAtribuicaoTerritorioSaber,
) -> dict:
    """Formata AgrupamentoAtribuicaoTerritorioSaber para shape de resposta."""
    codigos = _parse_csv(agrupamento.cod_componentes_curriculares)
    primeiro = codigos[0] if codigos else 0
    ts = agrupamento.desc_territorio_saber or ""
    ep = agrupamento.desc_experiencia_pedagogica or ""
    descricao = f"{ts} - {ep}" if ep else ts
    return {
        "codigo": agrupamento.cod_agrupamento,
        "codigo_componente_territorio_saber": primeiro,
        "codigo_componente_curricular_pai": None,
        "descricao": descricao,
        "regencia": False,
        "planejamento_regencia": False,
        "territorio_saber": True,
        "turma_codigo": agrupamento.cod_turma,
        "exibir_componente_eol": True,
        "professor": agrupamento.rf_professor,
        "codigosTerritoriosAgrupamento": codigos,
    }


def _parse_csv(csv_str: str | None) -> list[int]:
    """Converte CSV de códigos de componentes para lista de inteiros."""
    if not csv_str:
        return []
    return [
        int(c.strip())
        for c in csv_str.split(",")
        if c.strip().isdigit()
    ]


class ComponentesRepository:
    """Queries ORM para componentes curriculares."""

    _DB = "default"

    def listar_por_turma_funcionario(
        self,
        codigo_turma: str,
        login: str,
    ) -> list[dict]:
        """Lista componentes por turma e funcionário (EP-1 com codigoTurma)."""
        rows = list(
            ComponenteCurricularPorTurma.objects.using(self._DB)
            .filter(turma_codigo=codigo_turma, professor=login)
            .values(*_CAMPOS_COMPONENTE)
        )
        return [_componente_para_dict(r) for r in rows]

    def listar_por_funcionario(
        self,
        login: str,
    ) -> list[dict]:
        """Lista todos os componentes do funcionário sem filtro de turma (EP-1)."""
        rows = list(
            ComponenteCurricularPorTurma.objects.using(self._DB)
            .filter(professor=login)
            .values(*_CAMPOS_COMPONENTE)
            .distinct()
        )
        return [_componente_para_dict(r) for r in rows]

    def listar_planejamento_por_turma_funcionario(
        self,
        codigo_turma: str,
        login: str,
    ) -> list[dict]:
        """Lista componentes de planejamento de regência por turma (EP-1 planejamento)."""
        rows = list(
            ComponenteCurricularPorTurma.objects.using(self._DB)
            .filter(
                turma_codigo=codigo_turma,
                professor=login,
                planejamento_regencia=True,
            )
            .values(*_CAMPOS_COMPONENTE)
        )
        return [_componente_para_dict(r) for r in rows]

    def listar_regencia_por_ano_turma(
        self,
        ano_turma: int,
    ) -> list[dict]:
        """Lista componentes de regência por ano de turma (EP-2)."""
        if ano_turma <= 0:
            codigos = list(
                RegenciaComponenteCurricular.objects.using(self._DB)
                .filter(ano__isnull=True)
                .values_list("id_componente_curricular", flat=True)
            )
        else:
            codigos = list(
                RegenciaComponenteCurricular.objects.using(self._DB)
                .filter(ano=ano_turma)
                .values_list("id_componente_curricular", flat=True)
            )
        componentes = ComponenteCurricular.objects.using(self._DB).filter(
            codigo__in=codigos
        ).values("codigo", "descricao")
        return [
            {
                "ano_turma": None,
                "ano_letivo": 0,
                "codigo": c["codigo"],
                "codigo_componente_territorio_saber": 0,
                "descricao": c["descricao"],
                "territorio_saber": False,
                "tipo_escola": None,
                "turno_turma": 0,
                "componente_planejamento_regencia": False,
                "turma_codigo": None,
                "professor": None,
                "inicio_atribuicao": None,
                "fim_atribuicao": None,
            }
            for c in componentes
        ]

    def turma_possui_componente_pap(
        self,
        codigo_turma: str,
        login: str,
    ) -> bool:
        """Verifica se a turma possui componente PAP para o funcionário (EP-3)."""
        codigos = list(
            ComponenteCurricularPorTurma.objects.using(self._DB)
            .filter(turma_codigo=codigo_turma, professor=login)
            .values_list("codigo", flat=True)
        )
        return ComponenteCurricularPAP.objects.using(self._DB).filter(
            id_componente_curricular__in=codigos
        ).exists()

    def listar_por_ue_modalidade_ano_e_anos_escolares(
        self,
        modalidade: int,
        ano_letivo: int,
        anos_escolares: list[str],
    ) -> list[dict]:
        """Lista componentes da grade por modalidade, ano e séries (EP-4)."""
        qs = GradeCurricularSerie.objects.using(self._DB).filter(
            modalidade=modalidade,
            ano_letivo=ano_letivo,
        )
        if anos_escolares:
            qs = qs.filter(codigo_ano_turma__in=anos_escolares)
        rows = list(
            qs.values(
                "codigo_componente_curricular",
                "descricao_componente_curricular",
            ).distinct()
        )
        return [_grade_para_componente(r) for r in rows]

    def listar_turma_programa_por_ue_modalidade_ano(
        self,
        modalidade: int,
        ano_letivo: int,
    ) -> list[dict]:
        """Lista componentes de turmas programa por modalidade e ano (EP-5)."""
        rows = list(
            GradeCurricularSerie.objects.using(self._DB)
            .filter(modalidade=modalidade, ano_letivo=ano_letivo)
            .values(
                "codigo_componente_curricular",
                "descricao_componente_curricular",
            )
            .distinct()
        )
        return [_grade_para_componente(r) for r in rows]

    def listar_por_ue_e_turmas(
        self,
        turmas: list[str],
    ) -> list[dict]:
        """Lista componentes simplificados por lista de turmas (EP-6)."""
        qs = ComponenteCurricularPorTurma.objects.using(self._DB).exclude(
            codigo=0
        )
        if turmas:
            qs = qs.filter(turma_codigo__in=turmas)
        return list(
            qs.values("codigo", "descricao")
            .distinct()
            .order_by("descricao")
        )

    def listar_por_lista_turmas(
        self,
        codigos_turmas: list[str],
    ) -> list[dict]:
        """Lista componentes de múltiplas turmas para planejamento (EP-7)."""
        rows = list(
            ComponenteCurricularPorTurma.objects.using(self._DB)
            .filter(turma_codigo__in=codigos_turmas)
            .values(*_CAMPOS_COMPONENTE)
            .distinct()
        )
        return [_componente_para_dict(r) for r in rows]

    def listar_turmas_brutos(
        self,
        codigos_turmas: list[str],
    ) -> list[dict]:
        """Lista componentes sem pós-processamento (EP-8)."""
        rows = list(
            ComponenteCurricularPorTurma.objects.using(self._DB)
            .filter(turma_codigo__in=codigos_turmas)
            .values(*_CAMPOS_COMPONENTE)
            .distinct()
        )
        return [_componente_para_dict(r) for r in rows]

    def listar_catalogo(self) -> list[dict]:
        """Lista o catálogo completo de componentes (EP-9)."""
        return list(
            ComponenteCurricular.objects.using(self._DB)
            .values("codigo", "descricao")
            .order_by("codigo")
        )

    def listar_vigencia_componentes(
        self,
        ue_codigo: str,
        ano_letivo: int,
        componentes_curriculares: list[str],
        semestre: int | None,
    ) -> list[dict]:
        """Lista vigência de componentes por turma e UE (EP-10)."""
        qs = ComponenteInicioTurma.objects.using(self._DB).filter(
            ue_codigo=ue_codigo,
            ano_letivo=ano_letivo,
            componente_codigo__in=componentes_curriculares,
        )
        if semestre is not None:
            qs = qs.filter(tipo_periodicidade=semestre)
        return list(
            qs.values(
                "componente_codigo",
                "componente_descricao",
                "turma_codigo",
                "data_inicio_turma",
            )
        )

    def listar_grade_curricular(
        self,
        ano_letivo: int,
    ) -> list[dict]:
        """Lista grade curricular completa por ano letivo (EP-11)."""
        return list(
            GradeCurricularSerie.objects.using(self._DB)
            .filter(ano_letivo=ano_letivo)
            .values(
                "codigo_componente_curricular",
                "descricao_componente_curricular",
                "codigo_ano_turma",
                "descricao_serie_ensino",
                "codigo_serie_ensino",
                "modalidade",
            )
        )

    def listar_componentes_sem_atribuicao(
        self,
        codigo_turma: str,
    ) -> list[str]:
        """Lista componentes sem professor atribuído na turma (EP-12)."""
        return list(
            ComponenteCurricularPorTurma.objects.using(self._DB)
            .filter(turma_codigo=codigo_turma, professor__isnull=True)
            .values_list("descricao", flat=True)
        )

    def listar_agrupamentos_correlacionados(
        self,
        codigo_componente: int,
        data_base: date | None,
    ) -> list[dict]:
        """Retorna agrupamentos correlacionados de território do saber (EP-13)."""
        origem = (
            AgrupamentoAtribuicaoTerritorioSaber.objects.using(self._DB)
            .filter(cod_agrupamento=codigo_componente)
            .order_by(
                F("dt_fim_atribuicao").asc(nulls_first=True),
                "-dt_inicio_atribuicao",
            )
            .first()
        )
        if origem is None:
            return []

        qs = AgrupamentoAtribuicaoTerritorioSaber.objects.using(
            self._DB
        ).filter(
            cod_turma=origem.cod_turma,
            cod_territorio_saber=origem.cod_territorio_saber,
        )
        if data_base is not None:
            qs = qs.filter(dt_inicio_atribuicao__date__lte=data_base)

        codigos_origem = set(_parse_csv(origem.cod_componentes_curriculares))
        resultado: list[dict] = []
        for ag in qs:
            codigos_ag = set(_parse_csv(ag.cod_componentes_curriculares))
            if codigos_ag and codigos_ag.issubset(codigos_origem):
                resultado.append(_agrupamento_para_dict(ag))
        return resultado

    def listar_agrupamentos_correlacionados_lote(
        self,
        codigos_agrupamentos: list[int],
        data_base: date | None,
    ) -> list[dict]:
        """Retorna agrupamentos correlacionados em lote (EP-14)."""
        resultado: list[dict] = []
        vistos: set[int] = set()
        for cod in codigos_agrupamentos:
            for item in self.listar_agrupamentos_correlacionados(
                cod, data_base
            ):
                ag_cod = item["codigo"]
                if ag_cod not in vistos:
                    vistos.add(ag_cod)
                    resultado.append(item)
        return resultado

    def listar_agrupamentos_territorio(
        self,
        codigos_agrupamentos: list[int],
    ) -> list[dict]:
        """Retorna agrupamentos de território do saber por IDs (EP-15)."""
        agrupamentos = (
            AgrupamentoAtribuicaoTerritorioSaber.objects.using(self._DB)
            .filter(cod_agrupamento__in=codigos_agrupamentos)
            .order_by(
                F("dt_fim_atribuicao").asc(nulls_first=True),
                "-dt_inicio_atribuicao",
            )
        )
        vistos: set[int] = set()
        resultado: list[dict] = []
        for ag in agrupamentos:
            if ag.cod_agrupamento not in vistos:
                vistos.add(ag.cod_agrupamento)
                resultado.append(_agrupamento_para_dict(ag))
        return resultado
