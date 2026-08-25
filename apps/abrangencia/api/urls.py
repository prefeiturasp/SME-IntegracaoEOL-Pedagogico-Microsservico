"""Rotas da API do domínio de abrangência."""

from django.urls import path

from apps.abrangencia.api.views import CiclosEnsinoView

urlpatterns = [
    path(
        "ciclo-ensino",
        CiclosEnsinoView.as_view(),
        name="abrangencia-ciclo-ensino",
    ),
]
