from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.RegisterView.as_view()),
    path("login/", views.LoginView.as_view()),
]
