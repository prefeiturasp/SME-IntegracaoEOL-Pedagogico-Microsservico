"""View base do microsserviço pedagógico."""
from rest_framework.views import APIView


class BaseAPIView(APIView):
    """View base com configuração padrão de autenticação/permissão.

    Todas as views do projeto devem herdar desta classe.
    A permissão é gerenciada globalmente via REST_FRAMEWORK settings,
    portanto esta classe serve principalmente como ponto de extensão.
    """
