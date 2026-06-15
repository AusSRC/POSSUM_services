from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from ..services.pipeline_3d import (
    get_tiles_for_ingest,
    get_tiles_for_pipeline_run,
    get_tiles_with_filter,
    get_tiles_for_completed_processing,
    get_tiles_order_by_3d_pipeline_val,
    get_tiles_where_no_validation_link,
    get_tiles_that_had_processing_started,
    get_all_tiles,
    reset_3d_pipeline_val_and_link,
    reset_3d_pipeline_val_running,
    reset_3d_pipeline_val_waiting,
    update_3d_pipeline_table,
)

@extend_schema(summary="check main tile database",
               description="SELECT * FROM possum.tile")
@api_view(["GET"])
def check_main_tile_database(request):
    try:
        tiles = get_all_tiles()
        return Response({
            "success": True,
            "tiles": tiles,
        })
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )


@extend_schema(summary="Find tiles that had processing at least started",
    parameters=[
            OpenApiParameter(
            name="band_number",
            type=int,
            location=OpenApiParameter.QUERY,
            required=True,
            description="Band number (1 or 2)",
        ),
        OpenApiParameter(
            name="tile_number",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,  # <-- optional
            description="Tile number e.g. 10670. If omitted, all tiles are checked.",
        ),
    ]
)
@api_view(["GET"])
def find_tiles_that_had_processing_started(request):
    try:
        band_number = request.query_params.get("band_number")
        tile_id = request.query_params.get("tile_id")
        tiles = get_tiles_that_had_processing_started(band_number, tile_id)
        return Response({
            "success": True,
            "tiles": tiles,
        })
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )

@extend_schema(summary="check whole tile3d pipeline status database",
               description="""
                    SELECT tile_3d.*
                    FROM possum.tile_state_band1 AS tile_3d
                    ORDER BY "3d_pipeline_val" ASC
                """)
@api_view(["GET"])
def tiles_order_by_3d_pipeline_val(request, band_number):
    try:
        tiles = get_tiles_order_by_3d_pipeline_val(band_number)
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
    

@extend_schema(summary="Select tiles where ingest running",
               description="""
                    SELECT tile_3d.*
                    FROM possum.tile_state_band1 AS tile_3d
                    WHERE "3d_pipeline_ingest" = 'IngestRunning'
                    -- ORDER BY "3d_pipeline_ingest"
                """)
@api_view(["GET"])
def tiles_for_ingest_running(request, band_number, ordered=True):
    try:
        tiles = get_tiles_with_filter(band_number, column_name='3d_pipeline_ingest', column_value='IngestRunning', order_by_3d_pipeline_ingest=ordered)
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

@extend_schema(summary="check tile3d for running jobs",
               description="""
                    SELECT tile_3d.*
                    FROM possum.tile_state_band1 AS tile_3d
                    WHERE "3d_pipeline_val" = 'Running'
                """)
@api_view(["GET"])
def tiles_for_running_jobs(request, band_number):
    try:
        tiles = get_tiles_with_filter(band_number, column_name='3d_pipeline_val', column_value='running')
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

@extend_schema(summary="check tile3d for a specific tilenumber",
               description="""
                    SELECT tile_3d.*
                    FROM possum.tile_state_band1 AS tile_3d
                    WHERE tile = '5423'
                """)
@api_view(["GET"])
def tiles_for_tile_id(request, band_number, tile_id):
    try:
        tiles = get_tiles_with_filter(band_number, column_name='tile', column_value=tile_id, order_by_3d_pipeline_ingest=False)
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

@extend_schema(summary="check tile3d for completed processing",
               description="""
                   SELECT tile_3d.*
                   FROM possum.tile_state_band1 AS tile_3d
                   WHERE "3d_pipeline_val" = 'WaitingForValidation' OR "3d_pipeline_val" = 'Good'
                """)
@api_view(["GET"])
def tiles_for_completed_processing(request, band_number):
    try:
        tiles = get_tiles_for_completed_processing(band_number)
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

@extend_schema(summary="Select tiles where validation link doesnt exist",
               description="""
                    SELECT tile_3d.*
                    FROM possum.tile_state_band1 AS tile_3d
                    WHERE "3d_pipeline" IS NOT NULL and "3d_pipeline_val" IS NULL
                    ORDER BY "3d_pipeline" ASC
                """)
@api_view(["GET"])
def tiles_where_validation_link_doesnt_exist(request, band_number):
    try:
        tiles = get_tiles_where_no_validation_link(band_number)
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

@extend_schema(summary="Select tiles where ingest failed",
               description="""
                    SELECT tile_3d.*
                    FROM possum.tile_state_band1 AS tile_3d
                    WHERE "3d_pipeline_ingest" = 'IngestFailed'
                    -- ORDER BY "3d_pipeline_ingest"
                """)
@api_view(["GET"])
def tiles_where_ingest_failed(request, band_number, order_by_3d_pipeline_ingest=True):
    try:
        tiles = get_tiles_with_filter(band_number, order_by_3d_pipeline_ingest)
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

    @extend_schema(summary="Find tiles to do with 3D pipeline, CUBE and MFS needs to be done")
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

@extend_schema(
    parameters=[
        OpenApiParameter(name="band_number", type=int, location=OpenApiParameter.QUERY, required=True,
                         description="Band number (1 or 2)"),
        OpenApiParameter(name="tile_number", type=int, location=OpenApiParameter.QUERY, required=True),
        OpenApiParameter(name="3d_pipeline", type=str, location=OpenApiParameter.QUERY, required=False,
                         description="A timestamp e.g. 2025-11-25 19:43:29.286359. If omitted, status will be set to NULL")
    ]
)
@api_view(["PATCH"])
def update_3d_pipeline(request):
    try:
        band_number = request.query_params.get("band_number")
        tile_number = request.query_params.get("tile_number")
        status = request.query_params.get("3d_pipeline")
        rows = update_3d_pipeline_table(
            tile_number=tile_number,
            band_number=band_number,
            status=status,
            column_name="3d_pipeline"
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
    
@extend_schema(
    parameters=[
        OpenApiParameter(name="band_number", type=int, location=OpenApiParameter.QUERY, required=True,
                         description="Band number (1 or 2)"),
        OpenApiParameter(name="tile_number", type=int, location=OpenApiParameter.QUERY, required=True),
        OpenApiParameter(name="3d_val_link", type=str, location=OpenApiParameter.QUERY, required=False,
                         description="Optional. If omitted, value will be set to NULL.")
    ]
)
@api_view(["PATCH"])
def update_3d_val_link(request):
    try:
        band_number = request.query_params.get("band_number")
        tile_number = request.query_params.get("tile_number")
        status = request.query_params.get("3d_val_link")
        rows = update_3d_pipeline_table(
            tile_number=tile_number,
            band_number=band_number,
            status=status,
            column_name="3d_val_link"
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

@extend_schema(
    parameters=[
        OpenApiParameter(name="band_number", type=int, location=OpenApiParameter.QUERY, required=True,
                         description="Band number (1 or 2)"),
        OpenApiParameter(name="tile_number", type=int, location=OpenApiParameter.QUERY, required=True),
        OpenApiParameter(name="3d_pipeline_ingest", type=str, location=OpenApiParameter.QUERY, required=False,
                         description="Possible values: 'Ingested', 'IngestFailed', 'IngestRunning'."
                            " If omitted, value will be set to NULL.")
    ]                    
)
@api_view(["PATCH"])
def update_3d_pipeline_ingest(request):
    try:
        band_number = request.query_params.get("band_number")
        tile_number = request.query_params.get("tile_number")
        status = request.query_params.get("3d_pipeline_ingest")
        rows = update_3d_pipeline_table(
            tile_number=tile_number,
            band_number=band_number,
            status=status,
            column_name="3d_pipeline_ingest"
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

@extend_schema(
    parameters=[
        OpenApiParameter(name="band_number", type=int, location=OpenApiParameter.QUERY, required=True,
                         description="Band number (1 or 2)"),
        OpenApiParameter(name="tile_number", type=int, location=OpenApiParameter.QUERY, required=True),
        OpenApiParameter(name="3d_pipeline_val", type=str, location=OpenApiParameter.QUERY, required=False,
                         description="Possible values: 'Running', 'Failed', 'WaitingForValidation', 'Good', 'Bad'."
                         " If omitted, value will be set to NULL")
    ]
)
@api_view(["PATCH"])
def update_3d_pipeline_val(request):
    try:
        band_number = request.query_params.get("band_number")
        tile_number = request.query_params.get("tile_number")
        status = request.query_params.get("3d_pipeline_val")
        rows = update_3d_pipeline_table(
            tile_number=tile_number,
            band_number=band_number,
            status=status,
            column_name="3d_pipeline_val"
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

@extend_schema(summary="Update 3d_pipeline to null where 3d_pipeline_val = 'WaitingForValidation'",
               description="""\n-- UPDATE possum.tile_state_band1
                              \n-- SET "3d_pipeline" = NULL
                              \n-- WHERE "3d_pipeline_val" = 'WaitingForValidation'""")
@api_view(["POST"])
def reset_3d_pipeline_val_waitingforvalidation(request, band_number):
    try:
        rows = reset_3d_pipeline_val_waiting(band_number)
        return Response({
            "success": True,
            "rows_updated": rows,
        })
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )   


@extend_schema(summary="Update 3d_pipeline_val to null where it's supposedly running",
              description="""\n-- UPDATE possum.tile_state_band1
                             \n-- SET "3d_pipeline_val" = NULL
                             \n-- WHERE "3d_pipeline_val" = 'Running'""")
@api_view(["POST"])
def reset_3d_pipeline_val_running(request, band_number):
    try:
        rows = reset_3d_pipeline_val_running(band_number)
        return Response({
            "success": True,
            "rows_updated": rows,
        })
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )  


@extend_schema(summary="Update 3d_pipeline_val and 3d_val_link to null WHERE 3d_pipeline is Null",
              description="""\n-- UPDATE possum.tile_state_band1
                             \n-- SET "3d_pipeline_val" = Null, "3d_val_link" = Null
                             \n-- WHERE "3d_pipeline" is NULL;""")
@api_view(["POST"])
def reset_3d_pipeline_val_and_link(request, band_number):
    try:
        rows = reset_3d_pipeline_val_and_link(band_number)
        return Response({
            "success": True,
            "rows_updated": rows,
        })
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )  
