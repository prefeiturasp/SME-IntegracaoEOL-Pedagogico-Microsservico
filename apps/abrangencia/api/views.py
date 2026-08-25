"""Views do domínio de abrangência."""

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.request import Request
from rest_framework.response import Response

from apps.abrangencia.serializers import CicloEnsinoSerializer
from apps.abrangencia.services import AbrangenciaService
from apps.core.views import BaseAPIView

_TAG = ["Abrangencia"]


class CiclosEnsinoView(BaseAPIView):
    """Lista os ciclos de ensino."""

    @extend_schema(
        responses={200: CicloEnsinoSerializer(many=True)},
        description="Lista o catálogo completo de ciclos de ensino.",
        tags=_TAG,
        operation_id="abrangencia_listar_ciclos_ensino",
        examples=[
            OpenApiExample(
                "Resposta",
                value=[
                    {
                        "codigoModalidadeEnsino": 5,
                        "codigoEtapaEnsino": 4,
                        "codigo": 3,
                        "descricao": "Alfabetização",
                        "dtAtualizacao": "2026-08-20T10:30:15.123",
                    }
                ],
                response_only=True,
                status_codes=["200"],
            )
        ],
    )
    def get(self, _request: Request) -> Response:
        """Lista os ciclos de ensino.

        Args:
            _request: Requisição HTTP (não utilizada).

        Returns:
            Catálogo de ciclos de ensino.
        """
        ciclos = AbrangenciaService().listar_ciclos_ensino()
        return Response(CicloEnsinoSerializer(ciclos, many=True).data)
