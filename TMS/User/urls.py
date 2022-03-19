from django.urls import path
from . import views

urlpatterns = [
    path("register", views.RegisterAPI.as_view(), name="register"),
    path("login", views.LoginAPI.as_view(), name="login"),
    path("test", views.testLogin.as_view(), name="test"),
    path("landing-page", views.landingPageAPI.as_view(), name="landing-page"),
    
]
