from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("add-bus", views.addBusPageAPI.as_view(), name="add-bus"),
    path("bus-details", views.addBusAPI.as_view(), name="bus-details"),
    path("transport-reqs", views.getTransportReqsAPI.as_view(), name="Transport-Reqs"),
    path("add-stops-page", views.addStopsPageAPI.as_view(), name="add-stops-page"),
    path("add-stops", views.addStopsAPI.as_view(), name="add-stops"),
    path(
        "submit-trans-reqs",
        views.acceptOrRejectTransportRequestsAPI.as_view(),
        name="submit-trans-reqs",
    ),
]
