from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from ..services.pipeline_common import (
    get_observations,
    get_all_tiles,
    get_tiles_and_observations
)

@extend_schema(summary="check main tile database (for all bands)")
@api_view(["GET"])
def tiles(request):
    try:
        rows = get_all_tiles()
        return Response(rows, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )

@extend_schema(summary="Get all tiles and associated observations")
@api_view(["GET"])
def tiles_observations(request, band_number: int):
    try:
        rows = get_tiles_and_observations(band_number)
        return Response(rows, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@extend_schema(summary="Get all observations")
@api_view(["GET"])
def observations(request, band_number: int):
    try:
        rows = get_observations(band_number)
        return Response(rows, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )