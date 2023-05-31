from django.http import JsonResponse
from rest_framework.authtoken.models import Token

class TokenAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'HTTP_AUTHORIZATION' in request.META:
            auth_header = request.META['HTTP_AUTHORIZATION']
            auth_token = auth_header.split(' ')[1]
            try:
                Token.objects.get(key=auth_token)
            except Token.DoesNotExist:
                return JsonResponse({'resultCode': 500}, status=401)

        response = self.get_response(request)
        return response
