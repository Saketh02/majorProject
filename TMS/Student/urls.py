from django.urls import path
from User import views

urlpatterns = [
    path("logout", views.logoutAPI.as_view(), name="logout"),
]
