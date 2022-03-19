import imp
from django.http import HttpResponse
from django.shortcuts import redirect
from rest_framework.views import APIView
from CollegeAdmin.models import busRequest, busStops
from TMS.middleware import authorizationMiddleware
from django.utils.decorators import method_decorator
from django.contrib import messages

# Create your views here.
class TransportRequestAPI(APIView):
    @method_decorator(authorizationMiddleware)
    def post(self, request):
        userObj = request.user
        data = request.data
        result = busRequest.objects.filter(student=userObj).first()
        if result:
            messages.error(
                request,
                "There is an existing Transport request, Please wait for the approval",
            )
        else:
            if not "stopName" in data:
                return HttpResponse(status=404)
            stopName = data["stopName"]
            if stopName == "":
                return
            stopObj = busStops.objects.filter(name=stopName).first()
            print(stopObj)
            busRequest.objects.create(student=userObj, stop=stopObj)
            messages.success(request, "Your Transport Request has been submitted")
        return redirect("landing-page")
