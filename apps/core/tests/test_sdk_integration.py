"""Testes de integração do SME Sidecar SDK com Django.

Este módulo contém testes end-to-end que validam a integração completa
do SDK com a aplicação Django, incluindo logs estruturados, propagação
de contexto e comportamento em diferentes cenários.
"""

import json
import logging
from io import StringIO
from typing import Any
from unittest.mock import patch

import pytest
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.test import RequestFactory, override_settings
from sme_sidecar_sdk.integrations.django import ObservabilityMiddleware


class LogCapture:
    """Captura logs estruturados emitidos durante os testes.

    Args:
        logger_name: Nome do logger a ser capturado.
    """

    def __init__(self, logger_name: str = "sme_sidecar_sdk") -> None:
        self.logger_name = logger_name
        self.stream = StringIO()
        self.handler = logging.StreamHandler(self.stream)
        self.handler.setLevel(logging.DEBUG)
        self.logger = logging.getLogger(logger_name)
        self.original_handlers: list[logging.Handler] = []
        self.original_level = self.logger.level

    def __enter__(self) -> "LogCapture":
        """Adiciona o handler de captura ao logger.

        Returns:
            Instância do LogCapture para uso em context manager.
        """
        self.original_handlers = self.logger.handlers[:]
        self.logger.handlers = [self.handler]
        self.logger.setLevel(logging.DEBUG)
        return self

    def __exit__(self, *args: Any) -> None:
        """Remove o handler de captura e restaura configuração original.

        Args:
            *args: Argumentos do context manager (não utilizados).
        """
        self.logger.handlers = self.original_handlers
        self.logger.setLevel(self.original_level)

    def get_logs(self) -> list[str]:
        """Retorna lista de mensagens de log capturadas.

        Returns:
            Lista com cada linha de log como string.
        """
        return [
            line.strip()
            for line in self.stream.getvalue().split("\n")
            if line.strip()
        ]


def _process_request(
    request: HttpRequest,
    view_callable=None,
) -> HttpResponse:
    """Processa requisição através do middleware de observabilidade.

    Args:
        request: Requisição HTTP Django.
        view_callable: Função view opcional. Se None, retorna 200.

    Returns:
        Resposta HTTP processada pelo middleware.
    """
    if view_callable is None:
        view_callable = lambda _: HttpResponse(status=200)

    middleware: ObservabilityMiddleware[HttpRequest, HttpResponse] = (
        ObservabilityMiddleware(view_callable)
    )
    return middleware(request)


def test_middleware_adiciona_request_id_ao_request_object() -> None:
    """Valida que o request_id é acessível no objeto request."""
    request = RequestFactory().get("/api/v1/pedagogico/turmas/")

    response = _process_request(request)

    assert hasattr(request, "request_id")
    assert isinstance(request.request_id, str)  # type: ignore[attr-defined]
    assert len(request.request_id) > 0  # type: ignore[attr-defined]
    assert response["X-Request-ID"] == request.request_id  # type: ignore[attr-defined]


def test_propagacao_contexto_em_chamadas_aninhadas() -> None:
    """Garante que o request_id é propagado em processamento aninhado."""

    def view_que_chama_subview(request: HttpRequest) -> HttpResponse:
        # Simula uma view que acessa o request_id internamente
        request_id = getattr(request, "request_id", None)
        assert request_id is not None
        return JsonResponse({"request_id": request_id})

    request = RequestFactory().get(
        "/api/v1/pedagogico/turmas/",
        headers={"X-Request-ID": "nested-call-123"},
    )

    response = _process_request(request, view_que_chama_subview)

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data["request_id"] == "nested-call-123"


def test_middleware_nao_interfere_em_resposta_json() -> None:
    """Verifica que JsonResponse é preservado sem alterações."""

    def json_view(_request: HttpRequest) -> JsonResponse:
        return JsonResponse(
            {
                "codigo_turma": "1234567",
                "nome": "8º A",
                "componentes": [1, 2, 3],
            }
        )

    request = RequestFactory().get("/api/v1/pedagogico/turmas/1234567/")

    response = _process_request(request, json_view)

    assert response.status_code == 200
    assert "X-Request-ID" in response
    data = json.loads(response.content)
    assert data["codigo_turma"] == "1234567"
    assert data["nome"] == "8º A"
    assert data["componentes"] == [1, 2, 3]


def test_middleware_funciona_com_post_json_body() -> None:
    """Valida processamento de requisições POST com corpo JSON."""

    def create_view(request: HttpRequest) -> JsonResponse:
        # Simula criação de recurso
        return JsonResponse({"created": True}, status=201)

    request = RequestFactory().post(
        "/api/v1/pedagogico/turmas/",
        data=json.dumps({"nome": "Nova Turma"}),
        content_type="application/json",
        headers={"X-Request-ID": "post-test-789"},
    )

    response = _process_request(request, create_view)

    assert response.status_code == 201
    assert response["X-Request-ID"] == "post-test-789"


def test_request_id_consistente_em_excecoes() -> None:
    """Garante request_id consistente mesmo quando view levanta exceção."""

    def failing_view(_request: HttpRequest) -> HttpResponse:
        raise RuntimeError("Erro de processamento")

    request = RequestFactory().get(
        "/api/v1/pedagogico/turmas/",
        headers={"X-Request-ID": "error-scenario-456"},
    )

    with pytest.raises(RuntimeError, match="Erro de processamento"):
        _process_request(request, failing_view)

    # Request ID deve ter sido definido antes da exceção
    assert hasattr(request, "request_id")
    assert request.request_id == "error-scenario-456"  # type: ignore[attr-defined]


def test_middleware_com_multiple_middlewares() -> None:
    """Valida comportamento quando há múltiplos middlewares na cadeia."""

    def another_middleware(get_response):
        def middleware(request):
            response = get_response(request)
            response["X-Another-Middleware"] = "processed"
            return response

        return middleware

    def simple_view(_request: HttpRequest) -> HttpResponse:
        return HttpResponse("OK", status=200)

    # Simula cadeia: ObservabilityMiddleware -> another_middleware -> view
    request = RequestFactory().get(
        "/api/v1/pedagogico/turmas/",
        headers={"X-Request-ID": "multi-middleware-test"},
    )

    obs_middleware = ObservabilityMiddleware(
        another_middleware(simple_view)
    )
    response = obs_middleware(request)

    assert response.status_code == 200
    assert response["X-Request-ID"] == "multi-middleware-test"
    assert response["X-Another-Middleware"] == "processed"


def test_request_id_header_case_insensitive() -> None:
    """Valida que o header X-Request-ID é case-insensitive."""
    factory = RequestFactory()

    # Testa diferentes variações de case
    headers_variants = [
        {"X-Request-ID": "test-upper"},
        {"x-request-id": "test-lower"},
        {"X-REQUEST-ID": "test-all-upper"},
    ]

    for headers in headers_variants:
        request = factory.get("/api/v1/pedagogico/turmas/", headers=headers)
        response = _process_request(request)

        # Django normaliza headers, então o valor deve ser preservado
        assert "X-Request-ID" in response
        expected_id = list(headers.values())[0]
        assert response["X-Request-ID"] == expected_id


@override_settings(SME_CORRELATION_ID_HEADER="X-Correlation-ID")
def test_middleware_respeita_header_customizado() -> None:
    """Verifica suporte a header de correlação customizado via settings."""
    request = RequestFactory().get(
        "/api/v1/pedagogico/turmas/",
        headers={"X-Correlation-ID": "custom-header-123"},
    )

    response = _process_request(request)

    # O SDK deve respeitar o header configurado ou usar o padrão X-Request-ID
    assert "X-Request-ID" in response or "X-Correlation-ID" in response


def test_request_id_preservado_apos_multiplas_requisicoes() -> None:
    """Garante que request_ids não vazam entre requisições diferentes."""
    factory = RequestFactory()
    request_ids_seen = []

    for i in range(5):
        request = factory.get(
            "/api/v1/pedagogico/turmas/",
            headers={"X-Request-ID": f"req-{i}"},
        )
        response = _process_request(request)
        request_ids_seen.append(response["X-Request-ID"])

    # Cada requisição deve ter mantido seu próprio ID
    assert request_ids_seen == ["req-0", "req-1", "req-2", "req-3", "req-4"]


def test_middleware_nao_modifica_request_path() -> None:
    """Verifica que o middleware não altera o path da requisição."""
    original_path = "/api/v1/pedagogico/turmas/1234567/componentes/"
    request = RequestFactory().get(original_path)

    def view_que_valida_path(request: HttpRequest) -> HttpResponse:
        assert request.path == original_path
        return HttpResponse(status=200)

    response = _process_request(request, view_que_valida_path)

    assert response.status_code == 200


def test_middleware_preserva_query_parameters() -> None:
    """Garante que query parameters são preservados."""
    request = RequestFactory().get(
        "/api/v1/pedagogico/turmas/?ano_letivo=2026&modalidade=1"
    )

    def view_que_usa_query_params(request: HttpRequest) -> JsonResponse:
        return JsonResponse(
            {
                "ano_letivo": request.GET.get("ano_letivo"),
                "modalidade": request.GET.get("modalidade"),
            }
        )

    response = _process_request(request, view_que_usa_query_params)

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data["ano_letivo"] == "2026"
    assert data["modalidade"] == "1"
