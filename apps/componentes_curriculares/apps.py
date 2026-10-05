"""Configuração do app de componentes curriculares."""

from django.apps import AppConfig


class ComponentesCurricularesConfig(AppConfig):
    """Configura o app de componentes curriculares."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.componentes_curriculares"
