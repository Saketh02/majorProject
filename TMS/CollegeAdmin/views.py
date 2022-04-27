from django.shortcuts import redirect, render
from rest_framework.views import APIView
from django.http import HttpResponse
from TMS.middleware import authorizationMiddleware
from django.utils.decorators import method_decorator
from django.contrib import messages
from .serializers import addBusDetailsSerializer
from django.db.models import Q
from .models import Bus, busStops, busTimings, busRequest, busAllotmentData
from User.models import Register

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
        # one key is bus name itself
        dataLength = len(data) - 1
        # There are 3 attributes for every stop
        dataLength = dataLength // 3
        if "busName" not in data:
            return HttpResponse("Bus Name Can't be found")
        busName = data["busName"]
        if not busName:
            messages.error(request, "Bus Name Can't be found")
        busObj = Bus.objects.filter(name=busName).first()
        for i in range(1, dataLength + 1):
            j = str(i)
            try:
                fee = int(data["Fee " + j])
                stop = data["Stop " + j]
                time = data["Time " + j]
            except KeyError:
                continue
            stopObj = busStops.objects.filter(name=stop).first()
            if not stopObj:
                stopObj = busStops.objects.create(name=stop, fee=fee)
            stopObj.bus.add(busObj)
            busTimings.objects.create(bus=busObj, time=time, stop=stopObj)
            messages.success(request, "Details were succesfully saved")
        return redirect("add-stops-page")


class getTransportReqsAPI(APIView):
    @method_decorator(authorizationMiddleware)
    def get(self, request):
        data = []
        busRequests = busRequest.objects.filter(approvedStatus=False)
        c = 1
        if not busRequests:
            messages.error(request, "No Transport Request found")
        for requestObj in busRequests:
            studentObj = requestObj.student
            name = studentObj.name
            rollnum = studentObj.rollnum
            year = studentObj.year
            department = studentObj.department
            stopName = requestObj.stop.name
            busses = busStops.objects.filter(name=stopName).first().bus.all()
            dataTuple = (name, rollnum, year, department, stopName, busses)
            data.append(dataTuple)
            c += 1
        d = {}
        d["items"] = data
        return render(request, "transport-reqs.html", d)


class acceptOrRejectTransportRequestsAPI(APIView):
    @method_decorator(authorizationMiddleware)
    def post(self, request):
        data = request.data
        checkBoxes = data.getlist("checkboxh")
        rollNums = data.getlist("rollNumh")
        busNames = data.getlist("busNameh")
        if "btn1" in request.POST:
            if not rollNums or not busNames:
                return HttpResponse("Invalid Request", status=404)
            rows = len(rollNums)
            filledBusses = []
            for i in range(rows):
                if busNames[i] != "":
                    busObj = Bus.objects.filter(name=busNames[i]).first()
                    count = busAllotmentData.objects.filter(bus=busObj).count()
                    if count == busObj.seats:
                        filledBusses.append(busNames[i])
                        continue
                    else:
                        seatNum = count + 1
                    studentObj = Register.objects.filter(rollnum=rollNums[i]).first()
                    busReqObj = busRequest.objects.filter(student=studentObj).first()
                    stopObj = busReqObj.stop
                    busReqObj.approvedStatus = True
                    busReqObj.save()
                    busAllotmentData.objects.create(
                        student=studentObj,
                        bus=busObj,
                        boardingPoint=stopObj,
                        seatNumber=seatNum,
                    )
                else:
                    continue
            if filledBusses:
                messages.success(
                    request,
                    "The busses {} are filled and remaining students have been alloted".format(
                        filledBusses
                    ),
                )
            else:
                messages.success(
                    request, "The choosen Transport Requests have been approved"
                )
            return redirect("Transport-Reqs")
        elif "btn2" in request.POST:
            if not checkBoxes:
                return HttpResponse("Invalid Request", status=404)
            rows = len(checkBoxes)
            for i in range(rows):
                if checkBoxes[i] == "True":
                    rollNum = int(rollNums[i])
                    userObj = Register.objects.filter(rollnum=rollNum).first()
                    transReqObj = busRequest.objects.filter(student=userObj)
                    transReqObj.delete()
            messages.success(request, "Selected Students have been removed")
            return redirect("Transport-Reqs")
        else:
            return HttpResponse("Invalid Request")


class bussesInfoAPI(APIView):
    @method_decorator(authorizationMiddleware)
    def get(self, request):
        querySet = Bus.objects.all()
        return render(request, "busses-info.html", {"items": querySet})


class bussesListAPI(APIView):
    @method_decorator(authorizationMiddleware)
    def get(self, request):
        busses = Bus.objects.values_list("name", flat=True)
        bussesDict = {}
        bussesDict["busses"] = busses
        return render(request, "students-info.html", bussesDict)


class studentsInfoAPI(APIView):
    @method_decorator(authorizationMiddleware)
    def post(self, request):
        busNames = Bus.objects.values_list("name", flat=True)
        if "busName" not in request.data:
            return HttpResponse("Invalid Request", status=404)
        busName = request.data["busName"]
        busses = Bus.objects.filter(name=busName)
        if not busses:
            return HttpResponse("Invalid Request", status=404)
        busObj = busses.first()
        querySet = busAllotmentData.objects.filter(bus=busObj)
        data = []
        if querySet:
            for i in querySet:
                name = i.student.name
                rollNum = i.student.rollnum
                year = i.student.year
                dept = i.student.department
                boardingPoint = i.boardingPoint.name
                feePaid = i.paidAmount
                due = busStops.objects.filter(name=boardingPoint).first().fee - feePaid
                student = [
                    name,
                    rollNum,
                    year,
                    dept,
                    boardingPoint,
                    busName,
                    feePaid,
                    due,
                ]
                data.append(student)
        if not data:
            messages.error(request, "No Students are alloted to the selected bus")
        return render(
            request,
            "students-info.html",
            {"items": data, "busses": busNames, "currBus": busObj.name},
        )


class bussesListAPI2(APIView):
    @method_decorator(authorizationMiddleware)
    def get(self, request):
        busses = Bus.objects.values_list("name", flat=True)
        bussesDict = {}
        bussesDict["busses"] = busses
        return render(request, "stops-info.html", bussesDict)


class stopsInfoAPI(APIView):
    @method_decorator(authorizationMiddleware)
    def post(self, request):
        busNames = Bus.objects.values_list("name", flat=True)
        if "busName" not in request.data:
            return HttpResponse("Invalid Request", status=404)
        busName = request.data["busName"]
        busses = Bus.objects.filter(name=busName)
        if not busses:
            return HttpResponse("Invalid Request", status=404)
        busObj = busses.first()
        querySet = busTimings.objects.filter(bus=busObj).order_by("time")
        data = []
        if querySet:
            for i in querySet:
                stopName = i.stop.name
                time = i.time
                student = [stopName, time]
                data.append(student)
        if not data:
            messages.error(request, "Stops are not yet added to the selected bus")
        return render(
            request,
            "stops-info.html",
            {"items": data, "busses": busNames, "currBus": busObj.name},
        )


class deleteAllAllotmentsAPI(APIView):
    @method_decorator(authorizationMiddleware)
    def get(self, request):
        busRequest.objects.all().delete()
        busAllotmentData.objects.all().delete()
        messages.success(request, "All Allotments are Deleted")
        return redirect("landing-page")


class findStudentPageAPI(APIView):
    @method_decorator(authorizationMiddleware)
    def get(self, request):
        return render(request, "single-student-info.html")
