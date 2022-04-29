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

# Create your views here.


class RegisterAPI(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        sendBackgroundTask(
            sendEmailNotifs,
            "Regarding User Registration",
            "Welcome to BVRIT Transport Management Portal. Your Registration has been successful",
            [request.data["email"]],
        )
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
            if user.isVerified:
                response = render(request, "Admin.html")
            else:
                return HttpResponse("You are yet to be verified by the admin")
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
        sendBackgroundTask(
            sendEmailNotifs,
            "This is a Test",
            "This is to test the functionality of email notifs in Transport Management Website",
            [
                "18211a1253@bvrit.ac.in",
                "18211a1213@bvrit.ac.in",
                "18211a1203@bvrit.ac.in",
            ],
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
            return render(request, "Student.html", dataDict)


class sendOtpPageAPI(APIView):
    @method_decorator(authorizationMiddleware)
    def get(self, request):
        return render(request, "forgot-password.html")


class sendOtpAPI(APIView):
    @method_decorator(authorizationMiddleware)
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
    @method_decorator(authorizationMiddleware)
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
