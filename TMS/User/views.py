import imp
from math import exp
from msilib.schema import ReserveCost
import django
from django.shortcuts import redirect, render
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from django.contrib.auth import logout

import jwt, datetime


from .serializers import RegisterSerializer

from rest_framework.response import Response
from django.http import HttpResponse
from .models import Register
from TMS.middleware import authorizationMiddleware
from django.utils.decorators import method_decorator
from CollegeAdmin.models import busStops, busAllotmentData

# Create your views here.


class RegisterAPI(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return HttpResponse("User Registration Successful")


class LoginAPI(APIView):
    def post(self, request):
        if "email" not in request.data and "password" not in request.data:
            return HttpResponse("Invalid Request", status=404)
        email = request.data["email"]
        password = request.data["password"]
        user = Register.objects.filter(email=email).first()
        if user is None:
            return HttpResponse("Invalid Credentials")
        if not user.check_password(password):
            return HttpResponse("Email ID or Password is Incorrect")
        payload = {
            "id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            "iat": datetime.datetime.utcnow(),
        }
        token = jwt.encode(payload, "secret", algorithm="HS256")
        response = Response()

        if user.isAdmin:
            response = render(request, "Admin.html")
        else:
            stops = busStops.objects.values_list("name", flat=True)
            dataDict = {}
            dataDict["stops"] = stops
            dataDict["user"] = user.__dict__
            response = render(request, "student.html", dataDict)
        response.set_cookie(key="jwt", value=token, httponly=True)
        return response


class testLogin(APIView):
    @method_decorator(authorizationMiddleware)
    def get(self, request):
        user = request.user

        return HttpResponse("Welcome")


class logoutAPI(APIView):
    @method_decorator(authorizationMiddleware)
    def get(self, request):
        response = redirect("/")
        response.delete_cookie("jwt")
        return response


class landingPageAPI(APIView):
    @method_decorator(authorizationMiddleware)
    def get(self, request):
        userObj = request.user
        if userObj.isAdmin:
            return render(request, "Admin.html")
        else:
            stops = busStops.objects.values_list("name", flat=True)
            dataDict = {}
            dataDict["stops"] = stops
            dataDict["user"] = userObj.__dict__
            allotmentData = busAllotmentData.objects.filter(student=userObj)
            if allotmentData:
                dataDict["user"][
                    "boardingPoint"
                ] = allotmentData.first().boardingPoint.name
                dataDict["user"]["busName"] = allotmentData.first().bus.name
            return render(request, "Student.html", dataDict)
