"""Rotas principais do microsserviço pedagógico."""

from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from rest_framework.permissions import AllowAny

urlpatterns = [
    path(
        "pedagogico/api/v1/schema/",
        SpectacularAPIView.as_view(
            authentication_classes=[],
            permission_classes=[AllowAny],
        ),
        name="schema",
    ),
    path(
        "pedagogico/api/v1/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema",
            authentication_classes=[],
            permission_classes=[AllowAny],
        ),
        name="swagger-ui",
    ),
    path(
        "api/v1/pedagogico/componentes-curriculares/",
        include("apps.componentes_curriculares.api.urls"),
    ),
    path(
        "api/v1/pedagogico/turmas/",
        include("apps.turmas.api.urls"),
    ),
]
