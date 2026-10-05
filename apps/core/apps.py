"""AppConfig do app core."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuração do app core."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"

    def ready(self) -> None:
        """Inicializa observabilidade e resiliência no boot do processo."""
        from sme_sidecar_sdk import runtime

        runtime.configure()
