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
from rest_framework.response import Response
from rest_framework.views import APIView
from two_factor.utils import get_otpauth_url, totp_digits

PENDING_TOTP_SESSION_KEY = "pending_totp_key"


class QRSetup(APIView):
    """Authenticated TOTP enrollment: issue a QR code, then confirm with a token."""

    permission_classes = (permissions.IsAuthenticated,)
    default_qr_factory = "qrcode.image.svg.SvgPathImage"

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
            name=request.data.get("name", "default"),
            confirmed=True,
        )
        request.session.pop(PENDING_TOTP_SESSION_KEY, None)

        return Response(
            QrCodeSerializer(device).data,
            status=status.HTTP_201_CREATED,
        )
