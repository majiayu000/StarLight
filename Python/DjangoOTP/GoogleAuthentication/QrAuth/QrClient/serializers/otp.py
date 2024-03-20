from rest_framework import serializers
from django_otp.plugins.otp_totp.models import TOTPDevice



class QrCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TOTPDevice
        fields = "__all__"