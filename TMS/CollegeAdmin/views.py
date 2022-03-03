from django.shortcuts import redirect, render
from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseRedirect
from TMS.middleware import authorizationMiddleware
from django.utils.decorators import method_decorator
from django.contrib import messages
from .serializers import addBusDetailsSerializer
from django.db.models import Q
from .models import Bus

# Create your views here.


class addBusPageAPI(APIView):
    @method_decorator(authorizationMiddleware)
    def get(self, request):
        print("saketh chandra")
        return render(request, "bus.html")


class addBusAPI(APIView):
    @method_decorator(authorizationMiddleware)
    def post(self, request):
        data = request.data
        busName = data["name"]
        busNumber = data["number"]
        driverNumber = data["driverMobile"]
        inchargeNumber = data["inchargeContact"]
        results = Bus.objects.filter(
            Q(name=busName)
            | Q(number=busNumber)
            | Q(driverMobile=driverNumber)
            | Q(inchargeContact=inchargeNumber)
        )
        if results:
            messages.error(
                request,
                "Bus cannot be added because one or more fields already exists in the database",
            )
        else:
            serializer = addBusDetailsSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            messages.success(request, "Bus Added Successfully")
        return redirect("add-bus")


class addStopsPageAPI(APIView):
    @method_decorator(authorizationMiddleware)
    def get(self, request):
        busses = Bus.objects.values_list("name", flat=True)
        bussesDict = {}
        bussesDict["busses"] = busses
        return render(request, "stops.html", bussesDict)


class addStopsAPI(APIView):
    @method_decorator(authorizationMiddleware)
    def post(self, request):
        data = request.data
        print(data)
        return HttpResponse("Done")