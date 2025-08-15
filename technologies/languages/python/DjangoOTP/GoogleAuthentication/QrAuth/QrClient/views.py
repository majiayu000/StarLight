import time
from base64 import b32encode
from binascii import unhexlify
from typing import Any

import qrcode
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.utils.module_loading import import_string
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex
from QrClient.serializers import QrCodeSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from two_factor.utils import get_otpauth_url, totp_digits


class QRSetup(View):
    permission_classes = (permissions.AllowAny,)
    default_qr_factory = "qrcode.image.svg.SvgPathImage"

    def get(self, request, *args, **kwargs):
        start_time = time.time()
        key = random_hex(20)
        # start_time = time.time()
        print(f"key is: {key}")
        rawkey = unhexlify(key.encode("ascii"))
        b32key = b32encode(rawkey).decode("utf-8")

        # Get data for qrcode
        image_factory_string = getattr(
            settings, "TWO_FACTOR_QR_FACTORY", self.default_qr_factory
        )
        image_factory = import_string(image_factory_string)
        content_type = "image/svg+xml; charset=utf-8"

        # Todo: what will happend if many people get this at same time
        try:
            print(f"cache is {cache.get('cached_username')}")
        except Exception as e:
            print(e)
        try:
            username = cache.get("cached_username")
        except Exception as e:
            username = "lif"
        if username is None:
            username = "No username"
        # username = "list"
        issuer = get_current_site(self.request).name

        otpauth_url = get_otpauth_url(
            accountname=username, issuer=issuer, secret=b32key, digits=totp_digits()
        )

        # Make QR code

        resp = HttpResponse(content_type=content_type)

        img = qrcode.make(otpauth_url, image_factory=image_factory)

        img.save(resp)
        return resp

        # If you want to post key with qrcode, the use method below
        # print(img)
        from io import BytesIO

        byte_stream = BytesIO()

        img.save(byte_stream)

        import base64

        byte_content = byte_stream.getvalue()
        base64_content = base64.b64encode(byte_content).decode("utf-8")
        resp_data = {"key": key, "qr_image": base64_content}
        resp = JsonResponse(resp_data)
        end_time = time.time()
        time_since = end_time - start_time
        print(time_since)
        return resp

    @csrf_exempt
    def post(self, request):
        self.key = request.data.get("key")
        self.user = request.data.get("user")
        try:
            TOTPDevice.objects.create(
                user=self.user,
                key=self.key,
                tolerance=self.tolerance,
                t0=self.t0,
                step=self.step,
                drift=self.drift,
                digits=self.digits,
                name="default",
            )
            return HttpResponse("Success")
        except Exception as e:
            print(f"{e}")
            return HttpResponse("fail")


class QRCreateListView(generics.ListCreateAPIView):
    queryset = TOTPDevice.objects.all()
    serializer_class = QrCodeSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request) -> HttpResponse:
        try:
            request_body: dict[str, Any] = request.data
        except Exception as e:
            print(e)
            return HttpResponse("fail")

        key: int = request_body.get("key", 0)
        user: User = User.objects.filter(username=request_body.get("user")).first()
        if not user:
            return HttpResponse("User not found", status=status.HTTP_404_NOT_FOUND)


        try:
            TOTPDevice.objects.create(
                user=user,
                key=key,
                tolerance=1,
                t0=0,
                step=30,
                drift=0,
                digits=totp_digits(),
                name="default",
            )

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "api_token": str(refresh.access_token),
                    "refreshToken": str(refresh),
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print(str(e))
            return HttpResponse("fail", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
