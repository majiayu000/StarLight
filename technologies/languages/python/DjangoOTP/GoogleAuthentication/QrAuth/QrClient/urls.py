from QrClient.views import QRSetup, QRCreateListView
from django.urls import path

urlpatterns = [
    path(
        "api/v1/qrcode/list/", QRSetup.as_view(), name="getQr"
    ),
    
    path(
        "api/v1/qrcode/save", QRCreateListView.as_view(), name="saveQr"
    )

]