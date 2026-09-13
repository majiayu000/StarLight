from base64 import b32encode
from binascii import unhexlify

import qrcode
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.utils.module_loading import import_string
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex
from QrClient.serializers import QrCodeSerializer
from rest_framework import generics, permissions, status
from rest_framework.renderers import BaseRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from two_factor.utils import get_otpauth_url, totp_digits

PENDING_TOTP_SESSION_KEY = "pending_totp_key"
PENDING_TOTP_USER_SESSION_KEY = "pending_totp_user_id"
TOTP_DEVICE_NAME_MAX_LENGTH = 64
# random_hex(20) produces 40 lowercase hex characters (20 bytes).
TOTP_KEY_HEX_LENGTH = 40


class SvgXmlRenderer(BaseRenderer):
    """Advertise image/svg+xml so Accept: image/svg+xml does not 406."""

    media_type = "image/svg+xml"
    format = "svg"
    charset = "utf-8"
    render_style = "binary"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data is None:
            return b""
        if isinstance(data, HttpResponse):
            return data.content
        if isinstance(data, (bytes, bytearray, memoryview)):
            return bytes(data)
        return str(data).encode(self.charset or "utf-8")


def resolve_device_name(request_data):
    """Return a validated device name or an error Response."""
    if "name" not in request_data:
        return "default", None

    name = request_data.get("name")
    if not isinstance(name, str) or not name.strip():
        return None, Response(
            {"detail": "name must be a non-empty string."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if len(name) > TOTP_DEVICE_NAME_MAX_LENGTH:
        return None, Response(
            {
                "detail": (
                    f"name must be at most {TOTP_DEVICE_NAME_MAX_LENGTH} characters."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    return name, None


def is_valid_totp_key(key):
    """Accept only 20-byte hex secrets (same entropy as random_hex(20))."""
    if not isinstance(key, str) or len(key) != TOTP_KEY_HEX_LENGTH:
        return False
    try:
        unhexlify(key.encode("ascii"))
    except (TypeError, ValueError):
        return False
    return True


def ensure_additional_enrollment_allowed(request):
    """
    Password-only auth is fine for first-factor setup.

    Once a confirmed TOTP device exists, require an OTP-verified session or a
    valid token from an existing device before enrolling another factor.
    """
    confirmed = TOTPDevice.objects.filter(user=request.user, confirmed=True)
    if not confirmed.exists():
        return None

    if getattr(request.user, "is_verified", lambda: False)():
        return None

    existing_otp = None
    if hasattr(request, "data"):
        existing_otp = request.data.get("existing_otp")
    if existing_otp is None:
        existing_otp = request.META.get("HTTP_X_OTP")

    if existing_otp is None:
        return Response(
            {
                "detail": (
                    "OTP from an existing device is required to enroll another factor."
                )
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    for device in confirmed:
        if device.verify_token(str(existing_otp)):
            return None

    return Response(
        {"detail": "Invalid OTP for existing device."},
        status=status.HTTP_403_FORBIDDEN,
    )


def bind_pending_totp_key(request, key):
    request.session[PENDING_TOTP_SESSION_KEY] = key
    request.session[PENDING_TOTP_USER_SESSION_KEY] = request.user.pk


def get_pending_totp_key_for_user(request):
    """Return the session pending key only when bound to request.user."""
    key = request.session.get(PENDING_TOTP_SESSION_KEY)
    pending_user_id = request.session.get(PENDING_TOTP_USER_SESSION_KEY)
    if not key:
        return None, None
    if pending_user_id != request.user.pk:
        return None, Response(
            {"detail": "Pending TOTP secret belongs to a different user."},
            status=status.HTTP_403_FORBIDDEN,
        )
    return key, None


def clear_pending_totp(request):
    request.session.pop(PENDING_TOTP_SESSION_KEY, None)
    request.session.pop(PENDING_TOTP_USER_SESSION_KEY, None)


def confirm_totp_device(*, user, key, name, token):
    """
    Create a device and confirm via verify_token so last_t consumes the code.
    Returns (device, error_response).
    """
    digits = totp_digits()
    step = 30
    tolerance = 1

    if not is_valid_totp_key(str(key)):
        return None, Response(
            {
                "detail": (
                    f"key must be a {TOTP_KEY_HEX_LENGTH}-character hex string "
                    f"({TOTP_KEY_HEX_LENGTH // 2} bytes)."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    device = TOTPDevice.objects.create(
        user=user,
        key=key,
        tolerance=tolerance,
        t0=0,
        step=step,
        drift=0,
        digits=digits,
        name=name,
        confirmed=False,
    )
    if not device.verify_token(str(token)):
        device.delete()
        return None, Response(
            {"detail": "Invalid TOTP token"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    device.confirmed = True
    device.save(update_fields=["confirmed"])
    return device, None


class QRSetup(APIView):
    """Authenticated TOTP enrollment: issue a QR code, then confirm with a token."""

    permission_classes = (permissions.IsAuthenticated,)
    # GET only returns SVG; POST uses JSON. Do not advertise JSON on GET.
    renderer_classes = (SvgXmlRenderer, JSONRenderer)
    default_qr_factory = "qrcode.image.svg.SvgPathImage"

    def get_renderers(self):
        if (
            getattr(self, "request", None) is not None
            and self.request.method.upper() == "GET"
        ):
            return [SvgXmlRenderer()]
        return [JSONRenderer()]

    def get(self, request, *args, **kwargs):
        key = random_hex(20)
        bind_pending_totp_key(request, key)

        rawkey = unhexlify(key.encode("ascii"))
        b32key = b32encode(rawkey).decode("utf-8")

        image_factory_string = getattr(
            settings, "TWO_FACTOR_QR_FACTORY", self.default_qr_factory
        )
        image_factory = import_string(image_factory_string)
        content_type = "image/svg+xml; charset=utf-8"

        username = request.user.get_username()
        issuer = get_current_site(request).name

        otpauth_url = get_otpauth_url(
            accountname=username, issuer=issuer, secret=b32key, digits=totp_digits()
        )

        resp = HttpResponse(content_type=content_type)
        img = qrcode.make(otpauth_url, image_factory=image_factory)
        img.save(resp)
        return resp

    def post(self, request, *args, **kwargs):
        gate = ensure_additional_enrollment_allowed(request)
        if gate is not None:
            return gate

        token = request.data.get("token")
        if token is None:
            return Response(
                {"detail": "token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        key, binding_error = get_pending_totp_key_for_user(request)
        if binding_error is not None:
            return binding_error
        if not key:
            return Response(
                {"detail": "No pending TOTP enrollment. Request a QR code first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        device, error = confirm_totp_device(
            user=request.user, key=key, name="default", token=token
        )
        if error is not None:
            return error

        clear_pending_totp(request)
        return Response(
            QrCodeSerializer(device).data,
            status=status.HTTP_201_CREATED,
        )


class QRCreateListView(generics.ListCreateAPIView):
    serializer_class = QrCodeSerializer
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (JSONRenderer,)

    def get_queryset(self):
        return TOTPDevice.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Confirm enrollment only for the authenticated user; never mint JWTs."""
        gate = ensure_additional_enrollment_allowed(request)
        if gate is not None:
            return gate

        if request.data.get("user") and request.data.get("user") != request.user.username:
            return Response(
                {"detail": "Cannot create a TOTP device for another user."},
                status=status.HTTP_403_FORBIDDEN,
            )

        key, binding_error = get_pending_totp_key_for_user(request)
        if binding_error is not None:
            return binding_error
        # Never accept a client-chosen secret: entropy cannot be proven from
        # length/hex syntax alone (e.g. "0"*40). Enrollment must use the
        # server-generated pending session key from a prior QR request.
        if not key:
            return Response(
                {
                    "detail": (
                        "No pending TOTP enrollment. Request a QR code first; "
                        "client-supplied keys are not accepted."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = request.data.get("token")
        if token is None:
            return Response(
                {"detail": "Pending key and token are required to enroll."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        name, name_error = resolve_device_name(request.data)
        if name_error is not None:
            return name_error

        device, error = confirm_totp_device(
            user=request.user, key=key, name=name, token=token
        )
        if error is not None:
            return error

        clear_pending_totp(request)
        return Response(
            QrCodeSerializer(device).data,
            status=status.HTTP_201_CREATED,
        )
