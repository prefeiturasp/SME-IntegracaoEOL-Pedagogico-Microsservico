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
    """Lista componentes curriculares do funcionário."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "id_perfil",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Perfil do usuário (GUID)",
            ),
            OpenApiParameter(
                "codigo_turma",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Filtra componentes pela turma",
            ),
            OpenApiParameter(
                "agrupa_componente_curricular",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                default=True,
                description="Agrupa componentes por pai",
            ),
            OpenApiParameter(
                "checa_motivo_disponibilizacao",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                default=True,
                description="Verifica motivo de disponibilização",
            ),
            OpenApiParameter(
                "considera_turma_infantil",
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
        operation_id="componentes_funcionario",
    )
    def get(self, request: Request, login: str) -> Response:
        """Lista componentes curriculares do funcionário.

        Args:
            request: Requisição HTTP.
            login: Login (RF) do funcionário.

        Returns:
            Resposta com componentes curriculares do funcionário.
        """
        codigo_turma = request.query_params.get(
            "codigo_turma", request.query_params.get("codigoTurma")
        )
        planejamento = (
            request.query_params.get("planejamento", "false").lower() == "true"
        )
        agrupamento = (
            request.query_params.get(
                "agrupa_componente_curricular",
                request.query_params.get(
                    "agrupaComponenteCurricular", "false"
                ),
            ).lower()
            == "true"
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
    """Lista componentes curriculares de regência por ano de turma."""

    @extend_schema(
        responses={200: ComponenteRegenciaSerializer(many=True)},
        description="Lista componentes de regência por ano de turma.",
        tags=_TAG,
        operation_id="componentes_regencia",
    )
    def get(self, _request: Request, ano_turma: int) -> Response:
        """Lista componentes curriculares de regência.

        Args:
            _request: Requisição HTTP.
            ano_turma: Ano escolar da turma.

        Returns:
            Resposta com componentes de regência.
        """
        service = ComponentesService()
        dados = service.listar_regencia_por_ano_turma(ano_turma)
        return Response(dados)


class ValidarPapView(BaseAPIView):
    """Verifica se a turma possui componente curricular PAP."""

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
                "id_perfil",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Identificador do perfil",
            ),
        ],
        responses={200: None},
        description="Verifica se a turma possui componente PAP.",
        tags=_TAG,
        operation_id="validar_pap",
    )
    def get(self, request: Request, codigo_turma: str) -> Response:
        """Verifica se a turma possui componente PAP.

        Args:
            request: Requisição HTTP.
            codigo_turma: Código da turma.

        Returns:
            Resposta booleana indicando presença de componente PAP.
        """
        login = request.query_params.get("login", "")

        service = ComponentesService()
        resultado = service.turma_possui_componente_pap(codigo_turma, login)
        return Response(resultado)


class ComponentesPorUeAnosEscolaresView(BaseAPIView):
    """Lista componentes curriculares por UE, modalidade e anos escolares."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "anos_escolares",
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
        operation_id="componentes_ue_anos_escolares",
    )
    def get(
        self,
        request: Request,
        ue_id: str,
        modalidade: int,
        ano_letivo: int,
    ) -> Response:
        """Lista componentes por UE, modalidade e anos escolares.

        Args:
            request: Requisição HTTP.
            ue_id: Código da unidade educacional.
            modalidade: Código da modalidade.
            ano_letivo: Ano letivo consultado.

        Returns:
            Resposta com componentes curriculares encontrados.
        """
        anos_escolares: list[str] = request.query_params.getlist(
            "anos_escolares"
        ) or request.query_params.getlist("anosEscolares")
        service = ComponentesService()
        dados = service.listar_por_ue_modalidade_ano_e_anos_escolares(
            ue_id, modalidade, ano_letivo, anos_escolares
        )
        return Response(dados)


class ComponentesTurmaProgramaView(BaseAPIView):
    """Lista componentes curriculares de turmas programa."""

    @extend_schema(
        responses={200: ComponenteCurricularSerializer(many=True)},
        description="Lista componentes de turmas programa.",
        tags=_TAG,
        operation_id="componentes_turma_programa",
    )
    def get(
        self,
        _request: Request,
        ue_id: str,
        modalidade: int,
        ano_letivo: int,
    ) -> Response:
        """Lista componentes de turmas programa.

        Args:
            _request: Requisição HTTP.
            ue_id: Código da unidade educacional.
            modalidade: Código da modalidade.
            ano_letivo: Ano letivo consultado.

        Returns:
            Resposta com componentes de turmas programa.
        """
        service = ComponentesService()
        dados = service.listar_turma_programa_por_ue_modalidade_ano(
            ue_id, modalidade, ano_letivo
        )
        return Response(dados)


class ComponentesPorUeTurmasView(BaseAPIView):
    """Lista componentes curriculares por UE e turmas."""

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
        operation_id="componentes_ue_turmas",
    )
    def get(self, request: Request, ue_id: str) -> Response:
        """Lista componentes simplificados por UE e turmas.

        Args:
            request: Requisição HTTP.
            ue_id: Código da unidade educacional.

        Returns:
            Resposta com componentes simplificados.
        """
        turmas: list[str] = request.query_params.getlist("turmas")
        service = ComponentesService()
        dados = service.listar_por_ue_e_turmas(ue_id, turmas)
        return Response(dados)


class ComponentesPorListaTurmasView(BaseAPIView):
    """Lista componentes curriculares para planejamento por lista de turmas."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "codigo_turmas",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                many=True,
                required=True,
                description="Lista de códigos de turmas",
            ),
            OpenApiParameter(
                "adicionar_componentes_planejamento",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                default=True,
                description="Inclui componentes de planejamento",
            ),
        ],
        responses={200: ComponenteCurricularSerializer(many=True)},
        description="Lista componentes de múltiplas turmas para planejamento.",
        tags=_TAG,
        operation_id="componentes_lista_turmas",
    )
    def get(self, request: Request) -> Response:
        """Lista componentes para planejamento por lista de turmas.

        Args:
            request: Requisição HTTP.

        Returns:
            Resposta com componentes das turmas informadas.
        """
        codigos_turmas: list[str] = request.query_params.getlist(
            "codigo_turmas"
        ) or request.query_params.getlist("codigoTurmas")

        service = ComponentesService()
        adicionar_componentes_planejamento = (
            request.query_params.get(
                "adicionar_componentes_planejamento",
                request.query_params.get(
                    "adicionarComponentesPlanejamento", "true"
                ),
            ).lower()
            == "true"
        )
        dados = service.listar_por_lista_turmas(
            codigos_turmas,
            adicionar_componentes_planejamento=adicionar_componentes_planejamento,
        )
        return Response(dados)


class ComponentesTurmasBrutosView(BaseAPIView):
    """Lista componentes curriculares sem pós-processamento."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "codigo_turmas",
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
        operation_id="componentes_turmas_brutos",
    )
    def get(self, request: Request) -> Response:
        """Lista componentes de turmas sem pós-processamento.

        Args:
            request: Requisição HTTP.

        Returns:
            Resposta com componentes brutos das turmas.
        """
        codigos: list[str] = request.query_params.getlist(
            "codigo_turmas"
        ) or request.query_params.getlist("codigoTurmas")
        service = ComponentesService()
        dados = service.listar_turmas_brutos(codigos)
        return Response(dados)


class ComponentesCatalogoView(BaseAPIView):
    """Lista o catálogo de componentes curriculares."""

    @extend_schema(
        responses={200: ComponenteSimplificadoSerializer(many=True)},
        description="Lista todos os componentes curriculares.",
        tags=_TAG,
        operation_id="catalogo_componentes",
    )
    def get(self, _request: Request) -> Response:
        """Lista o catálogo completo de componentes.

        Args:
            _request: Requisição HTTP.

        Returns:
            Resposta com catálogo de componentes curriculares.
        """
        service = ComponentesService()
        dados = service.listar_catalogo()
        return Response(dados)


class VigenciaComponentesView(BaseAPIView):
    """Retorna vigência de componentes curriculares por turma e UE."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "ue_codigo",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=True,
                description="Código da Unidade Educacional",
            ),
            OpenApiParameter(
                "ano_letivo",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                required=True,
                description="Ano letivo",
            ),
            OpenApiParameter(
                "componentes_curriculares",
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
        operation_id="vigencia_componentes",
    )
    def get(self, request: Request) -> Response:
        """Lista vigência de componentes por turma e UE.

        Args:
            request: Requisição HTTP.

        Returns:
            Resposta com vigências de componentes.
        """
        ue_codigo = request.query_params.get(
            "ue_codigo", request.query_params.get("ueCodigo", "")
        )
        ano_letivo = int(
            request.query_params.get(
                "ano_letivo", request.query_params.get("anoLetivo", 0)
            )
        )
        componentes: list[str] = request.query_params.getlist(
            "componentes_curriculares"
        ) or request.query_params.getlist("componentesCurriculares")
        semestre_raw = request.query_params.get("semestre")
        semestre: int | None = int(semestre_raw) if semestre_raw else None
        service = ComponentesService()
        dados = service.listar_vigencia_componentes(
            ue_codigo, ano_letivo, componentes, semestre
        )
        return Response(dados)


class GradeCurricularView(BaseAPIView):
    """Lista a grade curricular por ano letivo."""

    @extend_schema(
        responses={200: GradeCurricularSerializer(many=True)},
        description="Lista grade curricular completa por ano letivo.",
        tags=_TAG,
        operation_id="grade_curricular",
    )
    def get(self, _request: Request, ano_letivo: int) -> Response:
        """Lista grade curricular por ano letivo.

        Args:
            _request: Requisição HTTP.
            ano_letivo: Ano letivo consultado.

        Returns:
            Resposta com grade curricular do ano letivo.
        """
        service = ComponentesService()
        dados = service.listar_grade_curricular(ano_letivo)
        return Response(dados)


class ComponentesSemAtribuicaoView(BaseAPIView):
    """Lista componentes sem atribuição em uma turma."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "data_base",
                OpenApiTypes.DATE,
                OpenApiParameter.QUERY,
                required=True,
                description="Data de referência ISO 8601 (yyyy-MM-dd)",
            ),
        ],
        responses={200: ComponenteSimplificadoSerializer(many=True)},
        description="Lista componentes sem professor atribuído.",
        tags=_TAG,
        operation_id="componentes_sem_atribuicao",
    )
    def get(self, request: Request, codigo_turma: str) -> Response:
        """Lista componentes sem professor atribuído.

        Args:
            request: Requisição HTTP.
            codigo_turma: Código da turma.

        Returns:
            Resposta com códigos dos componentes sem atribuição.

        Raises:
            ValueError: Quando `data_base` não estiver em formato ISO.
        """
        data_base = date.fromisoformat(request.query_params["data_base"])
        service = ComponentesService()
        dados = service.listar_componentes_sem_atribuicao(
            codigo_turma,
            data_base,
        )
        return Response(dados)


class AgrupamentosCorrelacionadosView(BaseAPIView):
    """Retorna agrupamentos correlacionados por componente."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "data_base",
                OpenApiTypes.DATE,
                OpenApiParameter.QUERY,
                description="Data de referência ISO 8601 (yyyy-MM-dd)",
            ),
        ],
        responses={200: ComponenteCurricularSerializer(many=True)},
        description="Retorna agrupamentos correlacionados por componente.",
        tags=_TAG,
        operation_id="agrupamentos_correlacionados",
    )
    def get(
        self,
        request: Request,
        codigo_componente: int,
    ) -> Response:
        """Retorna agrupamentos correlacionados por componente.

        Args:
            request: Requisição HTTP.
            codigo_componente: Código do agrupamento ou componente de origem.

        Returns:
            Resposta com agrupamentos correlacionados.

        Raises:
            ValueError: Quando `data_base` não estiver em formato ISO.
        """
        data_base_raw = request.query_params.get(
            "data_base", request.query_params.get("dataBase")
        )
        data_base: date | None = None
        if data_base_raw:
            data_base = date.fromisoformat(data_base_raw)
        service = ComponentesService()
        dados = service.listar_agrupamentos_correlacionados(
            codigo_componente, data_base
        )
        return Response(dados)


class AgrupamentosCorrelacionadosLoteView(BaseAPIView):
    """Retorna agrupamentos correlacionados em lote."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "data_base",
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
        operation_id="agrupamentos_correlacionados_lote",
    )
    def post(self, request: Request) -> Response:
        """Retorna agrupamentos correlacionados em lote.

        Args:
            request: Requisição HTTP com lista de códigos no corpo.

        Returns:
            Resposta com agrupamentos correlacionados sem duplicatas.

        Raises:
            ValueError: Quando `data_base` não estiver em formato ISO.
        """
        codigos = request.data
        if not isinstance(codigos, list):
            return Response(
                {"detail": "O corpo deve ser uma lista de inteiros."},
                status=400,
            )
        data_base_raw = request.query_params.get(
            "data_base", request.query_params.get("dataBase")
        )
        data_base: date | None = None
        if data_base_raw:
            data_base = date.fromisoformat(data_base_raw)
        service = ComponentesService()
        dados = service.listar_agrupamentos_correlacionados_lote(
            codigos, data_base
        )
        return Response(dados)


class AgrupamentosTerritorioLoteView(BaseAPIView):
    """Retorna agrupamentos de território do saber por IDs."""

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
        operation_id="agrupamentos_territorio",
    )
    def post(self, request: Request) -> Response:
        """Retorna agrupamentos de território do saber por IDs.

        Args:
            request: Requisição HTTP com lista de IDs no corpo.

        Returns:
            Resposta com agrupamentos de território do saber.
        """
        ids = request.data
        if not isinstance(ids, list):
            return Response(
                {"detail": "O corpo deve ser uma lista de inteiros."},
                status=400,
            )
        service = ComponentesService()
        dados = service.listar_agrupamentos_territorio(ids)
        return Response(dados)
