"""Serviços do domínio Componentes Curriculares."""

from typing import Any


def __getattr__(name: str) -> Any:
    """Carrega exports públicos do pacote sob demanda."""
    if name == "ComponentesService":
        from apps.componentes_curriculares.services.componentes import (
            ComponentesService,
        )

        return ComponentesService
    if name == "ComponentesRepository":
        from apps.componentes_curriculares.repository import (
            ComponentesRepository,
        )

        return ComponentesRepository
    raise AttributeError(name)


__all__ = ["ComponentesRepository", "ComponentesService"]
