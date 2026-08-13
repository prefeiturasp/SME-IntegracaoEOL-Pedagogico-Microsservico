"""Testes da integração de observabilidade do SME Sidecar SDK."""

import json
from unittest.mock import MagicMock
from uuid import UUID

import pytest
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory
from sme_sidecar_sdk.integrations.django import ObservabilityMiddleware


def _process_request(
    request: HttpRequest,
    view_callable=None,
) -> HttpResponse:
    """Processa uma requisição com o middleware de observabilidade.

    Args:
        request: Requisição HTTP a ser processada.
        view_callable: Função view opcional. Se None, retorna 204.

    Returns:
        Resposta HTTP processada pelo middleware.
    """
    if view_callable is None:
        view_callable = lambda _: HttpResponse(status=204)

    middleware: ObservabilityMiddleware[HttpRequest, HttpResponse] = (
        ObservabilityMiddleware(view_callable)
    )
    return middleware(request)


def test_preserva_request_id_recebido() -> None:
    """Propaga para a resposta o identificador recebido do consumidor."""
    request = RequestFactory().get(
        "/api/v1/pedagogico/turmas/",
        headers={"X-Request-ID": "request-pedagogico-123"},
    )

    response = _process_request(request)

    assert response["X-Request-ID"] == "request-pedagogico-123"
    assert request.request_id == "request-pedagogico-123"  # type: ignore[attr-defined]


def test_gera_request_id_quando_header_nao_e_enviado() -> None:
    """Gera um UUID e o devolve no header de correlação da resposta."""
    request = RequestFactory().get("/api/v1/pedagogico/turmas/")

    response = _process_request(request)

    request_id = response["X-Request-ID"]
    assert UUID(request_id).version == 4
    assert request.request_id == request_id  # type: ignore[attr-defined]


def test_preserva_request_id_mesmo_com_request_id_invalido() -> None:
    """Preserva o request_id mesmo se não for um UUID válido."""
    request = RequestFactory().get(
        "/api/v1/pedagogico/turmas/",
        headers={"X-Request-ID": "not-a-uuid-123"},
    )

    response = _process_request(request)

    assert response["X-Request-ID"] == "not-a-uuid-123"
    assert request.request_id == "not-a-uuid-123"  # type: ignore[attr-defined]


def test_propaga_request_id_em_diferentes_metodos_http() -> None:
    """Valida propagação do request_id em POST, PUT, PATCH e DELETE."""
    factory = RequestFactory()
    request_id = "test-request-id-456"
    headers = {"X-Request-ID": request_id}

    for method in ["post", "put", "patch", "delete"]:
        request_func = getattr(factory, method)
        request = request_func(
            "/api/v1/pedagogico/turmas/", headers=headers, data={}
        )

        response = _process_request(request)

        assert response["X-Request-ID"] == request_id
        assert request.request_id == request_id  # type: ignore[attr-defined]


def test_propaga_request_id_quando_view_levanta_excecao() -> None:
    """Garante que o request_id é preservado mesmo quando há erro."""

    def view_with_error(_request: HttpRequest) -> HttpResponse:
        raise ValueError("Erro intencional no processamento")

    request = RequestFactory().get(
        "/api/v1/pedagogico/turmas/",
        headers={"X-Request-ID": "error-test-123"},
    )

    # O middleware deve propagar a exceção, mas preservar o request_id
    with pytest.raises(ValueError, match="Erro intencional"):
        _process_request(request, view_with_error)

    # Verifica que o request foi anotado com request_id antes da exceção
    assert request.request_id == "error-test-123"  # type: ignore[attr-defined]


def test_middleware_com_diferentes_status_codes() -> None:
    """Valida que o middleware funciona com vários status codes."""
    factory = RequestFactory()
    test_cases = [
        (200, "OK"),
        (201, "Created"),
        (204, "No Content"),
        (400, "Bad Request"),
        (404, "Not Found"),
        (500, "Internal Server Error"),
    ]

    for status_code, _ in test_cases:
        request = factory.get(
            "/api/v1/pedagogico/turmas/",
            headers={"X-Request-ID": f"test-{status_code}"},
        )

        def view_with_status(
            _request: HttpRequest, code: int = status_code
        ) -> HttpResponse:
            return HttpResponse(status=code)

        response = _process_request(request, view_with_status)

        assert response.status_code == status_code
        assert response["X-Request-ID"] == f"test-{status_code}"


def test_request_id_vazio_gera_novo_uuid() -> None:
    """Gera novo UUID quando o header X-Request-ID está vazio."""
    request = RequestFactory().get(
        "/api/v1/pedagogico/turmas/",
        headers={"X-Request-ID": ""},
    )

    response = _process_request(request)

    request_id = response["X-Request-ID"]
    assert request_id != ""
    assert UUID(request_id).version == 4


def test_middleware_preserva_headers_da_resposta() -> None:
    """Verifica que outros headers da view são preservados."""

    def view_with_custom_headers(_request: HttpRequest) -> HttpResponse:
        response = HttpResponse(status=200)
        response["X-Custom-Header"] = "custom-value"
        response["Content-Type"] = "application/json"
        return response

    request = RequestFactory().get("/api/v1/pedagogico/turmas/")

    response = _process_request(request, view_with_custom_headers)

    assert response["X-Custom-Header"] == "custom-value"
    assert response["Content-Type"] == "application/json"
    assert "X-Request-ID" in response


def test_request_id_unico_para_cada_requisicao() -> None:
    """Garante que cada requisição sem header recebe um UUID único."""
    factory = RequestFactory()
    request_ids = set()

    for _ in range(10):
        request = factory.get("/api/v1/pedagogico/turmas/")
        response = _process_request(request)
        request_ids.add(response["X-Request-ID"])

    # Todos os 10 request IDs devem ser únicos
    assert len(request_ids) == 10
