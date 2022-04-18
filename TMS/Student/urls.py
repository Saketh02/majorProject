from django.urls import path
from User.views import logoutAPI
from .views import TransportRequestAPI, paymentPageAPI, payFeePageAPI, paymentCaptureAPI, webhookAPI

urlpatterns = [
    path("logout", logoutAPI.as_view(), name="logout"),
    path("trans-request", TransportRequestAPI.as_view(), name="trans-request"),
    path("payment-page", paymentPageAPI.as_view(), name="payment-page"),
    path("pay-fee-page", payFeePageAPI.as_view(), name="pay-fee-page"),
    path("payment-capture", paymentCaptureAPI.as_view(), name="payment-capture"),
    path("webhook-api", webhookAPI.as_view(), name="webhook-api")
]
