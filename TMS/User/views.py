from msilib.schema import ReserveCost
from django.shortcuts import redirect, render
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.serializers import Serializer
from rest_framework.views import APIView

import jwt, datetime
from .serializers import RegisterSerializer
from rest_framework.response import Response
from django.http import HttpResponse
from .models import Register
from TMS.middleware import authorizationMiddleware
from django.utils.decorators import method_decorator

# Create your views here.


class RegisterAPI(APIView):
    def post(self, request):
        print(request.data)
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return HttpResponse("User Registration Successful")


class LoginAPI(APIView):
    def post(self, request):
        email = request.data["email"]
        password = request.data["password"]

        user = Register.objects.filter(email=email).first()
        if user is None:
            return HttpResponse("Invalid Credentials")
        if not user.check_password(password):
            raise HttpResponse("Email ID or Password is Incorrect")
        payload = {
            "id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            "iat": datetime.datetime.utcnow(),
        }
        token = jwt.encode(payload, "secret", algorithm="HS256")
        print(token)
        response = Response()

        if user.isAdmin:
            response = render(request, "Admin.html")
        else:
            response = render(request, "student.html")
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
        response = Response()
        response.delete_cookie("jwt")
        return redirect("/")


class landingPageAPI(APIView):
    @method_decorator(authorizationMiddleware)
    def get(self, request):
        userObj = request.user
        if userObj.isAdmin:
            return render(request, "Admin.html")
        else:
            return render(request, "Student.html")