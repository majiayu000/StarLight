from base64 import b32encode
from binascii import unhexlify

import qrcode
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.utils.module_loading import import_string
from django_otp.oath import totp
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex
from QrClient.serializers import QrCodeSerializer
from rest_framework import generics, permissions, status
from rest_framework.renderers import BaseRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from two_factor.utils import get_otpauth_url, totp_digits

PENDING_TOTP_SESSION_KEY = "pending_totp_key"
TOTP_DEVICE_NAME_MAX_LENGTH = 64


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


class QRSetup(APIView):
    """Authenticated TOTP enrollment: issue a QR code, then confirm with a token."""

    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (SvgXmlRenderer, JSONRenderer)
    default_qr_factory = "qrcode.image.svg.SvgPathImage"

    def get_renderers(self):
        # GET advertises SVG for Accept: image/svg+xml; POST must stay JSON.
        if getattr(self, "request", None) is not None and self.request.method.upper() != "GET":
            return [JSONRenderer()]
        return [renderer() for renderer in self.renderer_classes]

    def get(self, request, *args, **kwargs):
        key = random_hex(20)
        request.session[PENDING_TOTP_SESSION_KEY] = key

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
        token = request.data.get("token")
        if token is None:
            return Response(
                {"detail": "token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        key = request.session.get(PENDING_TOTP_SESSION_KEY)
        if not key:
            return Response(
                {"detail": "No pending TOTP enrollment. Request a QR code first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token_int = int(token)
        except (TypeError, ValueError):
            return Response(
                {"detail": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        digits = totp_digits()
        step = 30
        tolerance = 1
        try:
            key_bytes = unhexlify(key.encode("ascii"))
        except (TypeError, ValueError):
            request.session.pop(PENDING_TOTP_SESSION_KEY, None)
            return Response(
                {"detail": "Invalid pending key"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        matched = False
        for offset in range(-tolerance, tolerance + 1):
            if totp(key_bytes, step=step, digits=digits, drift=offset) == token_int:
                matched = True
                break

        if not matched:
            return Response(
                {"detail": "Invalid TOTP token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        device = TOTPDevice.objects.create(
            user=request.user,
            key=key,
            tolerance=tolerance,
            t0=0,
            step=step,
            drift=0,
            digits=digits,
            name="default",
            confirmed=True,
        )
        request.session.pop(PENDING_TOTP_SESSION_KEY, None)

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
        if request.data.get("user") and request.data.get("user") != request.user.username:
            return Response(
                {"detail": "Cannot create a TOTP device for another user."},
                status=status.HTTP_403_FORBIDDEN,
            )

        key = request.session.get(PENDING_TOTP_SESSION_KEY) or request.data.get("key")
        token = request.data.get("token")
        if not key or token is None:
            return Response(
                {"detail": "Pending key and token are required to enroll."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        name, name_error = resolve_device_name(request.data)
        if name_error is not None:
            return name_error

        try:
            token_int = int(token)
        except (TypeError, ValueError):
            return Response(
                {"detail": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        digits = totp_digits()
        step = 30
        tolerance = 1
        try:
            key_bytes = unhexlify(str(key).encode("ascii"))
        except (TypeError, ValueError):
            return Response(
                {"detail": "Invalid key"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        matched = False
        for offset in range(-tolerance, tolerance + 1):
            if totp(key_bytes, step=step, digits=digits, drift=offset) == token_int:
                matched = True
                break

        if not matched:
            return Response(
                {"detail": "Invalid TOTP token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        device = TOTPDevice.objects.create(
            user=request.user,
            key=key,
            tolerance=tolerance,
            t0=0,
            step=step,
            drift=0,
            digits=digits,
            name=name,
            confirmed=True,
        )
        request.session.pop(PENDING_TOTP_SESSION_KEY, None)

        return Response(
            QrCodeSerializer(device).data,
            status=status.HTTP_201_CREATED,
        )
