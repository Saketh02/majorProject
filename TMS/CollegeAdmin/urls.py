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
    path("busses-info", views.bussesInfoAPI.as_view(), name="busses-info"),
    path("busses-list", views.bussesListAPI.as_view(), name="busses-list"),
    path("students-info", views.studentsInfoAPI.as_view(), name="students-info"),
    path("busses-list2", views.bussesListAPI2.as_view(), name="busses-list2"),
    path("stops-info", views.stopsInfoAPI.as_view(), name="stops-info"),
    path("delete-all",views.deleteAllAllotmentsAPI.as_view(), name="delete-all"),
    path("student-info",views.findStudentPageAPI.as_view(), name="student-info")
]
