from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@extend_schema(exclude=True)
@api_view(["POST"])
def service_token(request):
    """
    Internal use only: get service token for aladin
    """
    user = authenticate(
        username=settings.SERVICE_USERNAME,
        password=settings.SERVICE_PASSWORD,
    )

    if user is None:
        return Response(
            {"detail": "Authentication failed"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    refresh = RefreshToken.for_user(user)

    return Response({
        "access": str(refresh.access_token),
    })