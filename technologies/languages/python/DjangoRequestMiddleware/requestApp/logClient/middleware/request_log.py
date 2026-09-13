import logging
import uuid
from typing import Callable, Mapping, MutableMapping, Optional

from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

from logClient.common import Log

Log.log("requestLog.log")

# Headers that must never appear in logs with their real values.
SENSITIVE_HEADERS = frozenset(
    {
        "authorization",
        "cookie",
        "set-cookie",
        "proxy-authorization",
        "x-api-key",
        "x-auth-token",
        "x-csrftoken",
        "x-csrf-token",
    }
)

REDACTED = "[REDACTED]"

# Reserved for a future explicit body-field allowlist. Bodies are omitted by default.
BODY_FIELD_ALLOWLIST: frozenset[str] = frozenset()


def redact_headers(headers: Mapping[str, str]) -> dict[str, str]:
    """Return a copy of headers with sensitive values replaced."""
    redacted: dict[str, str] = {}
    for name, value in headers.items():
        if name.lower() in SENSITIVE_HEADERS:
            redacted[name] = REDACTED
        else:
            redacted[name] = value
    return redacted


def _request_id(request: HttpRequest) -> str:
    existing = getattr(request, "request_id", None)
    if existing:
        return str(existing)

    header_id = request.headers.get("X-Request-Id") or request.META.get(
        "HTTP_X_REQUEST_ID"
    )
    if header_id:
        request.request_id = header_id
        return str(header_id)

    generated = uuid.uuid4().hex
    request.request_id = generated
    return generated


def build_safe_request_log(
    request: HttpRequest,
    *,
    status: Optional[int] = None,
    include_headers: bool = False,
) -> dict:
    """
    Safe default log shape: method, path, request id, and status when available.

    Does not include raw request bodies. Headers are omitted by default; when
    explicitly requested they are redacted via redact_headers().
    """
    data: MutableMapping[str, object] = {
        "method": request.method,
        "path": request.path,
        "request_id": _request_id(request),
    }
    if status is not None:
        data["status"] = status
    if include_headers:
        data["headers"] = redact_headers(dict(request.headers))
    # Raw request bodies are never logged by default.
    return dict(data)


def _log_request(request: HttpRequest, *, status: Optional[int] = None) -> None:
    logging.info(build_safe_request_log(request, status=status))


# A middleware can be written as a function
def simple_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        response = get_response(request)
        _log_request(request, status=response.status_code)
        return response

    return middleware


# MiddlewareMixin-style class (educational). Prefer RequestLoggingMiddleware below.
class RequestLoggingMixinMiddleware(MiddlewareMixin):
    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        _log_request(request, status=response.status_code)
        return response

    def process_exception(
        self, request: HttpRequest, exception: Exception
    ) -> Optional[HttpResponse]:
        # Log only sanitized request metadata and the exception type.
        # Exception messages and tracebacks may contain secrets (passwords,
        # tokens) and must not be written to application logs.
        # Return None so Django continues normal exception/500 handling.
        logging.error(
            {
                **build_safe_request_log(request),
                "event": "unhandled_exception",
                "exception_type": type(exception).__name__,
            }
        )
        return None


# Given MiddlewareMixin has been deprecated,
# let's write a middleware from scratch
class RequestLoggingMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        _log_request(request, status=response.status_code)
        return response
