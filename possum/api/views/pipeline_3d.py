from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from ..services import (
    get_tiles_for_ingest,
    get_tiles_for_pipeline_run,
    update_3d_pipeline_table,
)

class TilesReadyForIngestAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, band_number):

        try:
            tiles = get_tiles_for_ingest(band_number)

            return Response({
                "success": True,
                "band": band_number,
                "tiles": tiles,
            })

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
class TilesReadyFor3DPipelineAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, band_number):

        try:
            tiles = get_tiles_for_pipeline_run(
                band_number
            )

            return Response({
                "success": True,
                "band": band_number,
                "tiles": tiles,
            })

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class Update3DPipelineAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, band_number, column_name, tile_number, status):

        try:
            rows = update_3d_pipeline_table(
                tile_number=tile_number,
                band_number=band_number,
                status=status,
                column_name=column_name,
            )

            return Response({
                "success": True,
                "rows_updated": rows,
            })

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )