from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("add-bus", views.addBus.as_view(), name="add-bus"),
]
