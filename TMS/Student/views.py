import imp
import re
from sre_constants import SUCCESS
from django.http import HttpResponse
from django.shortcuts import redirect, render
from rest_framework.views import APIView
from CollegeAdmin.models import busRequest, busStops
from TMS.middleware import authorizationMiddleware
from django.utils.decorators import method_decorator
from django.contrib import messages
import razorpay
from CollegeAdmin.models import busAllotmentData, busStops, payment
from .constants import RAZORPAY_KEY_ID, RAZORPAY_SECRET, WEBHOOK_SECRET

# Create your views here.
class TransportRequestAPI(APIView):
    @method_decorator(authorizationMiddleware)
    def post(self, request):
        userObj = request.user
        data = request.data
        result = busRequest.objects.filter(student=userObj).first()
        if result and result.approvedStatus:
            messages.error(
                request,
                "Your Transport Request was approved earlier please pay the fee if you haven't",
            )
        elif result and not result.approvedStatus:
            messages.error(
                request,
                "You have already submitted a request earlier, please wait for the admin to accept it",
            )
        else:
            if not "stopName" in data:
                return HttpResponse(status=404)
            stopName = data["stopName"]
            if stopName == "":
                return
            stopObj = busStops.objects.filter(name=stopName).first()
            busRequest.objects.create(student=userObj, stop=stopObj)
            messages.success(request, "Your Transport Request has been submitted")
        return redirect("landing-page")


class payFeePageAPI(APIView):
    @method_decorator(authorizationMiddleware)
    def get(self, request):
        studentObj = request.user
        data = {}
        busAllotment = busAllotmentData.objects.filter(student=studentObj)
        if not busAllotment:
            messages.error(
                request,
                "You either have not submitted a transport request or your transport request was not approved",
            )
        else:

            studentAllotment = busAllotment.first()
            feePaid = studentAllotment.paidAmount
            busObj = studentAllotment.bus
            busName = busObj.name
            stopName = studentAllotment.boardingPoint.name
            stopObj = busStops.objects.filter(name=stopName).first()
            totalFee = stopObj.fee
            feeDue = totalFee - feePaid
            data["name"] = studentObj.name
            data["rollNum"] = studentObj.rollnum
            data["stop"] = stopName
            data["bus"] = busName
            data["due"] = feeDue
        return render(request, "fee-payment.html", data)


client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_SECRET))


class paymentPageAPI(APIView):
    @method_decorator(authorizationMiddleware)
    def post(self, request):
        amount = int(request.data["amount"])
        DATA = {
            "amount": amount * 100,
            "currency": "INR",
            "receipt": "receipt#1",
            "notes": {"key1": "value3", "key2": "value2"},
        }
        payment_order = client.order.create(data=DATA)
        payment_order_id = payment_order["id"]
        userObj = request.user

        payment.objects.create(student=userObj, orderId=payment_order_id)
        return render(
            request,
            "make-payment.html",
            {
                "amount": amount,
                "order_id": payment_order_id,
                "razorpay_key_id": RAZORPAY_KEY_ID,
            },
        )


class paymentCaptureAPI(APIView):
    def post(self, request):
        paymentData = request.POST
        if (
            "razorpay_order_id" not in paymentData
            or "razorpay_payment_id" not in paymentData
            or "razorpay_signature" not in paymentData
        ):
            return HttpResponse("You are not authorized to view this content")
        orderId = request.POST["razorpay_order_id"]
        paymentId = request.POST["razorpay_payment_id"]
        signature = request.POST["razorpay_signature"]
        if not orderId or not paymentId or not signature:
            return HttpResponse("Invalid Content")
        paymentObj = payment.objects.filter(orderId=orderId).first()
        paymentObj.paymentId = paymentId
        paymentObj.signature = signature
        paymentObj.save()
        payload = client.payment.fetch(paymentId)
        if "status" not in payload:
            return HttpResponse("Invalid Request")
        if payload["status"] == "captured":
            amount = payload["amount"]/100
            allotmentObj = busAllotmentData.objects.filter(student=paymentObj.student).first()
            allotmentObj.paidAmount += amount
            print(allotmentObj.student)
            busRequestObj = busRequest.objects.filter(student=allotmentObj.student).first()
            stopObj = busRequestObj.stop
            if allotmentObj.paidAmount >= stopObj.fee:
                allotmentObj.paymentStatus = True
                allotmentObj.save()
            return render(request,"sample.html",{"event":True})
        return render(request,"sample.html",{"event":False})
        


class webhookAPI(APIView):
    def post(self, request):
        if "X-Razorpay-Signature" not in request.headers:
            return HttpResponse("Invalid Request")
        signature = request.headers["X-Razorpay-Signature"]
        webhookBody = str(request.body,'utf-8')
        status = client.utility.verify_webhook_signature(webhookBody, signature, WEBHOOK_SECRET)
        if status:
            try:
                payload = request.data["payload"]["payment"]["entity"]
                if payload["status"] == 'captured':
                    orderId = payload["order_id"]
            except KeyError:
                return HttpResponse("Invalid Request")
        return render(request,"sample.html",{"event":True})