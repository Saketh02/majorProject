from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("add-bus", views.addBusPageAPI.as_view(), name="add-bus"),
    path("bus-details", views.addBusAPI.as_view(), name="bus-details"),
    path("add-stops-page", views.addStopsPageAPI.as_view(), name="add-stops-page"),
    path("add-stops", views.addStopsAPI.as_view(), name="add-stops"),
]
