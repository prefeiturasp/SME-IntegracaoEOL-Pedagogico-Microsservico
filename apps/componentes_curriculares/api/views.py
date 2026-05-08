"""Views do domínio Componentes Curriculares."""
from datetime import date

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.request import Request
from rest_framework.response import Response

from apps.componentes_curriculares.serializers import (
    ComponenteCurricularSerializer,
    ComponenteRegenciaSerializer,
    ComponenteSimplificadoSerializer,
    GradeCurricularSerializer,
    VigenciaComponenteSerializer,
)
from apps.componentes_curriculares.services import ComponentesService
from apps.core.views import BaseAPIView

_TAG = ["ComponentesCurriculares"]


class ComponentesPorFuncionarioView(BaseAPIView):
    """EP-1: Listar Componentes Curriculares por Funcionário."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "idPerfil",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Perfil do usuário (GUID)",
            ),
            OpenApiParameter(
                "codigoTurma",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Filtra componentes pela turma",
            ),
            OpenApiParameter(
                "agrupaComponenteCurricular",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                default=True,
                description="Agrupa componentes por pai",
            ),
            OpenApiParameter(
                "checaMotivoDisponibilizacao",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                default=True,
                description="Verifica motivo de disponibilização",
            ),
            OpenApiParameter(
                "consideraTurmaInfantil",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                default=True,
                description="Aplica regras de educação infantil",
            ),
            OpenApiParameter(
                "planejamento",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                default=False,
                description="Substitui regência pelos filhos de planejamento",
            ),
        ],
        responses={200: ComponenteCurricularSerializer(many=True)},
        description="Lista componentes curriculares do funcionário.",
        tags=_TAG,
        operation_id="EP1_componentes_funcionario",
    )
    def get(self, request: Request, login: str) -> Response:

        codigo_turma = request.query_params.get("codigoTurma")
        planejamento = (
            request.query_params.get("planejamento", "false").lower() == "true"
        )
        agrupamento = (
            request.query_params.get("agrupaComponenteCurricular", "false").lower() == "true"
        )
        service = ComponentesService()
        dados = service.listar_componentes_por_funcionario(
            login,
            codigo_turma=codigo_turma,
            planejamento=planejamento,
            agrupamento=agrupamento,
        )
        return Response(dados)


class ComponentesRegenciaView(BaseAPIView):
    """EP-2: Listar Componentes Curriculares de Regência por Ano de Turma."""

    @extend_schema(
        responses={200: ComponenteRegenciaSerializer(many=True)},
        description="Lista componentes de regência por ano de turma.",
        tags=_TAG,
        operation_id="EP2_componentes_regencia",
    )
    def get(self, _request: Request, ano_turma: int) -> Response:
        """Retorna componentes de regência por ano de turma."""
        service = ComponentesService()
        dados = service.listar_regencia_por_ano_turma(ano_turma)
        return Response(dados)


class ValidarPapView(BaseAPIView):
    """EP-3: Verificar Componente Curricular PAP em Turma."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "login",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=True,
                description="Login (RF) do funcionário",
            ),
            OpenApiParameter(
                "idPerfil",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Identificador do perfil",
            ),
        ],
        responses={200: None},
        description="Verifica se a turma possui componente PAP.",
        tags=_TAG,
        operation_id="EP3_validar_pap",
    )
    def get(self, request: Request, codigo_turma: str) -> Response:
        """Verifica presença do componente PAP na turma."""
        login = request.query_params.get("login", "")

        service = ComponentesService()
        resultado = service.turma_possui_componente_pap(
            codigo_turma, login
        )
        return Response(resultado)


class ComponentesPorUeAnosEscolaresView(BaseAPIView):
    """EP-4: Listar Componentes Curriculares por UE, Modalidade e Ano."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "anosEscolares",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                many=True,
                required=True,
                description="Lista de anos escolares",
            ),
        ],
        responses={200: ComponenteCurricularSerializer(many=True)},
        description="Lista componentes da grade por UE, modalidade e séries.",
        tags=_TAG,
        operation_id="EP4_componentes_ue_anos_escolares",
    )
    def get(
        self,
        request: Request,
        ue_id: str,
        modalidade: int,
        ano_letivo: int,
    ) -> Response:
        """Retorna componentes por UE, modalidade, ano letivo e séries."""
        anos_escolares: list[str] = request.query_params.getlist(
            "anosEscolares"
        )
        service = ComponentesService()
        dados = service.listar_por_ue_modalidade_ano_e_anos_escolares(
            ue_id, modalidade, ano_letivo, anos_escolares
        )
        return Response(dados)


class ComponentesTurmaProgramaView(BaseAPIView):
    """EP-5: Listar Componentes de Turmas Programa."""

    @extend_schema(
        responses={200: ComponenteCurricularSerializer(many=True)},
        description="Lista componentes de turmas programa.",
        tags=_TAG,
        operation_id="EP5_componentes_turma_programa",
    )
    def get(
        self,
        _request: Request,
        ue_id: str,
        modalidade: int,
        ano_letivo: int,
    ) -> Response:
        """Retorna componentes de turmas programa por UE, modalidade e ano."""
        service = ComponentesService()
        dados = service.listar_turma_programa_por_ue_modalidade_ano(
            ue_id, modalidade, ano_letivo
        )
        return Response(dados)


class ComponentesPorUeTurmasView(BaseAPIView):
    """EP-6: Listar Componentes por Lista de Turmas e UE."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "turmas",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                many=True,
                required=True,
                description="Lista de códigos de turmas",
            ),
        ],
        responses={200: ComponenteSimplificadoSerializer(many=True)},
        description="Lista componentes simplificados por UE e turmas.",
        tags=_TAG,
        operation_id="EP6_componentes_ue_turmas",
    )
    def get(self, request: Request, ue_id: str) -> Response:

        turmas: list[str] = request.query_params.getlist("turmas")
        service = ComponentesService()
        dados = service.listar_por_ue_e_turmas(turmas)
        return Response(dados)


class ComponentesPorListaTurmasView(BaseAPIView):
    """EP-7: Listar Componentes para Planejamento por Lista de Turmas."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "codigoTurmas",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                many=True,
                required=True,
                description="Lista de códigos de turmas",
            ),
            OpenApiParameter(
                "adicionarComponentesPlanejamento",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                default=True,
                description="Inclui componentes de planejamento",
            ),
        ],
        responses={200: ComponenteCurricularSerializer(many=True)},
        description="Lista componentes de múltiplas turmas para planejamento.",
        tags=_TAG,
        operation_id="EP7_componentes_lista_turmas",
    )
    def get(self, request: Request) -> Response:

        codigos_turmas: list[str] = request.query_params.getlist(
            "codigoTurmas"
        )

        service = ComponentesService()
        dados = service.listar_por_lista_turmas(codigos_turmas)
        return Response(dados)


class ComponentesTurmasBrutosView(BaseAPIView):
    """EP-8: Listar Componentes de Turmas sem Pós-processamento."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "codigoTurmas",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                many=True,
                required=True,
                description="Lista de códigos de turmas",
            ),
        ],
        responses={200: ComponenteCurricularSerializer(many=True)},
        description="Lista componentes de turmas sem pós-processamento.",
        tags=_TAG,
        operation_id="EP8_componentes_turmas_brutos",
    )
    def get(self, request: Request) -> Response:

        codigos: list[str] = request.query_params.getlist("codigoTurmas")
        service = ComponentesService()
        dados = service.listar_turmas_brutos(codigos)
        return Response(dados)


class ComponentesCatalogoView(BaseAPIView):
    """EP-9: Listar Catálogo de Componentes Curriculares."""

    @extend_schema(
        responses={200: ComponenteSimplificadoSerializer(many=True)},
        description="Lista todos os componentes curriculares.",
        tags=_TAG,
        operation_id="EP9_catalogo_componentes",
    )
    def get(self, _request: Request) -> Response:

        service = ComponentesService()
        dados = service.listar_catalogo()
        return Response(dados)


class VigenciaComponentesView(BaseAPIView):
    """EP-10: Obter Vigência de Componentes por Turma e UE."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "ueCodigo",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=True,
                description="Código da Unidade Educacional",
            ),
            OpenApiParameter(
                "anoLetivo",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                required=True,
                description="Ano letivo",
            ),
            OpenApiParameter(
                "componentesCurriculares",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                many=True,
                required=True,
                description="Lista de códigos dos componentes curriculares",
            ),
            OpenApiParameter(
                "semestre",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Semestre (1 ou 2)",
            ),
        ],
        responses={200: VigenciaComponenteSerializer(many=True)},
        description="Retorna vigência de componentes por turma e UE.",
        tags=_TAG,
        operation_id="EP10_vigencia_componentes",
    )
    def get(self, request: Request) -> Response:

        ue_codigo = request.query_params.get("ueCodigo", "")
        ano_letivo = int(request.query_params.get("anoLetivo", 0))
        componentes: list[str] = request.query_params.getlist(
            "componentesCurriculares"
        )
        semestre_raw = request.query_params.get("semestre")
        semestre: int | None = int(semestre_raw) if semestre_raw else None
        service = ComponentesService()
        dados = service.listar_vigencia_componentes(
            ue_codigo, ano_letivo, componentes, semestre
        )
        return Response(dados)


class GradeCurricularView(BaseAPIView):
    """EP-11: Listar Grade Curricular por Ano Letivo."""

    @extend_schema(
        responses={200: GradeCurricularSerializer(many=True)},
        description="Lista grade curricular completa por ano letivo.",
        tags=_TAG,
        operation_id="EP11_grade_curricular",
    )
    def get(self, _request: Request, ano_letivo: int) -> Response:

        service = ComponentesService()
        dados = service.listar_grade_curricular(ano_letivo)
        return Response(dados)


class ComponentesSemAtribuicaoView(BaseAPIView):
    """EP-12: Listar Componentes Sem Atribuição em uma Turma."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "dataBase",
                OpenApiTypes.DATE,
                OpenApiParameter.QUERY,
                required=True,
                description="Data de referência ISO 8601 (yyyy-MM-dd)",
            ),
        ],
        responses={200: ComponenteSimplificadoSerializer(many=True)},
        description="Lista componentes sem professor atribuído.",
        tags=_TAG,
        operation_id="EP12_componentes_sem_atribuicao",
    )
    def get(self, request: Request, codigo_turma: str) -> Response:

        service = ComponentesService()
        dados = service.listar_componentes_sem_atribuicao(
            codigo_turma
        )
        return Response(dados)


class AgrupamentosCorrelacionadosView(BaseAPIView):
    """EP-13: Obter Agrupamentos Correlacionados por Componente."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "dataBase",
                OpenApiTypes.DATE,
                OpenApiParameter.QUERY,
                description="Data de referência ISO 8601 (yyyy-MM-dd)",
            ),
        ],
        responses={200: ComponenteCurricularSerializer(many=True)},
        description="Retorna agrupamentos correlacionados por componente.",
        tags=_TAG,
        operation_id="EP13_agrupamentos_correlacionados",
    )
    def get(
        self,
        request: Request,
        codigo_componente: int,
    ) -> Response:

        data_base_raw = request.query_params.get("dataBase")
        data_base: date | None = None
        if data_base_raw:
            data_base = date.fromisoformat(data_base_raw)
        service = ComponentesService()
        dados = service.listar_agrupamentos_correlacionados(
            codigo_componente, data_base
        )
        return Response(dados)


class AgrupamentosCorrelacionadosLoteView(BaseAPIView):
    """EP-14: Obter Agrupamentos Correlacionados em Lote."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "dataBase",
                OpenApiTypes.DATE,
                OpenApiParameter.QUERY,
                description="Data de referência ISO 8601 (yyyy-MM-dd)",
            ),
        ],
        request={
            "application/json": {
                "type": "array",
                "items": {"type": "integer"},
            }
        },
        responses={200: ComponenteCurricularSerializer(many=True)},

        description="Retorna agrupamentos correlacionados em lote.",
        tags=_TAG,
        operation_id="EP14_agrupamentos_correlacionados_lote",
    )
    def post(self, request: Request) -> Response:

        codigos = request.data
        if not isinstance(codigos, list):
            return Response(
                {"detail": "O corpo deve ser uma lista de inteiros."},
                status=400,
            )
        data_base_raw = request.query_params.get("dataBase")
        data_base: date | None = None
        if data_base_raw:
            data_base = date.fromisoformat(data_base_raw)
        service = ComponentesService()
        dados = service.listar_agrupamentos_correlacionados_lote(
            codigos, data_base
        )
        return Response(dados)


class AgrupamentosTerritorioLoteView(BaseAPIView):
    """EP-15: Obter Agrupamentos de Território do Saber por IDs."""

    @extend_schema(
        request={
            "application/json": {
                "type": "array",
                "items": {"type": "integer"},
            }
        },
        responses={200: ComponenteCurricularSerializer(many=True)},

        description="Retorna agrupamentos de Território do Saber por IDs.",
        tags=_TAG,
        operation_id="EP15_agrupamentos_territorio",
    )
    def post(self, request: Request) -> Response:

        ids = request.data
        if not isinstance(ids, list):
            return Response(
                {"detail": "O corpo deve ser uma lista de inteiros."},
                status=400,
            )
        service = ComponentesService()
        dados = service.listar_agrupamentos_territorio(ids)
        return Response(dados)
