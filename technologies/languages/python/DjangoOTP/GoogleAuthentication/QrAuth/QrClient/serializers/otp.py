from rest_framework import serializers
from django_otp.plugins.otp_totp.models import TOTPDevice


class QrCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TOTPDevice
        # Never expose the raw TOTP hex key in API responses.
        exclude = ("key",)
        read_only_fields = ("user", "confirmed")
