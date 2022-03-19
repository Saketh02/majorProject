from django.shortcuts import redirect, render
from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseRedirect
from TMS.middleware import authorizationMiddleware
from django.utils.decorators import method_decorator
from django.contrib import messages
from .serializers import addBusDetailsSerializer
from django.db.models import Q
from .models import Bus, busStops, busTimings

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
        """data = request.data
        # one key is bus name itself
        dataLength = len(data) - 1
        # There are 3 attributes for every stop
        dataLength = dataLength // 3
        if "busName" not in data:
            return HttpResponse("Bus Name Can't be found")
        busName = data["busName"]
        if not busName:
            messages.error(request,"Bus Name Can't be found")
        busObj = Bus.objects.filter(name=busName).first()
        for i in range(1, dataLength + 1):
            j = str(i)
            try:
                fee = int(data["Fee " + j])
                stop = data["Stop " + j]
                time = data["Time " + j]
            except KeyError:
                continue
            stopObj = busStops.objects.create(name=stop, fee=fee)
            stopObj.bus.add(busObj)
            busTimings.objects.create(bus=busObj, time=time, stop=stopObj)"""
        messages.success(request, "Details were succesfully saved")
        return redirect("add-stops-page")