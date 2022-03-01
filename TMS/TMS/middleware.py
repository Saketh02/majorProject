from multiprocessing import AuthenticationError
from User.models import Register
from django.http import HttpResponse
import jwt


def authorizationMiddleware(get_response):
    def middleware(request):
        token = request.COOKIES.get("jwt")
        if not token:
            return HttpResponse(
                "You are not authorized to view this content", status=404
            )
        try:
            payload = jwt.decode(token, "secret", algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return HttpResponse("Please Login again", status=404)
        user = Register.objects.get(id=payload["id"])
        request.user = user
        response = get_response(request)
        return response

    return middleware
