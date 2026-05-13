"""Views do domínio Turmas."""

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.views import BaseAPIView
from apps.turmas.serializers import (
    TurmaDadosSerializer,
    TurmaHistoricaSerializer,
    TurmaItinerarioSerializer,
    TurmaListSerializer,
    TurmaSincronizacaoSerializer,
)
from apps.turmas.services import TurmasService

_TAG = ["Turmas"]


# ---------------------------------------------------------------------------
# POST turmas-regulares
# ---------------------------------------------------------------------------


class TurmasRegularesView(BaseAPIView):
    """Filtra turmas regulares (tipo_turma=1) dentro de uma lista de códigos."""

    @extend_schema(
        tags=_TAG,
        summary="Buscar turmas regulares por lista de códigos",
        request={"application/json": {"type": "array", "items": {"type": "integer"}}},
        responses={200: TurmaListSerializer(many=True)},
        operation_id="turmas_regulares",
    )
    def post(self, request: Request) -> Response:
        codigos = request.data if isinstance(request.data, list) else []
        dados = TurmasService().turmas_regulares(codigos)
        return Response(dados)


# ---------------------------------------------------------------------------
# POST turmas-programa
# ---------------------------------------------------------------------------


class TurmasProgramaView(BaseAPIView):
    """Filtra turmas programa (tipo_turma=3) dentro de uma lista de códigos."""

    @extend_schema(
        tags=_TAG,
        summary="Buscar turmas programa por lista de códigos",
        request={"application/json": {"type": "array", "items": {"type": "integer"}}},
        responses={200: TurmaListSerializer(many=True)},
        operation_id="turmas_programa",
    )
    def post(self, request: Request) -> Response:
        codigos = request.data if isinstance(request.data, list) else []
        dados = TurmasService().turmas_programa(codigos)
        return Response(dados)


# ---------------------------------------------------------------------------
# POST listar-turmas
# ---------------------------------------------------------------------------


class ListarTurmasView(BaseAPIView):
    """Retorna turmas pelos códigos fornecidos, sem filtro de tipo."""

    @extend_schema(
        tags=_TAG,
        summary="Listar turmas por lista de códigos",
        request={"application/json": {"type": "array", "items": {"type": "integer"}}},
        responses={200: TurmaListSerializer(many=True)},
        operation_id="listar_turmas",
    )
    def post(self, request: Request) -> Response:
        codigos = request.data if isinstance(request.data, list) else []
        dados = TurmasService().listar_turmas(codigos)
        return Response(dados)


# ---------------------------------------------------------------------------
# GET {codigoTurma}/dados
# ---------------------------------------------------------------------------


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
        dados = TurmasService().dados_turma(codigo_turma)
        if dados is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(dados)


# ---------------------------------------------------------------------------
# GET /api/ues/{ueCodigo}/turmas/{turmaCodigo}/sincronizacoes-institucionais
# ---------------------------------------------------------------------------


class TurmaSincronizacoesInstitucionaisView(BaseAPIView):
    """Retorna dados de sincronização institucional de uma turma por UE."""

    @extend_schema(
        tags=_TAG,
        summary="Sincronizações institucionais da turma",
        parameters=[
            OpenApiParameter("ue_codigo", str, OpenApiParameter.PATH),
            OpenApiParameter("turma_codigo", int, OpenApiParameter.PATH),
        ],
        responses={200: TurmaSincronizacaoSerializer, 404: dict},
        operation_id="turma_sincronizacoes_institucionais",
    )
    def get(
        self,
        _request: Request,
        ue_codigo: str,
        turma_codigo: int,
    ) -> Response:
        dados = TurmasService().sincronizacoes_institucionais(ue_codigo, turma_codigo)
        if dados is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(dados)


# ---------------------------------------------------------------------------
# GET ue/{ueCodigo}/sincronizacoes-institucionais/anosLetivos
# ---------------------------------------------------------------------------


class AnosLetivosUEView(BaseAPIView):
    """Retorna anos letivos distintos com turmas na UE (exclui tipo_turma=4)."""

    @extend_schema(
        tags=_TAG,
        summary="Anos letivos de sincronizações institucionais por UE",
        parameters=[
            OpenApiParameter("ue_codigo", str, OpenApiParameter.PATH),
        ],
        responses={200: {"type": "array", "items": {"type": "integer"}}},
        operation_id="anos_letivos_ue",
    )
    def get(self, _request: Request, ue_codigo: str) -> Response:
        anos = TurmasService().anos_letivos_por_ue(ue_codigo)
        return Response(anos)


# ---------------------------------------------------------------------------
# GET anos-letivos/{anoLetivo}/professor/{professorRf}/turmas-historicas-geral
# ---------------------------------------------------------------------------


class TurmasHistoricasProfessorView(BaseAPIView):
    """Retorna turmas históricas do professor via AtribuicaoComponente."""

    @extend_schema(
        tags=_TAG,
        summary="Turmas históricas do professor por ano letivo",
        parameters=[
            OpenApiParameter("ano_letivo", int, OpenApiParameter.PATH),
            OpenApiParameter("professor_rf", str, OpenApiParameter.PATH),
        ],
        responses={200: TurmaHistoricaSerializer(many=True), 404: dict},
        operation_id="turmas_historicas_professor",
    )
    def get(
        self,
        _request: Request,
        ano_letivo: int,
        professor_rf: str,
    ) -> Response:
        dados = TurmasService().turmas_historicas_professor(ano_letivo, professor_rf)
        if not dados:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(dados)


# ---------------------------------------------------------------------------
# GET itinerario/ensino-medio
# ---------------------------------------------------------------------------


class ItinerarioEnsinoMedioView(BaseAPIView):
    """Retorna os itinerários do Ensino Médio (fixture local)."""

    @extend_schema(
        tags=_TAG,
        summary="Itinerários do Ensino Médio",
        responses={200: TurmaItinerarioSerializer(many=True)},
        operation_id="itinerario_ensino_medio",
    )
    def get(self, _request: Request) -> Response:
        dados = TurmasService().itinerarios_ensino_medio()
        return Response(dados)
