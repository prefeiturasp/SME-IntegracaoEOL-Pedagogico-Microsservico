"""Configuração do app de turmas."""

from django.apps import AppConfig


class TurmasConfig(AppConfig):
    """Configura o app de turmas."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.turmas"
    label = "turmas"
