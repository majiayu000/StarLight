import logging
from unittest.mock import MagicMock

from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings

from logClient.middleware.request_log import (
    REDACTED,
    RequestLoggingMiddleware,
    RequestLoggingMixinMiddleware,
    build_safe_request_log,
    redact_headers,
    simple_middleware,
)


SECRET_MARKER = "super-secret-token-should-never-appear"
COOKIE_MARKER = "sessionid=leak-me"
API_KEY_MARKER = "api-key-should-never-appear"
BODY_MARKER = "password=hunter2&otp=123456"


class HeaderRedactionTests(SimpleTestCase):
    def test_redact_headers_masks_sensitive_names(self):
        headers = {
            "Authorization": f"Bearer {SECRET_MARKER}",
            "Cookie": COOKIE_MARKER,
            "X-Api-Key": API_KEY_MARKER,
            "X-CSRFToken": "csrf-token-value",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        redacted = redact_headers(headers)

        self.assertEqual(redacted["Authorization"], REDACTED)
        self.assertEqual(redacted["Cookie"], REDACTED)
        self.assertEqual(redacted["X-Api-Key"], REDACTED)
        self.assertEqual(redacted["X-CSRFToken"], REDACTED)
        self.assertEqual(redacted["Accept"], "application/json")
        self.assertNotIn(SECRET_MARKER, str(redacted))
        self.assertNotIn(COOKIE_MARKER, str(redacted))
        self.assertNotIn(API_KEY_MARKER, str(redacted))


class SafeRequestLogShapeTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_default_shape_omits_headers_and_body(self):
        request = self.factory.post(
            "/login/",
            data=BODY_MARKER,
            content_type="application/x-www-form-urlencoded",
            HTTP_AUTHORIZATION=f"Bearer {SECRET_MARKER}",
            HTTP_COOKIE=COOKIE_MARKER,
            HTTP_X_API_KEY=API_KEY_MARKER,
            HTTP_X_REQUEST_ID="req-abc-123",
        )
        payload = build_safe_request_log(request, status=200)

        self.assertEqual(payload["method"], "POST")
        self.assertEqual(payload["path"], "/login/")
        self.assertEqual(payload["status"], 200)
        self.assertEqual(payload["request_id"], "req-abc-123")
        self.assertNotIn("headers", payload)
        self.assertNotIn("body", payload)
        serialized = str(payload)
        self.assertNotIn(SECRET_MARKER, serialized)
        self.assertNotIn(COOKIE_MARKER, serialized)
        self.assertNotIn(API_KEY_MARKER, serialized)
        self.assertNotIn(BODY_MARKER, serialized)
        self.assertNotIn("hunter2", serialized)

    def test_include_headers_still_redacts_secrets(self):
        request = self.factory.get(
            "/health/",
            HTTP_AUTHORIZATION=f"Bearer {SECRET_MARKER}",
            HTTP_COOKIE=COOKIE_MARKER,
        )
        payload = build_safe_request_log(request, include_headers=True)
        serialized = str(payload)
        self.assertIn(REDACTED, serialized)
        self.assertNotIn(SECRET_MARKER, serialized)
        self.assertNotIn(COOKIE_MARKER, serialized)


class _LogCapture(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(record.getMessage())


class MiddlewareLoggingTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.handler = _LogCapture()
        self.handler.setLevel(logging.INFO)
        root = logging.getLogger()
        root.addHandler(self.handler)
        self._prev_level = root.level
        root.setLevel(logging.INFO)

    def tearDown(self):
        root = logging.getLogger()
        root.removeHandler(self.handler)
        root.setLevel(self._prev_level)

    def _sensitive_request(self):
        return self.factory.post(
            "/api/auth/",
            data=BODY_MARKER,
            content_type="application/x-www-form-urlencoded",
            HTTP_AUTHORIZATION=f"Bearer {SECRET_MARKER}",
            HTTP_COOKIE=COOKIE_MARKER,
            HTTP_X_API_KEY=API_KEY_MARKER,
            HTTP_X_CSRFTOKEN="csrf-should-not-leak",
            HTTP_X_REQUEST_ID="rid-42",
        )

    def _assert_safe_logs(self):
        joined = "\n".join(self.handler.records)
        self.assertTrue(self.handler.records, "expected at least one log record")
        self.assertIn("/api/auth/", joined)
        self.assertIn("POST", joined)
        self.assertNotIn(SECRET_MARKER, joined)
        self.assertNotIn(COOKIE_MARKER, joined)
        self.assertNotIn(API_KEY_MARKER, joined)
        self.assertNotIn(BODY_MARKER, joined)
        self.assertNotIn("hunter2", joined)
        self.assertNotIn("csrf-should-not-leak", joined)
        self.assertNotIn("Authorization", joined)
        self.assertNotIn("Cookie", joined)

    def test_modern_middleware_does_not_log_secrets(self):
        mw = RequestLoggingMiddleware(lambda request: HttpResponse("ok", status=201))
        response = mw(self._sensitive_request())
        self.assertEqual(response.status_code, 201)
        self._assert_safe_logs()
        joined = "\n".join(self.handler.records)
        self.assertIn("201", joined)
        self.assertIn("rid-42", joined)

    def test_simple_middleware_does_not_log_secrets(self):
        mw = simple_middleware(lambda request: HttpResponse("ok", status=200))
        mw(self._sensitive_request())
        self._assert_safe_logs()

    def test_mixin_middleware_does_not_log_secrets(self):
        get_response = MagicMock(return_value=HttpResponse("ok", status=204))
        mw = RequestLoggingMixinMiddleware(get_response)
        request = self._sensitive_request()
        response = get_response(request)
        mw.process_response(request, response)
        self._assert_safe_logs()

    def test_mixin_process_exception_returns_none(self):
        get_response = MagicMock(side_effect=RuntimeError("boom"))
        mw = RequestLoggingMixinMiddleware(get_response)
        request = self.factory.get("/fail/")
        result = mw.process_exception(request, RuntimeError("boom"))
        self.assertIsNone(result)

    def test_mixin_process_exception_does_not_log_secret_messages(self):
        self.handler.setLevel(logging.ERROR)
        logging.getLogger().setLevel(logging.ERROR)
        mw = RequestLoggingMixinMiddleware(MagicMock())
        request = self._sensitive_request()
        secret_exc = ValueError(f"bad password={SECRET_MARKER} auth=Bearer {SECRET_MARKER}")
        result = mw.process_exception(request, secret_exc)
        self.assertIsNone(result)

        joined = "\n".join(self.handler.records)
        self.assertTrue(self.handler.records, "expected at least one log record")
        self.assertIn("ValueError", joined)
        self.assertIn("unhandled_exception", joined)
        self.assertIn("/api/auth/", joined)
        self.assertNotIn(SECRET_MARKER, joined)
        self.assertNotIn("password=", joined)
        self.assertNotIn("Bearer ", joined)
        self.assertNotIn(COOKIE_MARKER, joined)
        self.assertNotIn(BODY_MARKER, joined)
        # Message text and traceback must not appear.
        self.assertNotIn("bad password", joined)
        self.assertNotIn("Traceback", joined)


@override_settings(
    MIDDLEWARE=[
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "logClient.middleware.RequestLoggingMiddleware",
    ]
)
class MiddlewareImportSmokeTests(SimpleTestCase):
    def test_settings_middleware_path_resolves(self):
        from django.conf import settings
        from django.utils.module_loading import import_string

        path = "logClient.middleware.RequestLoggingMiddleware"
        self.assertIn(path, settings.MIDDLEWARE)
        cls = import_string(path)
        self.assertIs(cls, RequestLoggingMiddleware)
