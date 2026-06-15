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
        codigos = request.data if isinstance(request.data, list) else []
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
        codigos = request.data if isinstance(request.data, list) else []
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
        codigos = request.data if isinstance(request.data, list) else []
        dados = TurmasService().listar_turmas(codigos)
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
        responses={200: TurmaSincronizacaoSerializer, 404: dict},
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
            ue_codigo: Código da unidade educacional.
            turma_codigo: Código da turma consultada.

        Returns:
            Dados de sincronização institucional da turma, ou ausência de
            conteúdo quando não encontrada.
        """
        dados = TurmasService().sincronizacoes_institucionais(
            ue_codigo, turma_codigo
        )
        if dados is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(dados)


class AnosLetivosUEView(BaseAPIView):
    """Lista anos letivos com turmas na UE."""

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
        """Lista os anos letivos com turmas na UE.

        Args:
            ue_codigo: Código da unidade educacional.

        Returns:
            Anos letivos com turmas na UE.
        """
        anos = TurmasService().anos_letivos_por_ue(ue_codigo)
        return Response(anos)


class TurmasHistoricasProfessorView(BaseAPIView):
    """Retorna turmas históricas do professor."""

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
        """Lista as turmas históricas do professor no ano letivo.

        Args:
            ano_letivo: Ano letivo consultado.
            professor_rf: Registro funcional do professor.

        Returns:
            Turmas históricas do professor, ou ausência de conteúdo quando não
            há turmas.
        """
        dados = TurmasService().turmas_historicas_professor(
            ano_letivo, professor_rf
        )
        if not dados:
            return Response(status=status.HTTP_404_NOT_FOUND)
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
