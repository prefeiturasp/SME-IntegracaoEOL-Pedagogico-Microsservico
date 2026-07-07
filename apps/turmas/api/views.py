"""Views do domínio Turmas."""

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.views import BaseAPIView
from apps.turmas.constants import MENSAGEM_COMPORTAMENTO_INESPERADO
from apps.turmas.serializers import (
    AnosLetivosVigenteQuerySerializer,
    TurmaDadosSerializer,
    TurmaHistoricaSerializer,
    TurmaItinerarioSerializer,
    TurmaListSerializer,
    TurmaSincronizacaoSerializer,
)
from apps.turmas.services import TurmasService

_TAG = ["Turma"]


class TurmasRegularesView(BaseAPIView):
    """Lista turmas regulares pelos códigos informados."""

    @extend_schema(
        tags=_TAG,
        summary="Buscar turmas regulares por lista de códigos",
        request={
            "application/json": {"type": "array", "items": {"type": "integer"}}
        },
        responses={200: TurmaListSerializer(many=True)},
        operation_id="turmas_regulares",
    )
    def post(self, request: Request) -> Response:
        """Retorna as turmas regulares dos códigos informados.

        Args:
            request: Requisição com a lista de códigos de turma no corpo.

        Returns:
            Turmas regulares correspondentes aos códigos.
        """
        codigos: list[int] = (
            request.data if isinstance(request.data, list) else []
        )
        dados = TurmasService().turmas_regulares(codigos)
        return Response(dados)


class TurmasProgramaView(BaseAPIView):
    """Lista turmas programa pelos códigos informados."""

    @extend_schema(
        tags=_TAG,
        summary="Buscar turmas programa por lista de códigos",
        request={
            "application/json": {"type": "array", "items": {"type": "integer"}}
        },
        responses={200: TurmaListSerializer(many=True)},
        operation_id="turmas_programa",
    )
    def post(self, request: Request) -> Response:
        """Retorna as turmas programa dos códigos informados.

        Args:
            request: Requisição com a lista de códigos de turma no corpo.

        Returns:
            Turmas programa correspondentes aos códigos.
        """
        codigos: list[int] = (
            request.data if isinstance(request.data, list) else []
        )
        dados = TurmasService().turmas_programa(codigos)
        return Response(dados)


class ListarTurmasView(BaseAPIView):
    """Lista turmas pelos códigos informados."""

    @extend_schema(
        tags=_TAG,
        summary="Listar turmas por lista de códigos",
        request={
            "application/json": {"type": "array", "items": {"type": "integer"}}
        },
        responses={200: TurmaListSerializer(many=True)},
        operation_id="listar_turmas",
    )
    def post(self, request: Request) -> Response:
        """Retorna as turmas dos códigos informados.

        Args:
            request: Requisição com a lista de códigos de turma no corpo.

        Returns:
            Turmas correspondentes aos códigos.
        """
        codigos: list[int] = (
            request.data if isinstance(request.data, list) else []
        )
        dados = TurmasService().listar_turmas(codigos)
        return Response(dados)


class TurmasRecorteFundMedioEjaView(BaseAPIView):
    """Lista turmas no recorte de etapa (Fund/Médio/EJA)."""

    @extend_schema(
        tags=_TAG,
        summary="Listar turmas no recorte de etapa (Fund/Médio/EJA)",
        request={
            "application/json": {"type": "array", "items": {"type": "integer"}}
        },
        responses={200: TurmaListSerializer(many=True)},
        operation_id="turmas_recorte_fund_medio_eja",
    )
    def post(self, request: Request) -> Response:
        """Retorna as turmas dos códigos que estão no recorte de etapa.

        Args:
            request: Requisição com a lista de códigos de turma no corpo.

        Returns:
            Turmas dos códigos cuja etapa está no recorte
            (EJA + Fundamental + Médio).
        """
        codigos = request.data if isinstance(request.data, list) else []
        dados = TurmasService().turmas_recorte_fund_medio_eja(codigos)
        return Response(dados)


def _query_int_list(request: Request, *nomes: str) -> list[int]:
    """Extrai inteiros repetíveis da query string, ignorando inválidos.

    Args:
        request: Requisição consultada.
        nomes: Nomes aceitos do parâmetro (snake_case e camelCase).

    Returns:
        Inteiros informados, sem entradas vazias ou não numéricas.
    """
    valores: list[int] = []
    for nome in nomes:
        for bruto in request.query_params.getlist(nome):
            texto = bruto.strip()
            if texto.lstrip("-").isdigit():
                valores.append(int(texto))
    return valores


def _query_int(request: Request, *nomes: str) -> int | None:
    """Lê um inteiro opcional da query string.

    Args:
        request: Requisição consultada.
        nomes: Nomes aceitos do parâmetro (snake_case e camelCase).

    Returns:
        Inteiro informado, ou ``None`` quando ausente/inválido.
    """
    for nome in nomes:
        bruto = request.query_params.get(nome)
        if bruto is not None and bruto.strip().lstrip("-").isdigit():
            return int(bruto.strip())
    return None


class TurmasRecortePorTipoView(BaseAPIView):
    """Filtra códigos de turma por tipo de turma, UE e semestre."""

    @extend_schema(
        tags=_TAG,
        summary="Recortar códigos de turma por tipo/UE/semestre",
        parameters=[
            OpenApiParameter(
                "tipos_turma",
                {"type": "array", "items": {"type": "integer"}},
                OpenApiParameter.QUERY,
                required=False,
                explode=True,
            ),
            OpenApiParameter(
                "ue_codigo", str, OpenApiParameter.QUERY, required=False
            ),
            OpenApiParameter(
                "semestre", int, OpenApiParameter.QUERY, required=False
            ),
        ],
        request={
            "application/json": {"type": "array", "items": {"type": "integer"}}
        },
        responses={200: {"type": "array", "items": {"type": "integer"}}},
        operation_id="turmas_recorte_por_tipo",
    )
    def post(self, request: Request) -> Response:
        """Retorna os códigos de turma que atendem ao recorte.

        Recebe a lista de códigos de turma no corpo e os filtros de tipo de turma,
        UE e semestre na query string.

        Args:
            request: Requisição com a lista de códigos no corpo e os
                filtros ``tipos_turma``/``ue_codigo``/``semestre`` na query.

        Returns:
            Subconjunto dos códigos informados que atende ao recorte.
        """
        codigos = request.data if isinstance(request.data, list) else []
        tipos_turma = _query_int_list(request, "tipos_turma", "tiposTurma")
        ue_codigo = request.query_params.get(
            "ue_codigo"
        ) or request.query_params.get("ueCodigo")
        semestre = _query_int(request, "semestre")
        dados = TurmasService().turmas_recorte_por_tipo(
            codigos, tipos_turma, ue_codigo, semestre
        )
        return Response(dados)


class TurmaDadosView(BaseAPIView):
    """Retorna dados canônicos de uma turma."""

    @extend_schema(
        tags=_TAG,
        summary="Dados cadastrais de uma turma",
        parameters=[
            OpenApiParameter("codigo_turma", int, OpenApiParameter.PATH),
        ],
        responses={200: TurmaDadosSerializer, 404: dict},
        operation_id="turma_dados",
    )
    def get(self, _request: Request, codigo_turma: int) -> Response:
        """Retorna os dados cadastrais de uma turma.

        Args:
            codigo_turma: Código da turma consultada.

        Returns:
            Dados cadastrais da turma, ou ausência de conteúdo quando não
            encontrada.
        """
        dados = TurmasService().dados_turma(codigo_turma)
        if dados is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(dados)


class TurmaSincronizacoesInstitucionaisView(BaseAPIView):
    """Retorna dados de sincronização institucional da turma."""

    @extend_schema(
        tags=_TAG,
        summary="Sincronizações institucionais da turma",
        parameters=[
            OpenApiParameter("ue_codigo", str, OpenApiParameter.PATH),
            OpenApiParameter("turma_codigo", int, OpenApiParameter.PATH),
        ],
        responses={200: TurmaSincronizacaoSerializer, 400: dict},
        operation_id="turma_sincronizacoes_institucionais",
    )
    def get(
        self,
        _request: Request,
        ue_codigo: str,
        turma_codigo: int,
    ) -> Response:
        """Retorna os dados de sincronização institucional da turma.

        Args:
            ue_codigo: Código da unidade educacional, obrigatório no
                contrato mas não usado na consulta.
            turma_codigo: Código da turma consultada.

        Returns:
            Dados de sincronização institucional da turma, ou erro 400
            quando a turma não é encontrada.
        """
        dados = TurmasService().sincronizacoes_institucionais(
            ue_codigo, turma_codigo
        )
        if dados is None:
            return Response(
                {"detail": MENSAGEM_COMPORTAMENTO_INESPERADO},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(dados)


class AnosLetivosUEView(BaseAPIView):
    """Lista códigos de turma da UE."""

    @extend_schema(
        tags=_TAG,
        summary="Códigos de turma da UE por anos letivos vigentes",
        parameters=[
            OpenApiParameter("ue_codigo", str, OpenApiParameter.PATH),
            OpenApiParameter(
                "anos_letivos_vigente",
                {"type": "array", "items": {"type": "integer"}},
                OpenApiParameter.QUERY,
                required=False,
                explode=True,
            ),
        ],
        responses={200: {"type": "array", "items": {"type": "integer"}}},
        operation_id="anos_letivos_ue",
    )
    def get(self, request: Request, ue_codigo: str) -> Response:
        """Lista os códigos de turma da UE.

        Args:
            request: Requisição com os anos letivos em anos_letivos_vigente.
            ue_codigo: Código da unidade educacional.

        Returns:
            Códigos de turma da UE: todos quando o filtro é ausente, filtrados
            pelos anos informados, ou lista vazia quando o filtro é informado
            sem ano válido.
        """
        serializer = AnosLetivosVigenteQuerySerializer(
            data=request.query_params
        )
        serializer.is_valid(raise_exception=True)
        informados = serializer.validated_data.get("anos_letivos_vigente")
        if not informados:
            codigos = TurmasService().codigos_turmas_por_ue(ue_codigo, None)
            return Response(codigos)
        anos_letivos = [ano for ano in informados if ano > 0]
        if not anos_letivos:
            return Response([])
        codigos = TurmasService().codigos_turmas_por_ue(
            ue_codigo, anos_letivos
        )
        return Response(codigos)


class TurmasHistoricasProfessorView(BaseAPIView):
    """Retorna turmas históricas do professor."""

    @extend_schema(
        tags=_TAG,
        summary="Turmas históricas do professor por ano letivo",
        parameters=[
            OpenApiParameter("ano_letivo", int, OpenApiParameter.PATH),
            OpenApiParameter("professor_rf", str, OpenApiParameter.PATH),
        ],
        responses={200: TurmaHistoricaSerializer(many=True)},
        operation_id="turmas_historicas_professor",
    )
    def get(
        self,
        _request: Request,
        ano_letivo: int,
        professor_rf: str,
    ) -> Response:
        """Lista as turmas históricas do professor no ano letivo.

        Args:
            ano_letivo: Ano letivo consultado.
            professor_rf: Registro funcional do professor.

        Returns:
            Turmas históricas do professor.
        """
        dados = TurmasService().turmas_historicas_professor(
            ano_letivo, professor_rf
        )
        return Response(dados)


class ItinerarioEnsinoMedioView(BaseAPIView):
    """Retorna itinerários do Ensino Médio."""

    @extend_schema(
        tags=_TAG,
        summary="Itinerários do Ensino Médio",
        responses={200: TurmaItinerarioSerializer(many=True)},
        operation_id="itinerario_ensino_medio",
    )
    def get(self, _request: Request) -> Response:
        """Lista os itinerários do Ensino Médio.

        Returns:
            Itinerários do Ensino Médio.
        """
        dados = TurmasService().itinerarios_ensino_medio()
        return Response(dados)
