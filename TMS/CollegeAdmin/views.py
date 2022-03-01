from django.shortcuts import render
from rest_framework.views import APIView
from TMS.middleware import authorizationMiddleware
from django.utils.decorators import method_decorator

# Create your views here.


class addBus(APIView):
    @method_decorator(authorizationMiddleware)
    def get(self, request):
        print("saketh chandra")
        return render(request, "bus.html")




