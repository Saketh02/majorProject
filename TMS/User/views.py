from email import message
from django.shortcuts import redirect, render
from rest_framework.views import APIView
from django.contrib import messages
from CollegeAdmin.methods import sendBackgroundTask
from CollegeAdmin.tasks import sendEmailNotifs
import jwt, datetime
from .serializers import RegisterSerializer
from rest_framework.response import Response
from django.http import HttpResponse
from .models import Register, OneTimePassword
from TMS.middleware import authorizationMiddleware
from django.utils.decorators import method_decorator
from CollegeAdmin.models import busStops, busAllotmentData
from .methods import generateOTP
from django.core.mail import send_mail

import re

# Create your views here.


class RegisterAPI(APIView):
    def post(self, request):
        data = request.data
        serializer = RegisterSerializer(data=data)
        departments = {
            "BSH",
            "IT",
            "CSE",
            "BME",
            "CHE",
            "CIVIL",
            "MECH",
            "PHE",
            "MBA",
            "ECE",
            "EEE",
            "AIDS",
            "CSBS",
            "CSEDS",
            "CSEAIML",
        }
        try:
            password = data["password"]
            confirmPassword = data["confPass"]
            department = data["department"]
            mobile = data["mobile"]
            isAdmin = data["isAdmin"]
            print(isAdmin)
            if department not in departments:
                messages.error(
                    request,
                    "Invalid Department, Valid options are {}".format(departments),
                )
                return render(request, "index.html", {"register": True})
            if password != confirmPassword:
                messages.error(request, "Passwords do not match, Please verify")
                return render(request, "index.html", {"register": True})
            if len(mobile) > 10 or not mobile.isdecimal():
                messages.error(request, "Invalid Mobile Number")
                return render(request, "index.html", {"register": True})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            sendBackgroundTask(
                sendEmailNotifs,
                "Regarding User Registration",
                "Welcome to BVRIT Transport Management Portal. Your Registration has been successful",
                [request.data["email"]],
            )
            messages.success(request, "User Registration Successful")
        except:
            messages.error(
                request,
                "Error in creating the user, User with username or email already exists or Invalid Request",
            )
        finally:
            return render(request, "index.html", {"register": True})


class LoginAPI(APIView):
    def post(self, request):
        if "email" not in request.data and "password" not in request.data:
            return HttpResponse("Invalid Request", status=404)
        email = request.data["email"]
        password = request.data["password"]
        user = Register.objects.filter(email=email).first()
        if user is None:
            messages.error(request, "Incorrect Email Id")
            return render(request, "index.html", {"login": True})
        if not user.check_password(password):
            messages.error(request, "Username or Password is incorrect")
            return render(request, "index.html", {"login": True})
        payload = {
            "id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            "iat": datetime.datetime.utcnow(),
        }
        token = jwt.encode(payload, "secret", algorithm="HS256")
        response = Response()

        if user.isAdmin:
            if user.isVerified:
                response = render(request, "Admin.html")
            else:
                messages.error(request, "You are yet to be verified by the admin")
                return render(request, "index.html", {"login": True})
        else:
            stops = busStops.objects.values_list("name", flat=True)
            dataDict = {}
            dataDict["stops"] = stops
            dataDict["user"] = user.__dict__
            allotmentData = busAllotmentData.objects.filter(student=user)
            if allotmentData:
                dataDict["user"][
                    "boardingPoint"
                ] = allotmentData.first().boardingPoint.name
                dataDict["user"]["busName"] = allotmentData.first().bus.name
            response = render(request, "student.html", dataDict)
        response.set_cookie(key="jwt", value=token, httponly=True)
        return response


class testLogin(APIView):
    @method_decorator(authorizationMiddleware)
    def get(self, request):
        sendBackgroundTask(
            sendEmailNotifs,
            "subject",
            "Hi There",
            ["18211a1253@bvrit.ac.in"],
        )
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
                print(dataDict)
            return render(request, "Student.html", dataDict)


class sendOtpPageAPI(APIView):
    def get(self, request):
        return render(request, "forgot-password.html")


class sendOtpAPI(APIView):
    def post(self, request):
        if "email" not in request.data:
            return HttpResponse("Invalid Request", status=404)
        email = request.data["email"]
        querySet = Register.objects.filter(email=email)
        if not querySet:
            return HttpResponse("Invalid Request", status=404)
        userObj = querySet.first()
        otp = generateOTP()
        subject = "OTP for Password Reset"
        message = "The one time password(OTP) for your request is {}.If you haven't initiated this, please ignore this email and do not share otp with anyone".format(
            otp
        )
        sendBackgroundTask(sendEmailNotifs, subject, message, [email])
        OneTimePassword.objects.create(otp=otp, user=userObj)
        return render(request, "forgot-password.html", {"flag": True, "email": email})


class validateOtpAPI(APIView):
    def post(self, request):
        data = request.data
        if "otp" not in data or "pass" not in data or "confPass" not in data:
            return HttpResponse("Invalid Request", status=404)
        otp = data["otp"]
        try:
            otp = int(otp)
        except:
            messages.error(request, "Invalid OTP Format")
            return render(request, "forgot-password.html", {"done": True})
        password = data["pass"]
        confPassword = data["confPass"]
        if password != confPassword:
            messages.error(request, "Passwords do not match")
            return render(request, "forgot-password.html", {"done": True})
        querySet = OneTimePassword.objects.filter(otp=otp)
        if not querySet:
            messages.error(request, "Incorrect OTP")
            return render(request, "forgot-password.html", {"done": True})
        userObj = querySet.first().user
        userObj.set_password(password)
        userObj.save()
        sendBackgroundTask(
            sendEmailNotifs,
            "Regarding Password Change",
            "Your Password has been changed successfully",
            [userObj.email],
        )
        OneTimePassword.objects.filter(user=userObj).delete()
        messages.success(request, "Your Password changed successfully")
        return render(request, "forgot-password.html", {"done": True})
