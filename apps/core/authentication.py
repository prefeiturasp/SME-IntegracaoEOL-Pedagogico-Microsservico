"""Autenticação por API Key do microsserviço pedagógico."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.conf import settings
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import IsAuthenticated

if TYPE_CHECKING:
    from rest_framework.request import Request


class _ApiAuth:
    """Pseudo-usuário para requisições autenticadas via API Key."""

    is_authenticated = True
    is_active = True
    is_staff = False
    is_anonymous = False

    def __str__(self) -> str:
        """Retorna representação textual do usuário."""
        return "api-user"


class ApiKeyAuthentication(BaseAuthentication):
    """Autentica requisições via API Key no header configurado."""

    def authenticate(self, request: Request) -> tuple[_ApiAuth, None] | None:
        """Valida a API Key e retorna pseudo-user ou None (anônimo).

        Comportamento (RFC 7235):
        - Chave ausente → retorna None (usuário anônimo, deixa a permissão decidir).
        - Chave presente mas errada → levanta 401 AuthenticationFailed.
        - Chave correta → retorna (_ApiAuth(), None).
        """
        header_name = getattr(settings, "API_KEY_HEADER", "x-api-key")
        api_key = getattr(settings, "API_KEY", "")
        meta_key = "HTTP_" + header_name.upper().replace("-", "_")
        key_fornecida = request.META.get(meta_key)

        if key_fornecida is None:
            # Sem credencial — anônimo (AllowAny/IsAuthenticated decidem)
            return None
        if key_fornecida != api_key:
            raise exceptions.AuthenticationFailed("API Key inválida.")
        return (_ApiAuth(), None)

    def authenticate_header(self, request: Request) -> str:
        """Retorna o nome do header esperado."""
        return getattr(settings, "API_KEY_HEADER", "x-api-key")


# Alias mantido para retrocompatibilidade
ApiKeyPermission = IsAuthenticated
