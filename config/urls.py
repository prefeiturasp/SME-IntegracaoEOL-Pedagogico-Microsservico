"""URL configuration for the pedagogico microservice."""
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from rest_framework.permissions import AllowAny

urlpatterns = [
    # Documentação pública (sem autenticação)
    path(
        "api/schema/",
        SpectacularAPIView.as_view(
            authentication_classes=[],
            permission_classes=[AllowAny],
        ),
        name="schema",
    ),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema",
            authentication_classes=[],
            permission_classes=[AllowAny],
        ),
        name="swagger-ui",
    ),

    path(
        "api/v1/componentes-curriculares/",
        include("apps.componentes_curriculares.api.urls"),
    ),
    path("api/", include("apps.turmas.api.urls")),
]
