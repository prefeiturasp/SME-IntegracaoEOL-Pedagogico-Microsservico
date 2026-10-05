"""View base do microsserviço pedagógico."""

from rest_framework.views import APIView


class BaseAPIView(APIView):
    """Aplica autenticação por API Key às views do microsserviço."""
