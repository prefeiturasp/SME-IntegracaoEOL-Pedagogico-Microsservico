"""Configuração do app Turmas."""

from django.apps import AppConfig


class TurmasConfig(AppConfig):
    """App do domínio Turmas — leitura do PEDAGOGICO_DB."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.turmas"
    label = "turmas"
