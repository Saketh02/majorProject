from django.urls import path
from User.views import logoutAPI
from .views import TransportRequestAPI

urlpatterns = [
    path("logout", logoutAPI.as_view(), name="logout"),
    path("trans-request", TransportRequestAPI.as_view(), name="trans-request"),
]
